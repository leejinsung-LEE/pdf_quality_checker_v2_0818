# src/utils/alarm_manager/validators.py
"""
알람 유효성 검사 및 제한 관리
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import deque

from ...config.alarm_config import AlarmConditionType, AlarmSettings


class CooldownValidator:
    """알람 쿨다운 검증"""
    
    def __init__(self, cooldown_seconds: int = 60):
        """
        초기화
        
        Args:
            cooldown_seconds: 쿨다운 시간 (초)
        """
        self.cooldown_seconds = cooldown_seconds
        self.last_notification_times: Dict[AlarmConditionType, datetime] = {}
        
    def check(self, condition_type: AlarmConditionType) -> bool:
        """
        쿨다운 확인
        
        Args:
            condition_type: 조건 유형
            
        Returns:
            쿨다운이 끝났으면 True
        """
        if condition_type not in self.last_notification_times:
            return True
            
        last_time = self.last_notification_times[condition_type]
        cooldown_delta = timedelta(seconds=self.cooldown_seconds)
        
        return datetime.now() - last_time > cooldown_delta
        
    def update(self, condition_type: AlarmConditionType):
        """
        마지막 알림 시간 업데이트
        
        Args:
            condition_type: 조건 유형
        """
        self.last_notification_times[condition_type] = datetime.now()
        
    def reset(self, condition_type: Optional[AlarmConditionType] = None):
        """
        쿨다운 초기화
        
        Args:
            condition_type: 조건 유형 (None이면 전체 초기화)
        """
        if condition_type:
            self.last_notification_times.pop(condition_type, None)
        else:
            self.last_notification_times.clear()
            
    def get_remaining_time(self, condition_type: AlarmConditionType) -> int:
        """
        남은 쿨다운 시간 반환
        
        Args:
            condition_type: 조건 유형
            
        Returns:
            남은 초 (쿨다운 중이 아니면 0)
        """
        if condition_type not in self.last_notification_times:
            return 0
            
        last_time = self.last_notification_times[condition_type]
        elapsed = (datetime.now() - last_time).total_seconds()
        remaining = self.cooldown_seconds - elapsed
        
        return max(0, int(remaining))


class RateLimitValidator:
    """알람 속도 제한 검증"""
    
    def __init__(self, max_per_minute: int = 10):
        """
        초기화
        
        Args:
            max_per_minute: 분당 최대 알림 수
        """
        self.max_per_minute = max_per_minute
        self.recent_notifications: deque = deque()
        
    def check(self) -> bool:
        """
        속도 제한 확인
        
        Returns:
            제한 내에 있으면 True
        """
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # 1분 이상 지난 알림 제거
        while self.recent_notifications and self.recent_notifications[0] < one_minute_ago:
            self.recent_notifications.popleft()
            
        return len(self.recent_notifications) < self.max_per_minute
        
    def update(self):
        """알림 추가"""
        self.recent_notifications.append(datetime.now())
        
    def reset(self):
        """초기화"""
        self.recent_notifications.clear()
        
    def get_count(self) -> int:
        """
        최근 1분간 알림 수 반환
        
        Returns:
            알림 수
        """
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # 1분 이상 지난 알림 제거
        while self.recent_notifications and self.recent_notifications[0] < one_minute_ago:
            self.recent_notifications.popleft()
            
        return len(self.recent_notifications)


class QuietHoursValidator:
    """방해 금지 시간 검증"""
    
    def __init__(self, 
                 enabled: bool = False,
                 start_time: str = "22:00",
                 end_time: str = "08:00"):
        """
        초기화
        
        Args:
            enabled: 방해 금지 활성화 여부
            start_time: 시작 시간 (HH:MM)
            end_time: 종료 시간 (HH:MM)
        """
        self.enabled = enabled
        self.start_time = start_time
        self.end_time = end_time
        
    def check(self) -> bool:
        """
        방해 금지 시간 확인
        
        Returns:
            알림 가능하면 True
        """
        if not self.enabled:
            return True
            
        now = datetime.now()
        current_time = now.time()
        
        # 시간 파싱
        start_hour, start_minute = map(int, self.start_time.split(':'))
        end_hour, end_minute = map(int, self.end_time.split(':'))
        
        start_time = datetime.now().replace(hour=start_hour, minute=start_minute).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_minute).time()
        
        # 자정을 넘는 경우 처리
        if start_time > end_time:
            # 예: 22:00 ~ 08:00
            # 현재 시간이 22:00 이후거나 08:00 이전이면 방해 금지
            in_quiet_hours = current_time >= start_time or current_time <= end_time
        else:
            # 예: 09:00 ~ 17:00
            # 현재 시간이 09:00 ~ 17:00 사이면 방해 금지
            in_quiet_hours = start_time <= current_time <= end_time
            
        # 방해 금지 시간이 아니면 True
        return not in_quiet_hours
        
    def update_settings(self, 
                       enabled: Optional[bool] = None,
                       start_time: Optional[str] = None,
                       end_time: Optional[str] = None):
        """
        설정 업데이트
        
        Args:
            enabled: 방해 금지 활성화 여부
            start_time: 시작 시간
            end_time: 종료 시간
        """
        if enabled is not None:
            self.enabled = enabled
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
            
    def is_in_quiet_hours(self) -> bool:
        """
        현재 방해 금지 시간인지 확인
        
        Returns:
            방해 금지 시간이면 True
        """
        return self.enabled and not self.check()
        
    def get_next_available_time(self) -> Optional[datetime]:
        """
        다음 알림 가능 시간 반환
        
        Returns:
            다음 알림 가능 시간 (방해 금지가 아니면 None)
        """
        if not self.enabled or self.check():
            return None
            
        now = datetime.now()
        end_hour, end_minute = map(int, self.end_time.split(':'))
        
        # 오늘의 종료 시간
        next_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        # 종료 시간이 이미 지났으면 내일
        if next_time <= now:
            next_time += timedelta(days=1)
            
        return next_time


class AlarmValidator:
    """통합 알람 유효성 검사"""
    
    def __init__(self, settings: AlarmSettings, 
                 logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            settings: 알람 설정
            logger: 로거
        """
        self.settings = settings
        self.logger = logger or logging.getLogger(__name__)
        
        # 각 검증자 초기화
        self.cooldown = CooldownValidator(settings.cooldown_seconds)
        self.rate_limit = RateLimitValidator(settings.max_notifications_per_minute)
        self.quiet_hours = QuietHoursValidator(
            settings.quiet_hours_enabled,
            settings.quiet_hours_start,
            settings.quiet_hours_end
        )
        
    def validate(self, condition_type: AlarmConditionType) -> tuple[bool, str]:
        """
        알람 발송 가능 여부 검증
        
        Args:
            condition_type: 조건 유형
            
        Returns:
            (가능 여부, 불가 사유)
        """
        # 전체 알람 비활성화 확인
        if not self.settings.enabled:
            return False, "알람이 비활성화되어 있습니다"
            
        # 쿨다운 확인
        if not self.cooldown.check(condition_type):
            remaining = self.cooldown.get_remaining_time(condition_type)
            return False, f"쿨다운 중입니다 (남은 시간: {remaining}초)"
            
        # 속도 제한 확인
        if not self.rate_limit.check():
            count = self.rate_limit.get_count()
            return False, f"분당 알림 수 제한 초과 ({count}/{self.settings.max_notifications_per_minute})"
            
        # 방해 금지 시간 확인
        if not self.quiet_hours.check():
            next_time = self.quiet_hours.get_next_available_time()
            if next_time:
                return False, f"방해 금지 시간입니다 (다음 가능: {next_time.strftime('%H:%M')})"
            else:
                return False, "방해 금지 시간입니다"
                
        return True, "OK"
        
    def update_after_send(self, condition_type: AlarmConditionType):
        """
        알람 발송 후 업데이트
        
        Args:
            condition_type: 조건 유형
        """
        self.cooldown.update(condition_type)
        self.rate_limit.update()
        
    def reset(self):
        """모든 검증자 초기화"""
        self.cooldown.reset()
        self.rate_limit.reset()