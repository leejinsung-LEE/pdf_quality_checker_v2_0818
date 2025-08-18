"""
프로파일 설정 모듈 - 하위 호환성을 위한 export

이 파일은 profile_settings_view.py와의 하위 호환성을 제공합니다.
"""

from .base import ProfileSettingsView

__all__ = ['ProfileSettingsView']