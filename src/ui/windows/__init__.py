# src/ui/windows/__init__.py
"""
UI 윈도우 모듈 (통합 버전)

애플리케이션의 윈도우들을 제공합니다.
메인 윈도우 구조가 통합되어 더 효율적으로 관리됩니다.
"""

from .main_window import create_main_window

# 호환성을 위한 MainWindow 래퍼
def MainWindow():
    """메인 윈도우 생성 (호환성 래퍼)"""
    return create_main_window()

__all__ = ['MainWindow', 'create_main_window']