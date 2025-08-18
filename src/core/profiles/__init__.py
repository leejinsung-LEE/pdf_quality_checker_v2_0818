# src/core/profiles/__init__.py
"""
PDF 품질 검사 프로파일 시스템

검사 규칙, 심각도, 기준값 등을 프로파일로 관리합니다.
"""

from .profile_manager import ProfileManager, QualityProfile, get_profile_manager

__all__ = [
    'ProfileManager',
    'QualityProfile', 
    'get_profile_manager',
]


# 편의 함수들
def load_profile(name: str) -> QualityProfile:
    """프로파일 로드 편의 함수"""
    manager = get_profile_manager()
    profile = manager.get_profile(name)
    if not profile:
        raise ValueError(f"프로파일 '{name}'을 찾을 수 없습니다")
    return profile


def get_current_profile() -> QualityProfile:
    """현재 프로파일 가져오기"""
    manager = get_profile_manager()
    profile = manager.get_current_profile()
    if not profile:
        raise ValueError("현재 프로파일이 설정되지 않았습니다")
    return profile


def list_profiles() -> list:
    """사용 가능한 프로파일 목록"""
    manager = get_profile_manager()
    return manager.get_profile_list()