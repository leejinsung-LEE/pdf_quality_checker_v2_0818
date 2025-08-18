"""
통합 처리 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 unified_processing/ 디렉토리에 모듈화되어 있습니다.

마이그레이션:
기존: from src.ui.views.unified_processing_view import UnifiedProcessingView
새로운: from src.ui.views.unified_processing import UnifiedProcessingView

최종 수정: 2025-01-12
"""

from .unified_processing import UnifiedProcessingView

__all__ = ['UnifiedProcessingView']