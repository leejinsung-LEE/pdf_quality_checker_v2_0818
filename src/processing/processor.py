# src/processing/processor.py
"""
단일 파일 처리기 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 processor/ 디렉토리의 모듈로 분리되었습니다.
"""

# 모든 공개 API를 재노출
from .processor import (
    FileInfo,
    PDFProcessor,
    ProcessorPool,
    get_processor
)

# 파이프라인 관련 임포트 (하위 호환성)
from .pipeline import (
    ProcessingStatus,
    PipelineOptions,
    ProcessingResult
)

__all__ = [
    'FileInfo',
    'PDFProcessor',
    'ProcessorPool',
    'get_processor',
    # 파이프라인 관련 (하위 호환성)
    'ProcessingStatus',
    'PipelineOptions',
    'ProcessingResult',
]

# 하위 호환성 메시지
def __getattr__(name):
    """동적 속성 접근 처리"""
    import warnings
    warnings.warn(
        f"'{name}'에 대한 직접 접근은 deprecated 되었습니다. "
        f"'from processing.processor import {name}'를 사용하세요.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 모듈에서 속성 찾기
    from . import processor
    if hasattr(processor, name):
        return getattr(processor, name)
    
    raise AttributeError(f"module 'processing.processor' has no attribute '{name}'")