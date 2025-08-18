# src/processing/pipeline/stages.py
"""
파이프라인 스테이지별 처리 로직
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from .enums import ProcessingStatus
from .models import ProcessingResult

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.models import AnalysisResult
    from ...core.quality_checker import QualityCheckResult
    from ...core.analyzers import PDFAnalyzer
    from ...core.quality_checker import PDFQualityChecker


class PipelineStages:
    """파이프라인 스테이지 처리 담당"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze_pdf(self, 
                   analyzer: 'PDFAnalyzer',
                   pdf_path: Path) -> 'AnalysisResult':
        """
        PDF 분석 스테이지
        
        Args:
            analyzer: PDF 분석기
            pdf_path: PDF 파일 경로
            
        Returns:
            분석 결과
        """
        self.logger.debug(f"PDF 분석 시작: {pdf_path}")
        return analyzer.analyze(pdf_path)
    
    def check_quality(self,
                     quality_checker: 'PDFQualityChecker',
                     pdf_path: Path,
                     profile_name: str,
                     analysis_result: Optional['AnalysisResult'] = None,
                     check_options: Optional[Dict[str, bool]] = None) -> 'QualityCheckResult':
        """
        품질 검사 스테이지
        
        Args:
            quality_checker: 품질 검사기
            pdf_path: PDF 파일 경로
            profile_name: 프로파일 이름
            analysis_result: 분석 결과
            check_options: 검사 옵션
            
        Returns:
            품질 검사 결과
        """
        self.logger.debug(f"품질 검사 시작: {pdf_path} (프로파일: {profile_name})")
        return quality_checker.check(pdf_path, profile_name, analysis_result, check_options)
    
    def should_auto_fix(self, quality_result: 'QualityCheckResult') -> bool:
        """
        자동 수정 필요 여부 판단
        
        Args:
            quality_result: 품질 검사 결과
            
        Returns:
            자동 수정 필요 여부
        """
        # 수정 가능한 이슈가 있는지 확인
        fixable_issues = [
            issue for issue in quality_result.issues 
            if issue.is_fixable
        ]
        return len(fixable_issues) > 0
    
    def auto_fix(self,
                pdf_path: Path,
                quality_result: 'QualityCheckResult',
                fix_options: Dict[str, bool]) -> Optional[Dict[str, Any]]:
        """
        자동 수정 스테이지 (백업 지원)
        
        Args:
            pdf_path: PDF 파일 경로
            quality_result: 품질 검사 결과
            fix_options: 수정 옵션
            
        Returns:
            수정 결과
        """
        # 백업 매니저 가져오기
        backup_id = None
        try:
            from ...data import get_backup_manager
            backup_manager = get_backup_manager()
            
            # 수정 전 백업 생성
            changes_to_make = []
            for issue in quality_result.issues:
                if issue.is_fixable:
                    changes_to_make.append(f"{issue.category.value}: {issue.description}")
            
            if changes_to_make:
                backup_id = backup_manager.create_backup(
                    file_path=pdf_path,
                    profile_used=quality_result.profile_name,
                    changes_to_make=changes_to_make[:5],  # 최대 5개만 기록
                    metadata={
                        'quality_score': quality_result.quality_score,
                        'error_count': quality_result.error_count,
                        'warning_count': quality_result.warning_count,
                        'fix_options': fix_options
                    }
                )
                
                if backup_id:
                    self.logger.info(f"백업 생성 완료: {backup_id}")
                else:
                    self.logger.warning("백업 생성 실패 - 자동 수정을 계속합니다")
                    
        except Exception as e:
            self.logger.warning(f"백업 생성 중 오류: {e}")
        
        # 자동 수정 실행
        try:
            from ...fixers import FixerManager
            fixer_manager = FixerManager()
            
            fix_result = fixer_manager.fix(pdf_path, quality_result, fix_options)
            
            # 수정 성공 시 백업 ID 기록
            if fix_result and backup_id:
                fix_result['backup_id'] = backup_id
                
            return fix_result
            
        except ImportError:
            self.logger.warning("자동 수정 모듈을 찾을 수 없습니다")
            return None
        except Exception as e:
            self.logger.error(f"자동 수정 실패: {e}")
            
            # 백업이 있으면 롤백 옵션 제공
            if backup_id:
                self.logger.info(f"롤백 가능 - 백업 ID: {backup_id}")
                try:
                    # 심각한 오류의 경우 자동 롤백
                    if "critical" in str(e).lower() or "corrupt" in str(e).lower():
                        backup_manager.rollback(pdf_path, backup_id)
                        self.logger.info("파일이 자동으로 롤백되었습니다")
                except:
                    pass
                    
            return None
    
    def generate_reports(self,
                        quality_result: 'QualityCheckResult',
                        formats: List[str],
                        output_folder: Optional[Path] = None) -> Dict[str, Path]:
        """
        보고서 생성 스테이지
        
        Args:
            quality_result: 품질 검사 결과
            formats: 보고서 형식 목록
            output_folder: 출력 폴더
            
        Returns:
            형식별 보고서 경로
        """
        try:
            from ...reporting import ReportGenerator
            report_generator = ReportGenerator()
        except ImportError:
            self.logger.warning("보고서 생성 모듈을 찾을 수 없습니다")
            return {}
        
        report_paths = {}
        for format_type in formats:
            try:
                path = report_generator.generate(
                    quality_result,
                    format_type,
                    output_folder
                )
                if path:
                    report_paths[format_type] = path
            except Exception as e:
                self.logger.error(f"{format_type} 보고서 생성 실패: {e}")
        
        return report_paths
    
    def save_to_database(self, 
                        quality_result: 'QualityCheckResult',
                        process_result: ProcessingResult):
        """
        데이터베이스 저장 스테이지
        
        Args:
            quality_result: 품질 검사 결과
            process_result: 처리 결과
        """
        try:
            from ...data import DataManager
            data_manager = DataManager()
            data_manager.save_processing_result(quality_result, process_result)
        except ImportError:
            self.logger.debug("데이터 관리 모듈을 찾을 수 없습니다")
        except Exception as e:
            self.logger.error(f"데이터베이스 저장 실패: {e}")
    
    def move_to_completed(self, 
                         pdf_path: Path,
                         fix_result: Optional[Dict[str, Any]]):
        """
        완료 폴더로 이동 스테이지
        
        Args:
            pdf_path: 원본 PDF 경로
            fix_result: 수정 결과
        """
        try:
            from datetime import datetime
            from ...config import Config
            
            completed_folder = Config.COMPLETED_FOLDER
            completed_folder.mkdir(parents=True, exist_ok=True)
            
            # 수정된 파일이 있으면 그것을, 없으면 원본을 이동
            source_path = pdf_path
            if fix_result and fix_result.get('fixed_path'):
                source_path = Path(fix_result['fixed_path'])
            
            dest_path = completed_folder / source_path.name
            
            # 이름 중복 처리
            if dest_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                stem = source_path.stem
                suffix = source_path.suffix
                dest_path = completed_folder / f"{stem}_{timestamp}{suffix}"
            
            source_path.rename(dest_path)
            self.logger.info(f"파일 이동: {source_path.name} → completed/")
            
        except Exception as e:
            self.logger.error(f"파일 이동 실패: {e}")