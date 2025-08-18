# src/ui/controllers/profile_controller.py
"""
프로파일 관리 컨트롤러 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 profile_controller/ 모듈에 있습니다.

모듈화 이후에도 기존 임포트가 동작하도록 합니다:
- from .profile_controller import ProfileController
- from src.ui.controllers.profile_controller import ProfileInfo, get_profile_controller
"""

# 모듈화된 구현에서 가져오기
from .profile_controller import ProfileController, ProfileInfo, get_profile_controller

# 호환성을 위한 export
__all__ = ['ProfileController', 'ProfileInfo', 'get_profile_controller']