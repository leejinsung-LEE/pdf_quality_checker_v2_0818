# src/ui/components/sidebar.py
"""
사이드바 컴포넌트 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 sidebar/ 모듈에 있습니다.

모듈화 이후에도 기존 임포트가 동작하도록 합니다:
- from .sidebar import Sidebar
- from src.ui.components.sidebar import Sidebar
"""

# 모듈화된 구현에서 가져오기
from .sidebar import Sidebar

# 호환성을 위한 export
__all__ = ['Sidebar']