# -*- coding: utf-8 -*-
"""
알람 설정 데이터 모델

PDF 품질 검사 시 발생하는 다양한 이벤트에 대한 
알람 조건과 알림 방식을 정의합니다.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path


class AlarmLevel(Enum):
    """알람 수준"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationMethod(Enum):
    """알림 방식"""
    SYSTEM_NOTIFICATION = "system"  # Windows Toast 알림
    SOUND = "sound"  # 소리 알림
    POPUP = "popup"  # 팝업 대화상자
    TRAY = "tray"  # 시스템 트레이 알림
    LOG = "log"  # 로그 기록만


class AlarmConditionType(Enum):
    """알람 조건 유형"""
    # 오류 수준별
    ERROR_LEVEL = "error_level"
    
    # 문제 유형별
    LOW_DPI = "low_dpi"
    FONT_ISSUE = "font_issue"
    INK_COVERAGE = "ink_coverage"
    BLEED_ISSUE = "bleed_issue"
    TRANSPARENCY_ISSUE = "transparency"
    OVERPRINT_ISSUE = "overprint"
    SPOT_COLOR_ISSUE = "spot_color"
    
    # 처리 상태별
    PROCESSING_COMPLETE = "processing_complete"
    PROCESSING_FAILED = "processing_failed"
    BATCH_COMPLETE = "batch_complete"
    
    # 폴더 감시
    FOLDER_WATCH_START = "folder_watch_start"
    FOLDER_WATCH_STOP = "folder_watch_stop"
    NEW_FILE_DETECTED = "new_file_detected"


@dataclass
class AlarmCondition:
    """알람 조건 설정"""
    condition_type: AlarmConditionType
    enabled: bool = True
    threshold_value: Optional[Any] = None  # 조건별 임계값
    notification_methods: List[NotificationMethod] = field(default_factory=lambda: [NotificationMethod.SYSTEM_NOTIFICATION])
    custom_message: Optional[str] = None  # 커스텀 메시지
    
    def should_trigger(self, value: Any = None) -> bool:
        """알람 트리거 여부 확인"""
        if not self.enabled:
            return False
            
        if self.threshold_value is not None and value is not None:
            # 임계값 비교 (조건 유형에 따라 다르게 처리)
            if self.condition_type == AlarmConditionType.LOW_DPI:
                return value < self.threshold_value
            elif self.condition_type == AlarmConditionType.INK_COVERAGE:
                return value > self.threshold_value
                
        return True


@dataclass
class SoundSettings:
    """소리 알림 설정"""
    enabled: bool = True
    volume: int = 50  # 0-100
    default_sound: str = "default.wav"
    custom_sounds: Dict[AlarmConditionType, str] = field(default_factory=dict)
    
    def get_sound_file(self, condition_type: AlarmConditionType) -> str:
        """조건별 소리 파일 반환"""
        return self.custom_sounds.get(condition_type, self.default_sound)


@dataclass
class AlarmSettings:
    """전체 알람 설정"""
    # 알람 활성화
    enabled: bool = True
    
    # 조건별 설정
    conditions: Dict[AlarmConditionType, AlarmCondition] = field(default_factory=dict)
    
    # 전역 알림 방식
    default_notification_methods: List[NotificationMethod] = field(
        default_factory=lambda: [NotificationMethod.SYSTEM_NOTIFICATION]
    )
    
    # 소리 설정
    sound_settings: SoundSettings = field(default_factory=SoundSettings)
    
    # 알림 제한
    cooldown_seconds: int = 60  # 동일 알람 재발생 방지 시간
    max_notifications_per_minute: int = 10  # 분당 최대 알림 수
    quiet_hours_enabled: bool = False  # 방해 금지 시간대
    quiet_hours_start: str = "22:00"  # 시작 시간
    quiet_hours_end: str = "07:00"  # 종료 시간
    
    # 알림 기록
    keep_notification_history: bool = True
    max_history_items: int = 1000
    
    def __post_init__(self):
        """초기화 후 기본 조건 설정"""
        if not self.conditions:
            self._setup_default_conditions()
    
    def _setup_default_conditions(self):
        """기본 알람 조건 설정"""
        # 오류 수준별 기본 설정
        self.conditions[AlarmConditionType.ERROR_LEVEL] = AlarmCondition(
            condition_type=AlarmConditionType.ERROR_LEVEL,
            enabled=True,
            threshold_value=AlarmLevel.ERROR,
            notification_methods=[NotificationMethod.SYSTEM_NOTIFICATION, NotificationMethod.SOUND]
        )
        
        # DPI 부족 알람
        self.conditions[AlarmConditionType.LOW_DPI] = AlarmCondition(
            condition_type=AlarmConditionType.LOW_DPI,
            enabled=True,
            threshold_value=300,  # 300 DPI 미만
            notification_methods=[NotificationMethod.SYSTEM_NOTIFICATION],
            custom_message="이미지 해상도가 인쇄 품질 기준에 미달합니다."
        )
        
        # 잉크 커버리지 초과
        self.conditions[AlarmConditionType.INK_COVERAGE] = AlarmCondition(
            condition_type=AlarmConditionType.INK_COVERAGE,
            enabled=True,
            threshold_value=320,  # 320% 초과
            notification_methods=[NotificationMethod.SYSTEM_NOTIFICATION],
            custom_message="잉크 커버리지가 인쇄 한계를 초과했습니다."
        )
        
        # 폰트 문제
        self.conditions[AlarmConditionType.FONT_ISSUE] = AlarmCondition(
            condition_type=AlarmConditionType.FONT_ISSUE,
            enabled=True,
            notification_methods=[NotificationMethod.SYSTEM_NOTIFICATION],
            custom_message="임베딩되지 않은 폰트가 발견되었습니다."
        )
        
        # 처리 완료
        self.conditions[AlarmConditionType.PROCESSING_COMPLETE] = AlarmCondition(
            condition_type=AlarmConditionType.PROCESSING_COMPLETE,
            enabled=True,
            notification_methods=[NotificationMethod.SYSTEM_NOTIFICATION]
        )
        
        # 처리 실패
        self.conditions[AlarmConditionType.PROCESSING_FAILED] = AlarmCondition(
            condition_type=AlarmConditionType.PROCESSING_FAILED,
            enabled=True,
            notification_methods=[NotificationMethod.SYSTEM_NOTIFICATION, NotificationMethod.SOUND]
        )
        
        # 배치 완료
        self.conditions[AlarmConditionType.BATCH_COMPLETE] = AlarmCondition(
            condition_type=AlarmConditionType.BATCH_COMPLETE,
            enabled=True,
            notification_methods=[NotificationMethod.SYSTEM_NOTIFICATION]
        )
        
        # 폴더 감시 시작
        self.conditions[AlarmConditionType.FOLDER_WATCH_START] = AlarmCondition(
            condition_type=AlarmConditionType.FOLDER_WATCH_START,
            enabled=False,  # 기본적으로 비활성화
            notification_methods=[NotificationMethod.TRAY]
        )
        
        # 새 파일 감지
        self.conditions[AlarmConditionType.NEW_FILE_DETECTED] = AlarmCondition(
            condition_type=AlarmConditionType.NEW_FILE_DETECTED,
            enabled=False,  # 기본적으로 비활성화
            notification_methods=[NotificationMethod.LOG]
        )
    
    def get_condition(self, condition_type: AlarmConditionType) -> Optional[AlarmCondition]:
        """특정 조건 설정 반환"""
        return self.conditions.get(condition_type)
    
    def set_condition(self, condition_type: AlarmConditionType, condition: AlarmCondition):
        """조건 설정 업데이트"""
        self.conditions[condition_type] = condition
    
    def is_condition_enabled(self, condition_type: AlarmConditionType) -> bool:
        """특정 조건 활성화 여부"""
        condition = self.get_condition(condition_type)
        return condition.enabled if condition else False
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'enabled': self.enabled,
            'conditions': {
                ct.value: {
                    'enabled': c.enabled,
                    'threshold_value': c.threshold_value,
                    'notification_methods': [m.value for m in c.notification_methods],
                    'custom_message': c.custom_message
                }
                for ct, c in self.conditions.items()
            },
            'default_notification_methods': [m.value for m in self.default_notification_methods],
            'sound_settings': {
                'enabled': self.sound_settings.enabled,
                'volume': self.sound_settings.volume,
                'default_sound': self.sound_settings.default_sound,
                'custom_sounds': {ct.value: sf for ct, sf in self.sound_settings.custom_sounds.items()}
            },
            'cooldown_seconds': self.cooldown_seconds,
            'max_notifications_per_minute': self.max_notifications_per_minute,
            'quiet_hours_enabled': self.quiet_hours_enabled,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
            'keep_notification_history': self.keep_notification_history,
            'max_history_items': self.max_history_items
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlarmSettings':
        """딕셔너리에서 생성"""
        settings = cls()
        
        # 기본 설정
        settings.enabled = data.get('enabled', True)
        settings.cooldown_seconds = data.get('cooldown_seconds', 60)
        settings.max_notifications_per_minute = data.get('max_notifications_per_minute', 10)
        settings.quiet_hours_enabled = data.get('quiet_hours_enabled', False)
        settings.quiet_hours_start = data.get('quiet_hours_start', "22:00")
        settings.quiet_hours_end = data.get('quiet_hours_end', "07:00")
        settings.keep_notification_history = data.get('keep_notification_history', True)
        settings.max_history_items = data.get('max_history_items', 1000)
        
        # 기본 알림 방식
        if 'default_notification_methods' in data:
            settings.default_notification_methods = [
                NotificationMethod(m) for m in data['default_notification_methods']
            ]
        
        # 소리 설정
        if 'sound_settings' in data:
            sound_data = data['sound_settings']
            settings.sound_settings = SoundSettings(
                enabled=sound_data.get('enabled', True),
                volume=sound_data.get('volume', 50),
                default_sound=sound_data.get('default_sound', 'default.wav'),
                custom_sounds={
                    AlarmConditionType(k): v 
                    for k, v in sound_data.get('custom_sounds', {}).items()
                }
            )
        
        # 조건별 설정
        if 'conditions' in data:
            for condition_type_str, condition_data in data['conditions'].items():
                try:
                    condition_type = AlarmConditionType(condition_type_str)
                    settings.conditions[condition_type] = AlarmCondition(
                        condition_type=condition_type,
                        enabled=condition_data.get('enabled', True),
                        threshold_value=condition_data.get('threshold_value'),
                        notification_methods=[
                            NotificationMethod(m) 
                            for m in condition_data.get('notification_methods', ['system'])
                        ],
                        custom_message=condition_data.get('custom_message')
                    )
                except ValueError:
                    # 알 수 없는 조건 유형은 무시
                    pass
        
        return settings