# src/processing/pipeline/processor.py
"""
메인 파이프라인 프로세서
"""

from typing import Optional, Union, Callable, Protocol
from pathlib import Path
import time
import logging

from .enums import ProcessingStatus
from .models import PipelineOptions, ProcessingResult
from .stages import PipelineStages
from .progress import ProgressManager


# 커스텀 예외 클래스
class PipelineError(Exception):
    """파이프라인 기본 예외"""
    pass


class PipelineInitializationError(PipelineError):
    """파이프라인 초기화 오류"""
    pass


class PipelineStageError(PipelineError):
    """파이프라인 스테이지 처리 오류"""
    pass


class PipelineValidationError(PipelineError):
    """파이프라인 검증 오류"""
    pass

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.profiles import ProfileManager
    from ...core.analyzers import PDFAnalyzer
    from ...core.quality_checker import PDFQualityChecker


class ProgressCallback(Protocol):
    """진행 상황 콜백 프로토콜"""
    def __call__(self, progress: int, message: str) -> None:
        """진행 상황 업데이트"""
        ...


class ProfileProvider(Protocol):
    """프로파일 제공자 프로토콜"""
    def get_profile(self, name: str) -> dict:
        """프로파일 조회"""
        ...
    
    def get_active_profile(self) -> dict:
        """활성 프로파일 조회"""
        ...


class PDFProcessingPipeline:
    """
    PDF 처리 파이프라인
    
    v2의 모든 구성요소를 연결하여 통합 처리 흐름을 제공합니다.
    """
    
    def __init__(self, 
                 profile_manager: Optional['ProfileManager'] = None,
                 logger: Optional[logging.Logger] = None):
        """
        파이프라인 초기화
        
        Args:
            profile_manager: 프로파일 관리자
            logger: 로거
        """
        # 프로파일 관리자 설정
        if profile_manager is None:
            from ...core.profiles import get_profile_manager
            profile_manager = get_profile_manager()
        self.profile_manager = profile_manager
        
        self.logger = logger or logging.getLogger(__name__)
        
        # 핵심 구성요소 초기화
        from ...core.analyzers import PDFAnalyzer
        from ...core.quality_checker import PDFQualityChecker
        
        self.analyzer = PDFAnalyzer()
        self.quality_checker = PDFQualityChecker(self.profile_manager)
        
        # 스테이지 및 진행률 관리자
        self.stages = PipelineStages(self.logger)
        self.progress_manager = ProgressManager()
        
        # 진행 상태 콜백
        self.progress_callback: Optional[ProgressCallback] = None
    
    def set_progress_callback(self, callback: ProgressCallback) -> None:
        """
        진행 상태 콜백 설정
        
        Args:
            callback: 진행 상황 업데이트 콜백
        """
        self.progress_callback = callback
        self.progress_manager.set_callback(callback)
    
    def process(self, 
                pdf_path: Union[str, Path], 
                options: Optional[PipelineOptions] = None,
                file_id: Optional[str] = None) -> ProcessingResult:
        """
        PDF 파일 처리 - 전체 워크플로우
        
        Args:
            pdf_path: PDF 파일 경로
            options: 처리 옵션
            file_id: 파일 식별자 (진행률 추적용)
            
        Returns:
            ProcessingResult: 처리 결과
        """
        start_time = time.time()
        pdf_path = Path(pdf_path)
        
        if options is None:
            options = PipelineOptions()
        
        # 결과 초기화
        result = ProcessingResult(
            file_path=pdf_path,
            status=ProcessingStatus.WAITING
        )
        
        try:
            # 1. PDF 분석
            result.status = ProcessingStatus.ANALYZING
            self.progress_manager.update(file_id, result.status, 10, "PDF 분석 시작")
            
            analysis_result = self.stages.analyze_pdf(self.analyzer, pdf_path)
            result.analysis_result = analysis_result
            self.progress_manager.update(file_id, result.status, 30, "PDF 분석 완료")
            
            # 2. 품질 검사
            result.status = ProcessingStatus.CHECKING
            self.progress_manager.update(file_id, result.status, 40, "품질 검사 시작")
            
            quality_result = self.stages.check_quality(
                self.quality_checker,
                pdf_path,
                options.profile_name,
                analysis_result,
                options.check_options
            )
            result.quality_result = quality_result
            self.progress_manager.update(
                file_id, result.status, 60,
                f"{quality_result.error_count}개 오류, {quality_result.warning_count}개 경고 발견"
            )
            
            # 3. 자동 수정 (옵션)
            if options.auto_fix and self.stages.should_auto_fix(quality_result):
                result.status = ProcessingStatus.FIXING
                self.progress_manager.update(file_id, result.status, 70, "자동 수정 시작")
                
                fix_result = self.stages.auto_fix(pdf_path, quality_result, options.fix_options)
                result.fix_result = fix_result
                
                # 수정된 파일로 재분석 필요시
                if fix_result and fix_result.get('fixed_path'):
                    fixed_path = Path(fix_result['fixed_path'])
                    re_analysis = self.stages.analyze_pdf(self.analyzer, fixed_path)
                    re_check = self.stages.check_quality(
                        self.quality_checker,
                        fixed_path,
                        options.profile_name,
                        re_analysis,
                        options.check_options
                    )
                    
                    # 수정 전후 비교 정보 추가
                    fix_result['before_errors'] = quality_result.error_count
                    fix_result['after_errors'] = re_check.error_count
                    fix_result['improvements'] = quality_result.error_count - re_check.error_count
                
                self.progress_manager.update(file_id, result.status, 80, "자동 수정 완료")
            
            # 4. 보고서 생성 (옵션)
            if options.generate_report:
                result.status = ProcessingStatus.REPORTING
                self.progress_manager.update(file_id, result.status, 85, "보고서 생성 시작")
                
                report_paths = self.stages.generate_reports(
                    quality_result,
                    options.report_formats,
                    options.output_folder
                )
                result.report_paths = report_paths
                self.progress_manager.update(file_id, result.status, 95, "보고서 생성 완료")
            
            # 5. 데이터베이스 저장 (옵션)
            if options.save_to_database:
                self.stages.save_to_database(quality_result, result)
            
            # 6. 파일 이동 (옵션)
            if options.move_to_completed:
                self.stages.move_to_completed(pdf_path, result.fix_result)
            
            # 완료
            result.status = ProcessingStatus.COMPLETED
            result.processing_time = time.time() - start_time
            self.progress_manager.update(file_id, result.status, 100, "처리 완료")
            
            self.logger.info(f"PDF 처리 완료: {pdf_path.name} ({result.processing_time:.2f}초)")
            
        except Exception as e:
            result.status = ProcessingStatus.ERROR
            result.error = str(e)
            result.processing_time = time.time() - start_time
            
            self.logger.error(f"PDF 처리 오류: {pdf_path.name} - {e}")
            self.progress_manager.update(file_id, result.status, 0, f"오류: {str(e)}")
        
        return result