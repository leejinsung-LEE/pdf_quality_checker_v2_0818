# src/utils/alarm_manager.py
"""
알람 매니저 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 alarm_manager/ 디렉토리의 모듈로 분리되었습니다.
"""

# 모든 공개 API를 재노출
from .alarm_manager import (
    # 메인 클래스
    AlarmManager,
    NotificationHistory,
    
    # 싱글톤 함수
    get_alarm_manager,
    test_alarm_manager,
    
    # 상태 변수 (하위 호환성)
    NOTIFICATION_AVAILABLE,
    NOTIFICATION_METHOD
)

# 추가 모듈 접근 (필요시)
from .alarm_manager.models import NotificationData, RateLimiter
from .alarm_manager.validators import (
    CooldownValidator, RateLimitValidator, 
    QuietHoursValidator, AlarmValidator
)
from .alarm_manager.notifiers import (
    BaseNotifier, SystemNotifier, SoundNotifier,
    PopupNotifier, TrayNotifier, LogNotifier, NotifierFactory
)
from .alarm_manager.singleton import reset_alarm_manager, configure_alarm_manager

# 하위 호환성을 위한 상수 (필요시)
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

__all__ = [
    'AlarmManager',
    'NotificationHistory',
    'get_alarm_manager',
    'test_alarm_manager',
    'NOTIFICATION_AVAILABLE',
    'NOTIFICATION_METHOD',
    # 추가 모듈 (선택적)
    'NotificationData',
    'RateLimiter',
    'CooldownValidator',
    'RateLimitValidator',
    'QuietHoursValidator',
    'AlarmValidator',
    'BaseNotifier',
    'SystemNotifier',
    'SoundNotifier',
    'PopupNotifier',
    'TrayNotifier',
    'LogNotifier',
    'NotifierFactory',
    'reset_alarm_manager',
    'configure_alarm_manager',
]

# 하위 호환성 메시지
def __getattr__(name):
    """동적 속성 접근 처리"""
    import warnings
    warnings.warn(
        f"'{name}'에 대한 직접 접근은 deprecated 되었습니다. "
        f"'from utils.alarm_manager import {name}'를 사용하세요.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 모듈에서 속성 찾기
    from . import alarm_manager
    if hasattr(alarm_manager, name):
        return getattr(alarm_manager, name)
    
    raise AttributeError(f"module 'utils.alarm_manager' has no attribute '{name}'")