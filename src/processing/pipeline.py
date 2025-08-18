# src/processing/pipeline.py
"""
PDF 처리 파이프라인 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 pipeline/ 디렉토리의 모듈로 분리되었습니다.
"""

# 모든 공개 API를 재노출
from .pipeline import (
    ProcessingStatus,
    PipelineOptions,
    ProcessingResult,
    PDFProcessingPipeline,
    process_pdf
)

# 하위 호환성을 위한 추가 임포트
from .pipeline.stages import PipelineStages
from .pipeline.progress import ProgressManager

__all__ = [
    'ProcessingStatus',
    'PipelineOptions',
    'ProcessingResult',
    'PDFProcessingPipeline',
    'process_pdf',
    'PipelineStages',
    'ProgressManager',
]

# 하위 호환성 메시지
def __getattr__(name):
    """동적 속성 접근 처리"""
    import warnings
    warnings.warn(
        f"'{name}'에 대한 직접 접근은 deprecated 되었습니다. "
        f"'from processing.pipeline import {name}'를 사용하세요.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 모듈에서 속성 찾기
    from . import pipeline
    if hasattr(pipeline, name):
        return getattr(pipeline, name)
    
    raise AttributeError(f"module 'processing.pipeline' has no attribute '{name}'")