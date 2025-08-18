# src/processing/processor/single_processor.py
"""
단일 PDF 파일 처리기
"""

from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import logging

from .models import FileInfo
from .utils import prepare_options, generate_file_id
from ..pipeline import (
    PDFProcessingPipeline, 
    PipelineOptions, 
    ProcessingResult,
    ProcessingStatus
)

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.profiles import ProfileManager


class PDFProcessor:
    """
    단일 PDF 파일 처리기
    
    파이프라인을 래핑하여 UI에서 쉽게 사용할 수 있도록 합니다.
    """
    
    def __init__(self,
                 profile_manager: Optional['ProfileManager'] = None,
                 logger: Optional[logging.Logger] = None):
        """
        처리기 초기화
        
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
        
        # 파이프라인
        self.pipeline = PDFProcessingPipeline(self.profile_manager, self.logger)
        
        # 콜백 함수들
        self.on_start: Optional[Callable] = None
        self.on_progress: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # 처리 중인 파일 추적
        self.processing_files: Dict[str, FileInfo] = {}
    
    def set_callbacks(self,
                     on_start: Optional[Callable] = None,
                     on_progress: Optional[Callable] = None,
                     on_complete: Optional[Callable] = None,
                     on_error: Optional[Callable] = None):
        """
        콜백 함수 설정
        
        Args:
            on_start: 처리 시작 콜백 (file_info)
            on_progress: 진행률 콜백 (file_id, status, progress, message)
            on_complete: 완료 콜백 (file_info, result)
            on_error: 오류 콜백 (file_info, error)
        """
        self.on_start = on_start
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        
        # 파이프라인에 진행률 콜백 설정
        if on_progress:
            self.pipeline.set_progress_callback(self._progress_wrapper)
    
    def process_file(self, 
                    file_path: Path,
                    file_id: Optional[str] = None,
                    folder_config: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        단일 파일 처리
        
        Args:
            file_path: PDF 파일 경로
            file_id: 파일 식별자
            folder_config: 폴더 설정 (폴더 감시용)
            
        Returns:
            ProcessingResult: 처리 결과
        """
        # 파일 정보 생성
        if file_id is None:
            file_id = generate_file_id(file_path)
        
        file_info = FileInfo(
            path=file_path,
            file_id=file_id,
            folder_config=folder_config
        )
        
        # 처리 중 목록에 추가
        self.processing_files[file_id] = file_info
        
        try:
            # 시작 콜백
            if self.on_start:
                self.on_start(file_info)
            
            # 옵션 준비
            options = prepare_options(folder_config)
            
            # 처리 실행
            result = self.pipeline.process(file_path, options, file_id)
            
            # 완료 콜백
            if self.on_complete:
                self.on_complete(file_info, result)
            
            return result
            
        except Exception as e:
            # 오류 콜백
            if self.on_error:
                self.on_error(file_info, str(e))
            
            # 오류 결과 생성
            return ProcessingResult(
                file_path=file_path,
                status=ProcessingStatus.ERROR,
                error=str(e)
            )
        
        finally:
            # 처리 중 목록에서 제거
            self.processing_files.pop(file_id, None)
    
    def process_with_profile(self,
                           file_path: Path,
                           profile_name: str,
                           auto_fix: bool = False) -> ProcessingResult:
        """
        특정 프로파일로 파일 처리
        
        Args:
            file_path: PDF 파일 경로
            profile_name: 프로파일 이름
            auto_fix: 자동 수정 여부
            
        Returns:
            ProcessingResult: 처리 결과
        """
        options = PipelineOptions(
            profile_name=profile_name,
            auto_fix=auto_fix
        )
        
        file_id = generate_file_id(file_path)
        return self.pipeline.process(file_path, options, file_id)
    
    def process_immediate(self,
                         file_paths: List[Path],
                         profile_name: str = "default") -> List[ProcessingResult]:
        """
        여러 파일 즉시 처리 (드래그앤드롭용)
        
        Args:
            file_paths: PDF 파일 경로 목록
            profile_name: 프로파일 이름
            
        Returns:
            List[ProcessingResult]: 처리 결과 목록
        """
        results = []
        
        for file_path in file_paths:
            result = self.process_with_profile(file_path, profile_name)
            results.append(result)
        
        return results
    
    def _progress_wrapper(self, file_id: str, status: ProcessingStatus, progress: int, message: str):
        """진행률 콜백 래퍼"""
        if self.on_progress:
            # 상태를 문자열로 변환
            status_str = status.value
            self.on_progress(file_id, status_str, progress, message)
    
    def get_processing_count(self) -> int:
        """현재 처리 중인 파일 수"""
        return len(self.processing_files)
    
    def get_processing_files(self) -> List[FileInfo]:
        """처리 중인 파일 목록"""
        return list(self.processing_files.values())
    
    def is_processing(self, file_id: str) -> bool:
        """특정 파일 처리 중인지 확인"""
        return file_id in self.processing_files