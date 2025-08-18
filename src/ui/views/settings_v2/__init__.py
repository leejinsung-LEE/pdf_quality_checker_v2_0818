# src/ui/views/settings_v2/__init__.py
"""
환경설정 뷰 V2 - 리뉴얼 버전

사이드바 네비게이션과 4개 카테고리로 재구성된 모던한 환경설정 뷰입니다.
"""

from .settings_view_v2 import SettingsViewV2
from .categories import GeneralCategory, ProcessingCategory, NotificationCategory, AdvancedCategory

__all__ = [
    'SettingsViewV2',
    'GeneralCategory',
    'ProcessingCategory', 
    'NotificationCategory',
    'AdvancedCategory'
]

# 모듈 정보
__version__ = "2.0.0"
__author__ = "PDF Quality Checker Team"
__description__ = "Modern Settings View with Sidebar Navigation"