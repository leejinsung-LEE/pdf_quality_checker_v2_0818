# src/core/profiles/profile_manager/__init__.py
"""
프로파일 관리 시스템 모듈

PDF 품질 검사 프로파일을 관리하고 적용하는 시스템입니다.
- 기본 제공 프로파일 (default, strict, quick, web)
- 사용자 정의 프로파일 생성/수정/삭제
- 프로파일 상속 기능
- 프로파일 내보내기/가져오기
"""

from typing import Optional
from pathlib import Path

from .models import QualityProfile, ProfileMetadata
from .manager import ProfileManager
from .builtin_profiles import BuiltinProfileProvider
from .io_handler import ProfileIOHandler
from .crud_operations import ProfileCRUD

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...checkers import CheckerContext


# 공개 API
__all__ = [
    # 메인 클래스
    'QualityProfile',
    'ProfileMetadata',
    'ProfileManager',
    
    # 서브 컴포넌트
    'BuiltinProfileProvider',
    'ProfileIOHandler',
    'ProfileCRUD',
    
    # 싱글톤 함수
    'get_profile_manager',
    'reset_profile_manager',
]


# 전역 프로파일 매니저 인스턴스
from functools import lru_cache


@lru_cache(maxsize=1)
def get_profile_manager() -> ProfileManager:
    """
    프로파일 매니저 싱글톤 인스턴스 반환 (스레드 안전)
    
    LRU 캐시를 사용하여 싱글톤 패턴을 구현합니다.
    Python 내장 기능으로 스레드 안전성이 보장됩니다.
    
    Returns:
        ProfileManager: 싱글톤 인스턴스
        
    Example:
        >>> manager = get_profile_manager()
        >>> profile = manager.get_current_profile()
        >>> context = profile.to_checker_context()
    """
    return ProfileManager()


def reset_profile_manager():
    """
    프로파일 매니저 인스턴스 리셋 (테스트용)
    """
    get_profile_manager.cache_clear()


def create_default_profiles_if_needed(profiles_dir: Optional[Path] = None):
    """
    기본 프로파일이 없을 경우 생성
    
    Args:
        profiles_dir: 프로파일 디렉토리
    """
    manager = ProfileManager(profiles_dir)
    
    # 기본 프로파일이 없으면 생성
    if not manager.has_profile('default'):
        builtin_profiles = BuiltinProfileProvider.create_all_builtin_profiles()
        for name, profile in builtin_profiles.items():
            manager.profiles[name] = profile
        manager.save_profiles()