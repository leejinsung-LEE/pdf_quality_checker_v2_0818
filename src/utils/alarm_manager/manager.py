# src/utils/alarm_manager/manager.py
"""
메인 알람 매니저 클래스
"""

import logging
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Optional, Any, Callable, Dict

from ...config.alarm_config import (
    AlarmSettings, AlarmCondition, AlarmConditionType,
    AlarmLevel, NotificationMethod, SoundSettings
)
from .models import NotificationHistory, NotificationData
from .notifiers import NotifierFactory
from .validators import AlarmValidator


class AlarmManager:
    """개선된 알람 매니저"""
    
    def __init__(self, 
                 settings: Optional[AlarmSettings] = None,
                 logger: Optional[logging.Logger] = None,
                 test_mode: bool = False):
        """
        알람 매니저 초기화
        
        Args:
            settings: 알람 설정
            logger: 로거
            test_mode: 테스트 모드 (간단한 초기화)
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 테스트용 큐 시스템
        self.alarm_queue = queue.Queue()
        self.alarm_thread = None
        self.is_running = False
        
        if test_mode:
            # 테스트 모드: 최소한의 초기화만
            self.settings = None
            self.history = None
            self.validator = None
            self.notifiers = {}
            self.sound_dir = Path("data/sounds")
            return
            
        # 정상 모드: 전체 초기화
        self.settings = settings or AlarmSettings()
        
        # 알림 기록
        self.history = NotificationHistory(self.settings.max_history_items)
        
        # 유효성 검사
        self.validator = AlarmValidator(self.settings, self.logger)
        
        # 알림 발송자들 초기화
        self._init_notifiers()
        
        # 콜백 함수들
        self.on_notification: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_tray_update: Optional[Callable[[str, str], None]] = None
        
        # 사운드 파일 경로
        self.sound_dir = Path("data/sounds")
        self.sound_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("알람 매니저 초기화 완료")
        
    def _init_notifiers(self):
        """알림 발송자 초기화"""
        self.notifiers = {}
        
        # 시스템 알림
        self.notifiers['system'] = NotifierFactory.create_notifier(
            'system', logger=self.logger
        )
        
        # 소리 알림
        self.notifiers['sound'] = NotifierFactory.create_notifier(
            'sound', sound_dir=self.sound_dir, logger=self.logger
        )
        
        # 팝업 알림
        self.notifiers['popup'] = NotifierFactory.create_notifier(
            'popup', logger=self.logger
        )
        
        # 트레이 알림
        self.notifiers['tray'] = NotifierFactory.create_notifier(
            'tray', on_tray_update=self.on_tray_update, logger=self.logger
        )
        
        # 로그 알림
        self.notifiers['log'] = NotifierFactory.create_notifier(
            'log', logger=self.logger
        )
        
    def check_and_notify(self, 
                        condition_type: AlarmConditionType, 
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
        if not self.settings or not self.settings.enabled:
            return False
            
        # 조건 확인
        condition = self.settings.get_condition(condition_type)
        if not condition or not condition.enabled:
            return False
            
        # 임계값 확인
        if not condition.should_trigger(value):
            return False
            
        # 유효성 검사
        is_valid, reason = self.validator.validate(condition_type)
        if not is_valid:
            self.logger.debug(f"알람 발송 불가: {reason}")
            return False
            
        # 알림 데이터 준비
        title = title or f"PDF Quality Checker - {condition_type.value}"
        message = message or condition.custom_message or self._get_default_message(condition_type, value)
        
        notification_data = NotificationData(
            condition_type=condition_type.value,
            title=title,
            message=message,
            value=value,
            severity=self._get_severity(condition_type)
        )
        
        # 알림 방법별로 발송
        success = False
        for method in condition.notification_methods:
            if self._send_notification(method, notification_data):
                success = True
                
        if success:
            # 기록 저장
            self.history.add(notification_data.to_dict())
            
            # 검증자 업데이트
            self.validator.update_after_send(condition_type)
            
            # 콜백 호출
            if self.on_notification:
                self.on_notification(notification_data.to_dict())
                
        return success
        
    def _send_notification(self, 
                          method: NotificationMethod, 
                          data: NotificationData) -> bool:
        """
        알림 발송
        
        Args:
            method: 알림 방법
            data: 알림 데이터
            
        Returns:
            성공 여부
        """
        try:
            if method == NotificationMethod.SYSTEM_NOTIFICATION:
                notifier = self.notifiers.get('system')
                if notifier:
                    return notifier.send(data.title, data.message)
                    
            elif method == NotificationMethod.SOUND:
                notifier = self.notifiers.get('sound')
                if notifier:
                    condition_type = AlarmConditionType(data.condition_type)
                    sound_file = self.settings.sound_settings.get_sound_file(condition_type)
                    volume = self.settings.sound_settings.volume
                    return notifier.send(
                        data.title, 
                        data.message,
                        sound_file=sound_file,
                        volume=volume,
                        condition_type=condition_type
                    )
                    
            elif method == NotificationMethod.POPUP:
                notifier = self.notifiers.get('popup')
                if notifier:
                    return notifier.send(data.title, data.message)
                    
            elif method == NotificationMethod.TRAY:
                notifier = self.notifiers.get('tray')
                if notifier:
                    return notifier.send(data.title, data.message)
                    
            elif method == NotificationMethod.LOG:
                notifier = self.notifiers.get('log')
                if notifier:
                    level = 'error' if data.severity == 'critical' else data.severity
                    return notifier.send(data.title, data.message, level=level)
                    
        except Exception as e:
            self.logger.error(f"알림 발송 실패 ({method.value}): {e}")
            
        return False
        
    def _get_default_message(self, 
                           condition_type: AlarmConditionType, 
                           value: Any) -> str:
        """
        기본 메시지 생성
        
        Args:
            condition_type: 조건 유형
            value: 관련 값
            
        Returns:
            기본 메시지
        """
        messages = {
            AlarmConditionType.ERROR_LEVEL: f"오류 레벨이 높습니다: {value}",
            AlarmConditionType.LOW_DPI: f"이미지 해상도가 낮습니다: {value} DPI",
            AlarmConditionType.INK_COVERAGE: f"잉크 커버리지가 높습니다: {value}%",
            AlarmConditionType.FONT_ISSUE: "폰트 문제가 발견되었습니다",
            AlarmConditionType.PROCESSING_COMPLETE: "처리가 완료되었습니다",
            AlarmConditionType.PROCESSING_FAILED: "처리가 실패했습니다",
            AlarmConditionType.BATCH_COMPLETE: "배치 처리가 완료되었습니다",
            AlarmConditionType.FOLDER_WATCH_START: "폴더 감시가 시작되었습니다",
            AlarmConditionType.NEW_FILE_DETECTED: "새 파일이 감지되었습니다"
        }
        return messages.get(condition_type, "알림")
        
    def _get_severity(self, condition_type: AlarmConditionType) -> str:
        """
        심각도 결정
        
        Args:
            condition_type: 조건 유형
            
        Returns:
            심각도 문자열
        """
        critical_types = [
            AlarmConditionType.ERROR_LEVEL,
            AlarmConditionType.PROCESSING_FAILED
        ]
        warning_types = [
            AlarmConditionType.LOW_DPI,
            AlarmConditionType.INK_COVERAGE,
            AlarmConditionType.FONT_ISSUE
        ]
        
        if condition_type in critical_types:
            return 'critical'
        elif condition_type in warning_types:
            return 'warning'
        else:
            return 'info'
            
    def test_notification(self) -> bool:
        """알림 테스트"""
        try:
            notifier = self.notifiers.get('system')
            if notifier:
                from .notifiers import NOTIFICATION_METHOD
                return notifier.send(
                    "테스트 알림",
                    f"알림 시스템이 정상 작동합니다.\n방식: {NOTIFICATION_METHOD}"
                )
            return False
        except Exception as e:
            self.logger.error(f"알림 테스트 실패: {e}")
            return False
            
    def show_notification(self, title: str, message: str):
        """
        알림 표시 (테스트용)
        
        Args:
            title: 제목
            message: 메시지
        """
        notifier = self.notifiers.get('system')
        if notifier:
            notifier.send(title, message)
            
    def add_alarm(self, title: str, message: str):
        """
        알람 큐에 추가
        
        Args:
            title: 제목
            message: 메시지
        """
        self.alarm_queue.put({'title': title, 'message': message})
        
    def start(self):
        """알람 처리 스레드 시작"""
        if not self.is_running:
            self.is_running = True
            self.alarm_thread = threading.Thread(target=self._process_alarms, daemon=True)
            self.alarm_thread.start()
            self.logger.info("알람 처리 스레드 시작")
            
    def stop(self):
        """알람 처리 스레드 중지"""
        self.is_running = False
        if self.alarm_thread:
            self.alarm_thread.join(timeout=1)
            self.logger.info("알람 처리 스레드 중지")
            
    def _process_alarms(self):
        """알람 큐 처리"""
        while self.is_running:
            try:
                if not self.alarm_queue.empty():
                    alarm = self.alarm_queue.get(timeout=0.1)
                    self.show_notification(alarm['title'], alarm['message'])
                time.sleep(0.1)
            except queue.Empty:
                pass
            except Exception as e:
                self.logger.error(f"알람 처리 중 오류: {e}")
                
    def get_statistics(self) -> Dict[str, Any]:
        """
        알람 통계 반환
        
        Returns:
            통계 딕셔너리
        """
        if self.history:
            return self.history.get_statistics()
        return {
            'total': 0,
            'by_type': {},
            'recent_hour': 0,
            'recent_day': 0
        }
        
    def save_history(self, filepath: Path):
        """
        알림 기록 저장
        
        Args:
            filepath: 저장할 파일 경로
        """
        if self.history:
            self.history.save_to_file(filepath)
            
    def load_history(self, filepath: Path):
        """
        알림 기록 로드
        
        Args:
            filepath: 로드할 파일 경로
        """
        if self.history:
            self.history.load_from_file(filepath)