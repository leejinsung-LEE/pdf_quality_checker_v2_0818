# src/processing/processor/__init__.py
"""
PDF 파일 처리기 모듈

이 모듈은 파이프라인을 래핑하여 UI에서 쉽게 사용할 수 있도록 합니다:
- 단일 파일 처리
- 다중 파일 동시 처리
- 진행률 추적
- 콜백 관리
"""

from functools import lru_cache

from .models import FileInfo
from .single_processor import PDFProcessor
from .pool import ProcessorPool
from .utils import prepare_options, generate_file_id

# 공개 API
__all__ = [
    'FileInfo',
    'PDFProcessor',
    'ProcessorPool',
    'prepare_options',
    'generate_file_id',
    'get_processor',  # 싱글톤 함수
    'reset_processor',  # 리셋 함수
]


@lru_cache(maxsize=1)
def get_processor() -> PDFProcessor:
    """
    PDF 프로세서 싱글톤 인스턴스 반환 (스레드 안전)
    
    Returns:
        PDFProcessor: 전역 프로세서 인스턴스
        
    Example:
        >>> processor = get_processor()
        >>> result = processor.process_with_profile(Path("sample.pdf"), "print_ready")
    """
    return PDFProcessor()


def reset_processor() -> None:
    """PDF 프로세서 인스턴스 리셋 (테스트용)"""
    get_processor.cache_clear()