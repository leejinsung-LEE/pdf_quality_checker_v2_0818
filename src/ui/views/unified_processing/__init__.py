"""
통합 처리 뷰 모듈

실시간 처리와 처리 이력을 통합하여 표시하는 뷰입니다.
처리 중인 항목은 상단에, 완료된 항목은 하단에 표시됩니다.

최종 수정: 2025-01-12
"""

from .base import UnifiedProcessingView

__all__ = ['UnifiedProcessingView']