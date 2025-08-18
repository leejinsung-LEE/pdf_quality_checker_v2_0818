"""
일괄 처리 모듈 - 하위 호환성을 위한 export

이 파일은 batch_process_view.py와의 하위 호환성을 제공합니다.
"""

from .base import BatchProcessView

__all__ = ['BatchProcessView']