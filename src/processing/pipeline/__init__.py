# src/processing/pipeline/__init__.py
"""
PDF 처리 파이프라인 모듈

이 모듈은 PDF 처리의 전체 워크플로우를 관리합니다:
- PDF 분석
- 품질 검사
- 자동 수정
- 보고서 생성
- 데이터베이스 저장
"""

from typing import Union
from pathlib import Path

from .enums import ProcessingStatus
from .models import PipelineOptions, ProcessingResult
from .processor import PDFProcessingPipeline
from .stages import PipelineStages
from .progress import ProgressManager

# 공개 API
__all__ = [
    'ProcessingStatus',
    'PipelineOptions',
    'ProcessingResult',
    'PDFProcessingPipeline',
    'PipelineStages',
    'ProgressManager',
    'process_pdf',  # 편의 함수
]


# 편의 함수
def process_pdf(pdf_path: Union[str, Path], 
                profile: str = "default",
                auto_fix: bool = False) -> ProcessingResult:
    """
    PDF 처리 편의 함수
    
    Args:
        pdf_path: PDF 파일 경로
        profile: 사용할 프로파일 이름
        auto_fix: 자동 수정 여부
        
    Returns:
        처리 결과
        
    Example:
        >>> result = process_pdf("sample.pdf", profile="print_ready", auto_fix=True)
        >>> if result.success:
        ...     print(f"품질 점수: {result.quality_result.quality_score}")
    """
    pipeline = PDFProcessingPipeline()
    options = PipelineOptions(
        profile_name=profile,
        auto_fix=auto_fix
    )
    return pipeline.process(pdf_path, options)