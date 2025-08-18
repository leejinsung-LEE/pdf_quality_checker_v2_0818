# src/core/profiles/profile_manager.py
"""
프로파일 관리 시스템 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 profile_manager/ 디렉토리의 모듈로 분리되었습니다.
"""

# 모든 공개 API를 재노출
from .profile_manager import (
    QualityProfile,
    ProfileMetadata,
    ProfileManager,
    get_profile_manager,
    reset_profile_manager
)

# 추가 모듈 접근 (필요시)
from .profile_manager.builtin_profiles import BuiltinProfileProvider
from .profile_manager.io_handler import ProfileIOHandler
from .profile_manager.crud_operations import ProfileCRUD

__all__ = [
    'QualityProfile',
    'ProfileMetadata',
    'ProfileManager',
    'get_profile_manager',
    'reset_profile_manager',
    # 추가 모듈 (선택적)
    'BuiltinProfileProvider',
    'ProfileIOHandler',
    'ProfileCRUD',
]

# 하위 호환성 메시지
def __getattr__(name):
    """동적 속성 접근 처리"""
    import warnings
    warnings.warn(
        f"'{name}'에 대한 직접 접근은 deprecated 되었습니다. "
        f"'from core.profiles.profile_manager import {name}'를 사용하세요.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 모듈에서 속성 찾기
    from . import profile_manager
    if hasattr(profile_manager, name):
        return getattr(profile_manager, name)
    
    raise AttributeError(f"module 'core.profiles.profile_manager' has no attribute '{name}'")