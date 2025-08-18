# src/ui/views/profile_manager_view.py
"""
프로파일 관리 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 profile_manager/ 모듈에 모듈화되어 있습니다.

AI 친화적 설명:
- 기존 import 경로 유지를 위한 호환성 래퍼
- 모듈화된 새로운 구조로의 투명한 전환 제공
- 기존 코드 수정 없이 새로운 아키텍처 적용

마이그레이션 가이드:
기존: from src.ui.views.profile_manager_view import ProfileManagerView
새로운: from src.ui.views.profile_manager import ProfileManagerView (권장)
또는: from src.ui.views.profile_manager_view import ProfileManagerView (호환)
"""

# 새로운 모듈화된 구조에서 클래스들을 가져와서 재export
from .profile_manager.base import ProfileManagerView
from .profile_manager.dialogs import ProfileCreateDialog

# 호환성을 위한 __all__ 정의
__all__ = ['ProfileManagerView', 'ProfileCreateDialog']

# 모듈 메타데이터 (정보성)
__version__ = "2.0.0"  # 모듈화된 버전
__architecture__ = "modular"  # 아키텍처 타입
__migration_status__ = "complete"  # 마이그레이션 상태