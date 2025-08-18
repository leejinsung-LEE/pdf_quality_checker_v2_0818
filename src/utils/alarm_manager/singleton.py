# src/utils/alarm_manager/singleton.py
"""
알람 매니저 싱글톤 패턴 구현
"""

from functools import lru_cache

from .manager import AlarmManager


@lru_cache(maxsize=1)
def get_alarm_manager() -> AlarmManager:
    """
    알람 매니저 싱글톤 인스턴스 반환 (스레드 안전)
    
    Returns:
        AlarmManager: 알람 매니저 인스턴스
    """
    try:
        instance = AlarmManager(test_mode=False)
        if hasattr(instance, 'start'):
            instance.start()
    except Exception:
        # 초기화 실패 시 테스트 모드로 생성
        instance = AlarmManager(test_mode=True)
    
    return instance


def reset_alarm_manager():
    """
    알람 매니저 인스턴스 리셋 (테스트용)
    """
    # 현재 인스턴스가 있다면 종료
    try:
        manager = get_alarm_manager()
        if hasattr(manager, 'stop'):
            manager.stop()
    except Exception:
        pass
    
    # 캐시 초기화
    get_alarm_manager.cache_clear()


def configure_alarm_manager(**kwargs) -> AlarmManager:
    """
    알람 매니저 설정 및 초기화
    
    Args:
        **kwargs: AlarmManager 초기화 인자들
        
    Returns:
        AlarmManager: 설정된 알람 매니저 인스턴스
    
    Note:
        @lru_cache와 함께 사용하기 위해 리셋 후 재생성하는 방식으로 동작
    """
    # 기존 인스턴스 정리
    reset_alarm_manager()
    
    # 캐시를 비운 후 새로운 설정으로 인스턴스 생성
    # 이 방법은 lru_cache와 호환되지 않으므로, 별도의 팩토리 함수 필요
    # 임시로 직접 생성하여 반환
    instance = AlarmManager(**kwargs)
    if hasattr(instance, 'start'):
        instance.start()
    
    # 캐시에 저장하기 위해 get_alarm_manager를 재정의
    # 주의: 이 방법은 권장되지 않음, 추후 리팩토링 필요
    get_alarm_manager.cache_clear()
    get_alarm_manager.cache_info  # 캐시 정보 확인용
    
    return instance