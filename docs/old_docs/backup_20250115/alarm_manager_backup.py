# -*- coding: utf-8 -*-
"""
알람 매니저

알람 조건을 확인하고 다양한 방식으로 사용자에게 알림을 제공합니다.
"""

import logging
import time
import threading
import winsound
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from collections import deque
import json

# Windows 알림을 위한 라이브러리
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from tkinter import messagebox
import customtkinter as ctk

from ..config.alarm_config import (
    AlarmSettings, AlarmCondition, AlarmConditionType,
    AlarmLevel, NotificationMethod, SoundSettings
)


class NotificationHistory:
    """알림 기록 관리"""
    
    def __init__(self, max_items: int = 1000):
        self.max_items = max_items
        self.history: deque = deque(maxlen=max_items)
        
    def add(self, notification: Dict[str, Any]):
        """알림 기록 추가"""
        notification['timestamp'] = datetime.now().isoformat()
        self.history.append(notification)
        
    def get_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """최근 알림 가져오기"""
        return list(self.history)[-count:]
        
    def clear(self):
        """기록 초기화"""
        self.history.clear()
        
    def save_to_file(self, filepath: Path):
        """파일로 저장"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(list(self.history), f, ensure_ascii=False, indent=2)


class AlarmManager:
    """알람 매니저"""
    
    def __init__(self, settings: Optional[AlarmSettings] = None,
                 logger: Optional[logging.Logger] = None):
        """
        알람 매니저 초기화
        
        Args:
            settings: 알람 설정
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        self.settings = settings or AlarmSettings()
        
        # 알림 도구 초기화
        self.toast_notifier = ToastNotifier() if TOAST_AVAILABLE else None
        
        # 소리 재생 초기화
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.sound_enabled = True
            except:
                self.sound_enabled = False
        else:
            self.sound_enabled = False
                
        # 알림 기록
        self.history = NotificationHistory(self.settings.max_history_items)
        
        # 쿨다운 관리 (조건별 마지막 알림 시간)
        self.last_notification_times: Dict[AlarmConditionType, datetime] = {}
        
        # 분당 알림 수 제한을 위한 큐
        self.recent_notifications: deque = deque()
        
        # 콜백 함수들
        self.on_notification: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_tray_update: Optional[Callable[[str, str], None]] = None
        
        # 사운드 파일 경로
        self.sound_dir = Path("data/sounds")
        self.sound_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("알람 매니저 초기화 완료")
        
    def check_and_notify(self, condition_type: AlarmConditionType, 
                        value: Any = None,
                        message: Optional[str] = None,
                        title: Optional[str] = None) -> bool:
        """
        조건을 확인하고 알림 발생
        
        Args:
            condition_type: 알람 조건 유형
            value: 확인할 값 (임계값 비교용)
            message: 알림 메시지 (None이면 기본 메시지 사용)
            title: 알림 제목 (None이면 기본 제목 사용)
            
        Returns:
            bool: 알림 발생 여부
        """
        if not self.settings.enabled:
            return False
            
        # 조건 확인
        condition = self.settings.get_condition(condition_type)
        if not condition or not condition.enabled:
            return False
            
        # 임계값 확인
        if not condition.should_trigger(value):
            return False
            
        # 쿨다운 확인
        if not self._check_cooldown(condition_type):
            self.logger.debug(f"알람 쿨다운 중: {condition_type.value}")
            return False
            
        # 분당 알림 수 제한 확인
        if not self._check_rate_limit():
            self.logger.warning("분당 알림 수 제한 초과")
            return False
            
        # 방해 금지 시간 확인
        if not self._check_quiet_hours():
            self.logger.debug("방해 금지 시간대")
            return False
            
        # 알림 발생
        notification_data = {
            'condition_type': condition_type.value,
            'value': value,
            'message': message or condition.custom_message or self._get_default_message(condition_type),
            'title': title or self._get_default_title(condition_type),
            'methods': condition.notification_methods
        }
        
        # 각 알림 방식으로 알림 발생
        for method in condition.notification_methods:
            self._send_notification(method, notification_data)
            
        # 기록 저장
        if self.settings.keep_notification_history:
            self.history.add(notification_data)
            
        # 콜백 호출
        if self.on_notification:
            self.on_notification(notification_data)
            
        # 쿨다운 및 rate limit 업데이트
        self.last_notification_times[condition_type] = datetime.now()
        self.recent_notifications.append(datetime.now())
        
        return True
        
    def _check_cooldown(self, condition_type: AlarmConditionType) -> bool:
        """쿨다운 확인"""
        if condition_type not in self.last_notification_times:
            return True
            
        last_time = self.last_notification_times[condition_type]
        cooldown_delta = timedelta(seconds=self.settings.cooldown_seconds)
        
        return datetime.now() - last_time > cooldown_delta
        
    def _check_rate_limit(self) -> bool:
        """분당 알림 수 제한 확인"""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # 1분 이상 지난 알림 제거
        while self.recent_notifications and self.recent_notifications[0] < one_minute_ago:
            self.recent_notifications.popleft()
            
        return len(self.recent_notifications) < self.settings.max_notifications_per_minute
        
    def _check_quiet_hours(self) -> bool:
        """방해 금지 시간 확인"""
        if not self.settings.quiet_hours_enabled:
            return True
            
        now = datetime.now()
        current_time = now.time()
        
        # 시간 파싱
        start_hour, start_minute = map(int, self.settings.quiet_hours_start.split(':'))
        end_hour, end_minute = map(int, self.settings.quiet_hours_end.split(':'))
        
        start_time = datetime.now().replace(hour=start_hour, minute=start_minute).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_minute).time()
        
        # 자정을 넘는 경우 처리
        if start_time > end_time:
            return current_time < start_time and current_time > end_time
        else:
            return current_time < start_time or current_time > end_time
            
    def _send_notification(self, method: NotificationMethod, data: Dict[str, Any]):
        """알림 발송"""
        try:
            if method == NotificationMethod.SYSTEM_NOTIFICATION:
                self._send_system_notification(data['title'], data['message'])
            elif method == NotificationMethod.SOUND:
                self._play_sound(AlarmConditionType(data['condition_type']))
            elif method == NotificationMethod.POPUP:
                self._show_popup(data['title'], data['message'])
            elif method == NotificationMethod.TRAY:
                self._update_tray(data['title'], data['message'])
            elif method == NotificationMethod.LOG:
                self.logger.info(f"알람: {data['title']} - {data['message']}")
        except Exception as e:
            self.logger.error(f"알림 발송 실패 ({method.value}): {e}")
            
    def _send_system_notification(self, title: str, message: str):
        """시스템 알림 발송"""
        if self.toast_notifier:
            try:
                # threaded=True로 설정하여 비차단으로 실행
                self.toast_notifier.show_toast(
                    title, 
                    message,
                    duration=10,
                    threaded=True  # 비차단 모드로 실행
                )
            except Exception as e:
                self.logger.error(f"시스템 알림 실패: {e}")
                # 실패 시 대체 방법 사용
                try:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                except:
                    pass
        else:
            # 대체 방법: Windows 기본 소리
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass
                
    def _play_sound(self, condition_type: AlarmConditionType):
        """소리 재생"""
        if not self.sound_enabled or not self.settings.sound_settings.enabled:
            return
            
        sound_file = self.settings.sound_settings.get_sound_file(condition_type)
        sound_path = self.sound_dir / sound_file
        
        # 기본 사운드 파일이 없으면 시스템 소리 사용
        if not sound_path.exists():
            try:
                # Windows 시스템 소리
                if condition_type in [AlarmConditionType.ERROR_LEVEL, 
                                     AlarmConditionType.PROCESSING_FAILED]:
                    winsound.MessageBeep(winsound.MB_ICONHAND)  # 오류 소리
                else:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)  # 경고 소리
            except:
                pass
            return
            
        # pygame으로 커스텀 소리 재생
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.load(str(sound_path))
                pygame.mixer.music.set_volume(self.settings.sound_settings.volume / 100)
                pygame.mixer.music.play()
            except Exception as e:
                self.logger.error(f"소리 재생 실패: {e}")
                
    def _show_popup(self, title: str, message: str):
        """팝업 대화상자 표시"""
        # 별도 스레드에서 실행
        thread = threading.Thread(
            target=lambda: messagebox.showinfo(title, message)
        )
        thread.daemon = True
        thread.start()
        
    def _update_tray(self, title: str, message: str):
        """시스템 트레이 업데이트"""
        if self.on_tray_update:
            self.on_tray_update(title, message)
            
    def _get_default_title(self, condition_type: AlarmConditionType) -> str:
        """기본 제목 반환"""
        titles = {
            AlarmConditionType.ERROR_LEVEL: "오류 발생",
            AlarmConditionType.LOW_DPI: "낮은 해상도",
            AlarmConditionType.FONT_ISSUE: "폰트 문제",
            AlarmConditionType.INK_COVERAGE: "잉크 커버리지 초과",
            AlarmConditionType.BLEED_ISSUE: "재단선 문제",
            AlarmConditionType.TRANSPARENCY_ISSUE: "투명도 문제",
            AlarmConditionType.OVERPRINT_ISSUE: "중복 인쇄 문제",
            AlarmConditionType.SPOT_COLOR_ISSUE: "별색 문제",
            AlarmConditionType.PROCESSING_COMPLETE: "처리 완료",
            AlarmConditionType.PROCESSING_FAILED: "처리 실패",
            AlarmConditionType.BATCH_COMPLETE: "배치 처리 완료",
            AlarmConditionType.FOLDER_WATCH_START: "폴더 감시 시작",
            AlarmConditionType.FOLDER_WATCH_STOP: "폴더 감시 중지",
            AlarmConditionType.NEW_FILE_DETECTED: "새 파일 감지"
        }
        return titles.get(condition_type, "알림")
        
    def _get_default_message(self, condition_type: AlarmConditionType) -> str:
        """기본 메시지 반환"""
        messages = {
            AlarmConditionType.ERROR_LEVEL: "PDF 파일에서 오류가 발견되었습니다.",
            AlarmConditionType.LOW_DPI: "이미지 해상도가 권장 수준보다 낮습니다.",
            AlarmConditionType.FONT_ISSUE: "임베딩되지 않은 폰트가 있습니다.",
            AlarmConditionType.INK_COVERAGE: "잉크 사용량이 인쇄 한계를 초과했습니다.",
            AlarmConditionType.BLEED_ISSUE: "재단선이 올바르게 설정되지 않았습니다.",
            AlarmConditionType.TRANSPARENCY_ISSUE: "투명 개체가 발견되었습니다.",
            AlarmConditionType.OVERPRINT_ISSUE: "중복 인쇄 설정 문제가 있습니다.",
            AlarmConditionType.SPOT_COLOR_ISSUE: "별색 사용 문제가 있습니다.",
            AlarmConditionType.PROCESSING_COMPLETE: "PDF 파일 처리가 완료되었습니다.",
            AlarmConditionType.PROCESSING_FAILED: "PDF 파일 처리 중 오류가 발생했습니다.",
            AlarmConditionType.BATCH_COMPLETE: "모든 파일 처리가 완료되었습니다.",
            AlarmConditionType.FOLDER_WATCH_START: "폴더 감시를 시작했습니다.",
            AlarmConditionType.FOLDER_WATCH_STOP: "폴더 감시를 중지했습니다.",
            AlarmConditionType.NEW_FILE_DETECTED: "새로운 PDF 파일이 감지되었습니다."
        }
        return messages.get(condition_type, "알림이 발생했습니다.")
        
    def update_settings(self, settings: AlarmSettings):
        """설정 업데이트"""
        self.settings = settings
        self.history.max_items = settings.max_history_items
        
    def get_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """알림 기록 조회"""
        return self.history.get_recent(count)
        
    def clear_history(self):
        """알림 기록 초기화"""
        self.history.clear()
        
    def save_history(self, filepath: Path):
        """알림 기록 저장"""
        self.history.save_to_file(filepath)
        
    def test_notification(self, condition_type: AlarmConditionType):
        """알림 테스트"""
        self.logger.info(f"알림 테스트: {condition_type.value}")
        
        # 임시로 쿨다운 제거
        original_cooldown = self.settings.cooldown_seconds
        self.settings.cooldown_seconds = 0
        
        # 테스트 알림 발송
        result = self.check_and_notify(
            condition_type,
            message="이것은 테스트 알림입니다.",
            title="알림 테스트"
        )
        
        # 쿨다운 복원
        self.settings.cooldown_seconds = original_cooldown
        
        return result


# 전역 알람 매니저 인스턴스
_alarm_manager: Optional[AlarmManager] = None


def get_alarm_manager() -> AlarmManager:
    """전역 알람 매니저 인스턴스 반환"""
    global _alarm_manager
    if _alarm_manager is None:
        _alarm_manager = AlarmManager()
    return _alarm_manager


def set_alarm_manager(manager: AlarmManager):
    """전역 알람 매니저 설정"""
    global _alarm_manager
    _alarm_manager = manager