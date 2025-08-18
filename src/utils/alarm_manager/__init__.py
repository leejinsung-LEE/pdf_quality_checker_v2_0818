# src/utils/alarm_manager/__init__.py
"""
알람 매니저 통합 모듈

이 모듈은 알람 및 알림 시스템을 관리합니다:
- 다양한 알림 방법 지원 (시스템, 소리, 팝업, 트레이, 로그)
- 쿨다운 및 속도 제한
- 방해 금지 시간 관리
- 알림 기록 관리
- 싱글톤 패턴 지원
"""

# 모든 공개 API 재노출
from .models import NotificationHistory, NotificationData, RateLimiter
from .manager import AlarmManager
from .singleton import get_alarm_manager, reset_alarm_manager, configure_alarm_manager
from .validators import CooldownValidator, RateLimitValidator, QuietHoursValidator, AlarmValidator
from .notifiers import (
    BaseNotifier, SystemNotifier, SoundNotifier, PopupNotifier, 
    TrayNotifier, LogNotifier, NotifierFactory,
    NOTIFICATION_AVAILABLE, NOTIFICATION_METHOD
)

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...config.alarm_config import AlarmSettings


# 공개 API
__all__ = [
    # 메인 클래스
    'AlarmManager',
    'NotificationHistory',
    'NotificationData',
    'RateLimiter',
    
    # 싱글톤 함수
    'get_alarm_manager',
    'reset_alarm_manager',
    'configure_alarm_manager',
    
    # 검증자
    'CooldownValidator',
    'RateLimitValidator', 
    'QuietHoursValidator',
    'AlarmValidator',
    
    # 알림 발송자
    'BaseNotifier',
    'SystemNotifier',
    'SoundNotifier',
    'PopupNotifier',
    'TrayNotifier',
    'LogNotifier',
    'NotifierFactory',
    
    # 상태 정보
    'NOTIFICATION_AVAILABLE',
    'NOTIFICATION_METHOD',
    
    # 테스트 함수
    'test_alarm_manager',
]


def test_alarm_manager():
    """
    알람 매니저 테스트
    """
    import time
    
    print(f"알람 시스템 테스트 시작 (방식: {NOTIFICATION_METHOD})")
    
    manager = AlarmManager()
    
    # 테스트 알림
    if manager.test_notification():
        print("✓ 알림 테스트 성공")
    else:
        print("✗ 알림 테스트 실패")
        
    # 알람 큐 테스트
    manager.start()
    manager.add_alarm("큐 테스트", "큐 기반 알람 시스템 작동")
    time.sleep(1)
    manager.stop()
    
    print("테스트 완료")