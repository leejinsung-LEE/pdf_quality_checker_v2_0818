"""Task handling functions for different task types"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from ..queue_manager import Task, TaskType
from ..processor import PDFProcessor
from ..pipeline import ProcessingStatus
from ...core.analyzers import PDFAnalyzer
from ...core.quality_checker import PDFQualityChecker


class TaskHandlers:
    """Handles different types of processing tasks"""
    
    def __init__(self,
                 processor: Optional[PDFProcessor] = None,
                 analyzer: Optional[PDFAnalyzer] = None,
                 checker: Optional[PDFQualityChecker] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize task handlers
        
        Args:
            processor: PDF processor instance
            analyzer: PDF analyzer instance
            checker: Quality checker instance
            logger: Logger instance
        """
        self.processor = processor or PDFProcessor()
        self.analyzer = analyzer or PDFAnalyzer()
        self.checker = checker or PDFQualityChecker()
        self.logger = logger or logging.getLogger(__name__)
        
        # Progress callback
        self.progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable):
        """Set progress callback function"""
        self.progress_callback = callback
    
    def handle_process_file(self, task: Task) -> Dict[str, Any]:
        """Handle file processing task
        
        Args:
            task: Task to process
            
        Returns:
            Processing result dictionary
        """
        data = task.data
        file_path = Path(data['file_path'])
        profile = data.get('profile', 'default')
        auto_fix = data.get('auto_fix', False)
        
        # Set up progress callback
        if self.progress_callback:
            def progress_wrapper(file_id: str, status: str, progress: int, message: str):
                self.progress_callback(task.task_id, status, progress, message)
            self.processor.set_callbacks(on_progress=progress_wrapper)
        
        # Process file
        result = self.processor.process_with_profile(
            file_path,
            profile,
            auto_fix
        )
        
        return {
            'file_path': str(file_path),
            'status': result.status.value,
            'analysis_result': result.analysis_result,
            'quality_result': result.quality_result,
            'processing_time': result.processing_time,
            'error': result.error
        }
    
    def handle_batch_process(self, task: Task) -> Dict[str, Any]:
        """Handle batch processing task
        
        Args:
            task: Task to process
            
        Returns:
            Batch processing results
        """
        data = task.data
        file_paths = [Path(p) for p in data['file_paths']]
        profile = data.get('profile', 'default')
        
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            try:
                result = self.processor.process_with_profile(
                    file_path,
                    profile,
                    auto_fix=False
                )
                
                if result.status == ProcessingStatus.COMPLETED:
                    successful += 1
                else:
                    failed += 1
                
                results.append({
                    'file': str(file_path),
                    'success': result.status == ProcessingStatus.COMPLETED,
                    'status': result.status.value
                })
            except Exception as e:
                failed += 1
                results.append({
                    'file': str(file_path),
                    'success': False,
                    'error': str(e)
                })
                self.logger.error(f"Batch processing error for {file_path}: {e}")
        
        return {
            'total_files': len(file_paths),
            'successful': successful,
            'failed': failed,
            'results': results
        }
    
    def handle_analyze_only(self, task: Task) -> Dict[str, Any]:
        """Handle analysis-only task
        
        Args:
            task: Task to process
            
        Returns:
            Analysis results
        """
        data = task.data
        file_path = Path(data['file_path'])
        
        # Perform analysis
        analysis_result = self.analyzer.analyze(file_path)
        
        return {
            'file_path': str(file_path),
            'document': analysis_result.document.__dict__ if analysis_result.document else None,
            'issues': [issue.__dict__ for issue in analysis_result.issues],
            'metadata': analysis_result.metadata,
            'summary': analysis_result.summary
        }
    
    def handle_check_quality(self, task: Task) -> Dict[str, Any]:
        """Handle quality check task
        
        Args:
            task: Task to process
            
        Returns:
            Quality check results
        """
        data = task.data
        file_path = Path(data['file_path'])
        profile = data.get('profile', 'default')
        
        # First analyze the file
        analysis_result = self.analyzer.analyze(file_path)
        
        # Then check quality
        quality_result = self.checker.check(
            analysis_result.document,
            profile
        )
        
        return {
            'file_path': str(file_path),
            'quality_score': quality_result.quality_score,
            'passed': quality_result.passed,
            'issues': [issue.__dict__ for issue in quality_result.issues],
            'warnings': [warning.__dict__ for warning in quality_result.warnings],
            'suggestions': quality_result.suggestions
        }
    
    def handle_generate_report(self, task: Task) -> Dict[str, Any]:
        """Handle report generation task
        
        Args:
            task: Task to process
            
        Returns:
            Report generation results
        """
        data = task.data
        results = data.get('results', [])
        output_path = data.get('output_path')
        format_type = data.get('format', 'html')
        
        try:
            from ...reporting.report_generator import ReportGenerator, ReportOptions
            from ...core.quality_checker import QualityCheckResult
            
            # 보고서 생성기 초기화
            generator = ReportGenerator(self.logger)
            
            # 보고서 옵션 설정
            options = ReportOptions(
                include_thumbnails=data.get('include_thumbnails', True),
                include_charts=data.get('include_charts', True),
                include_fix_suggestions=data.get('include_fix_suggestions', True)
            )
            
            # 출력 경로 설정
            if output_path:
                output_folder = Path(output_path).parent
                output_folder.mkdir(parents=True, exist_ok=True)
            else:
                output_folder = None
            
            generated_reports = []
            
            # 각 결과에 대해 보고서 생성
            for result in results:
                if isinstance(result, dict):
                    # dict를 QualityCheckResult로 변환 필요
                    # 이 부분은 결과 데이터 구조에 따라 조정 필요
                    quality_result = result.get('quality_result')
                else:
                    quality_result = result
                
                if quality_result:
                    report_path = generator.generate(
                        quality_result,
                        format_type=format_type,
                        output_folder=output_folder,
                        options=options
                    )
                    
                    if report_path:
                        generated_reports.append(str(report_path))
            
            return {
                'report_generated': len(generated_reports) > 0,
                'output_paths': generated_reports,
                'format': format_type,
                'message': f'{len(generated_reports)}개 보고서 생성 완료' if generated_reports else '보고서 생성 실패',
                'timestamp': datetime.now().isoformat()
            }
            
        except ImportError as e:
            self.logger.error(f"보고서 모듈 임포트 실패: {e}")
            return {
                'report_generated': False,
                'output_path': output_path,
                'format': format_type,
                'message': f'보고서 모듈 임포트 실패: {e}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"보고서 생성 중 오류: {e}")
            return {
                'report_generated': False,
                'output_path': output_path,
                'format': format_type,
                'message': f'보고서 생성 오류: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def handle_auto_fix(self, task: Task) -> Dict[str, Any]:
        """Handle auto-fix task
        
        Args:
            task: Task to process
            
        Returns:
            Auto-fix results
        """
        data = task.data
        file_path = Path(data['file_path'])
        fixes = data.get('fixes', [])
        backup = data.get('backup', True)
        profile = data.get('profile', 'default')
        output_path = data.get('output_path')
        
        try:
            from ...core.fixers.auto_fixer import AutoFixer
            
            backup_path = None
            # 백업 생성
            if backup:
                backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
                import shutil
                shutil.copy2(file_path, backup_path)
                self.logger.info(f"백업 생성: {backup_path}")
            
            # 자동 수정기 초기화
            fixer = AutoFixer(self.logger)
            
            # 수정 옵션 설정
            fix_options = {
                'fixes_to_apply': fixes,  # 적용할 수정 목록
                'aggressive': data.get('aggressive', False),  # 적극적 수정 여부
                'preserve_metadata': data.get('preserve_metadata', True),  # 메타데이터 보존
                'compress': data.get('compress', False)  # 압축 여부
            }
            
            # 출력 경로 설정
            if output_path:
                output_path = Path(output_path)
            else:
                # 기본값: 원본 파일 덮어쓰기
                output_path = file_path
            
            # 자동 수정 실행
            result = fixer.auto_fix(
                input_path=file_path,
                output_path=output_path,
                profile=profile,
                options=fix_options
            )
            
            # 결과 반환
            fixes_applied = []
            if result.success and result.fixes_applied:
                fixes_applied = [fix.__dict__ for fix in result.fixes_applied]
            
            return {
                'file_path': str(file_path),
                'output_path': str(output_path),
                'fixes_requested': fixes,
                'fixes_applied': fixes_applied,
                'backup_created': backup_path is not None,
                'backup_path': str(backup_path) if backup_path else None,
                'success': result.success,
                'message': result.message,
                'error': result.error if hasattr(result, 'error') else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except ImportError as e:
            self.logger.error(f"자동 수정 모듈 임포트 실패: {e}")
            return {
                'file_path': str(file_path),
                'fixes_requested': fixes,
                'fixes_applied': [],
                'backup_created': False,
                'message': f'자동 수정 모듈 임포트 실패: {e}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"자동 수정 중 오류: {e}")
            return {
                'file_path': str(file_path),
                'fixes_requested': fixes,
                'fixes_applied': [],
                'backup_created': False,
                'message': f'자동 수정 오류: {e}',
                'timestamp': datetime.now().isoformat()
            }