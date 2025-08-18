# src/ui/controllers/settings_controller/base.py
"""
설정 컨트롤러 기본 클래스 및 데이터 모델

이 모듈은 설정 관리 시스템의 핵심 데이터 구조와 기본 클래스를 정의합니다.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ....config.alarm_config import AlarmSettings


@dataclass
class UserSettings:
    """사용자 설정 데이터 모델
    
    애플리케이션의 모든 사용자 설정을 포함하는 중앙 데이터 모델입니다.
    """
    # 일반 설정
    theme: str = "dark"
    language: str = "ko"
    auto_start_watching: bool = False
    minimize_to_tray: bool = False
    
    # 처리 설정
    default_profile: str = "default"
    auto_fix_enabled: bool = False
    move_completed_files: bool = False
    generate_report: bool = True
    report_formats: List[str] = field(default_factory=lambda: ['html'])
    
    # 폴더 설정
    default_output_folder: Optional[str] = None
    default_completed_folder: Optional[str] = None
    watch_folders_on_startup: bool = True
    
    # UI 설정
    show_notifications: bool = True
    notification_sound: bool = True
    window_geometry: Optional[str] = None
    sidebar_width: int = 250
    
    # 고급 설정
    max_concurrent_files: int = 3
    processing_timeout: int = 300  # 초
    log_level: str = "INFO"
    keep_log_days: int = 30
    
    # 열 표시 설정
    column_visibility: Dict[str, bool] = field(default_factory=lambda: {
        'icon': True,
        'filename': True,
        'folder': True,
        'pagesize': True,
        'pages': True,
        'issues': True,
        'time': True,
        'report': True
    })
    
    # 알람 설정
    alarm_settings: Optional['AlarmSettings'] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        if self.alarm_settings is None:
            from ....config.alarm_config import AlarmSettings
            self.alarm_settings = AlarmSettings()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환
        
        Returns:
            Dict[str, Any]: 설정 딕셔너리
        """
        return {
            'theme': self.theme,
            'language': self.language,
            'auto_start_watching': self.auto_start_watching,
            'minimize_to_tray': self.minimize_to_tray,
            'default_profile': self.default_profile,
            'auto_fix_enabled': self.auto_fix_enabled,
            'move_completed_files': self.move_completed_files,
            'generate_report': self.generate_report,
            'report_formats': self.report_formats,
            'default_output_folder': self.default_output_folder,
            'default_completed_folder': self.default_completed_folder,
            'watch_folders_on_startup': self.watch_folders_on_startup,
            'show_notifications': self.show_notifications,
            'notification_sound': self.notification_sound,
            'window_geometry': self.window_geometry,
            'sidebar_width': self.sidebar_width,
            'max_concurrent_files': self.max_concurrent_files,
            'processing_timeout': self.processing_timeout,
            'log_level': self.log_level,
            'keep_log_days': self.keep_log_days,
            'column_visibility': self.column_visibility,
            'alarm_settings': self.alarm_settings.to_dict() if self.alarm_settings else {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        """딕셔너리에서 생성
        
        Args:
            data: 설정 딕셔너리
            
        Returns:
            UserSettings: 설정 객체
        """
        settings = cls()
        
        # bool 타입 필드 목록 (타입 변환이 필요한 필드들)
        bool_fields = {
            'auto_start_watching', 'minimize_to_tray', 'auto_fix_enabled',
            'move_completed_files', 'generate_report', 'watch_folders_on_startup',
            'show_notifications', 'notification_sound', 'check_fonts', 'allow_rgb',
            'allow_spot', 'check_transparency', 'check_overprint', 'check_ink_coverage',
            'log_to_file', 'verbose_logging'
        }
        
        # int 타입 필드 목록
        int_fields = {
            'sidebar_width', 'max_concurrent_files', 'processing_timeout',
            'file_check_interval', 'log_retention_days'
        }
        
        # 각 필드 업데이트
        for key, value in data.items():
            if key == 'alarm_settings':
                # 알람 설정은 별도 처리
                from ....config.alarm_config import AlarmSettings
                settings.alarm_settings = AlarmSettings.from_dict(value)
            elif hasattr(settings, key):
                # 타입 변환 적용
                if key in bool_fields:
                    # bool 타입 변환: 1/0, "true"/"false", True/False 모두 처리
                    if isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        value = bool(value)
                elif key in int_fields and value is not None:
                    # int 타입 변환
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        continue  # 변환 실패 시 건너뛰기
                
                setattr(settings, key, value)
        
        return settings
    
    def copy(self) -> 'UserSettings':
        """설정 복사본 생성
        
        Returns:
            UserSettings: 복사된 설정 객체
        """
        return UserSettings.from_dict(self.to_dict())
    
    def get_category_fields(self, category: str) -> Dict[str, Any]:
        """카테고리별 필드 조회
        
        Args:
            category: 카테고리 이름
            
        Returns:
            Dict[str, Any]: 해당 카테고리의 필드들
        """
        if category == 'ui':
            return {
                'theme': self.theme,
                'window_geometry': self.window_geometry,
                'sidebar_width': self.sidebar_width,
                'column_visibility': self.column_visibility,
                'show_notifications': self.show_notifications,
                'notification_sound': self.notification_sound
            }
        elif category == 'processing':
            return {
                'default_profile': self.default_profile,
                'auto_fix_enabled': self.auto_fix_enabled,
                'move_completed_files': self.move_completed_files,
                'generate_report': self.generate_report,
                'report_formats': self.report_formats,
                'max_concurrent_files': self.max_concurrent_files,
                'processing_timeout': self.processing_timeout
            }
        elif category == 'folders':
            return {
                'default_output_folder': self.default_output_folder,
                'default_completed_folder': self.default_completed_folder,
                'watch_folders_on_startup': self.watch_folders_on_startup
            }
        elif category == 'general':
            return {
                'language': self.language,
                'auto_start_watching': self.auto_start_watching,
                'minimize_to_tray': self.minimize_to_tray,
                'log_level': self.log_level,
                'keep_log_days': self.keep_log_days
            }
        else:
            return {}


@dataclass
class SettingsChangeEvent:
    """설정 변경 이벤트"""
    key: str
    old_value: Any
    new_value: Any
    category: Optional[str] = None


class SettingsControllerBase(ABC):
    """설정 컨트롤러 기본 클래스
    
    모든 설정 관리 기능의 기본 인터페이스를 정의합니다.
    """
    
    def __init__(self, settings_file: Optional[Path] = None, 
                 logger: Optional[logging.Logger] = None):
        """기본 초기화
        
        Args:
            settings_file: 설정 파일 경로
            logger: 로거 인스턴스
        """
        self.logger = logger or logging.getLogger(__name__)
        self.settings_file = settings_file or Path("user_settings.json")
        self.settings = UserSettings()
        
        # 이벤트 콜백들
        self.on_settings_changed: Optional[Callable[[str, Any], None]] = None
        self.on_theme_changed: Optional[Callable[[str], None]] = None
        self.on_category_changed: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
        # 변경 이벤트 리스너들
        self._change_listeners: List[Callable[[SettingsChangeEvent], None]] = []
    
    def add_change_listener(self, listener: Callable[[SettingsChangeEvent], None]) -> None:
        """설정 변경 리스너 추가
        
        Args:
            listener: 변경 이벤트 콜백
        """
        if listener not in self._change_listeners:
            self._change_listeners.append(listener)
    
    def remove_change_listener(self, listener: Callable[[SettingsChangeEvent], None]) -> None:
        """설정 변경 리스너 제거
        
        Args:
            listener: 제거할 콜백
        """
        if listener in self._change_listeners:
            self._change_listeners.remove(listener)
    
    def _notify_change(self, key: str, old_value: Any, new_value: Any, category: Optional[str] = None) -> None:
        """설정 변경 알림
        
        Args:
            key: 변경된 설정 키
            old_value: 이전 값
            new_value: 새로운 값
            category: 설정 카테고리
        """
        event = SettingsChangeEvent(key, old_value, new_value, category)
        
        # 리스너들에게 알림
        for listener in self._change_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"설정 변경 리스너 오류: {e}")
        
        # 기존 콜백들 호출
        if self.on_settings_changed:
            try:
                self.on_settings_changed(key, new_value)
            except Exception as e:
                self.logger.error(f"설정 변경 콜백 오류: {e}")
        
        # 테마 변경 특별 처리
        if key == 'theme' and self.on_theme_changed:
            try:
                self.on_theme_changed(new_value)
            except Exception as e:
                self.logger.error(f"테마 변경 콜백 오류: {e}")
        
        # 카테고리 변경 알림
        if category and self.on_category_changed:
            try:
                category_fields = self.settings.get_category_fields(category)
                self.on_category_changed(category, category_fields)
            except Exception as e:
                self.logger.error(f"카테고리 변경 콜백 오류: {e}")
    
    def _get_setting_category(self, key: str) -> Optional[str]:
        """설정 키에 따른 카테고리 결정
        
        Args:
            key: 설정 키
            
        Returns:
            Optional[str]: 카테고리 이름
        """
        ui_keys = {'theme', 'window_geometry', 'sidebar_width', 'column_visibility', 
                   'show_notifications', 'notification_sound'}
        processing_keys = {'default_profile', 'auto_fix_enabled', 'move_completed_files',
                          'generate_report', 'report_formats', 'max_concurrent_files', 
                          'processing_timeout'}
        folder_keys = {'default_output_folder', 'default_completed_folder', 
                      'watch_folders_on_startup'}
        general_keys = {'language', 'auto_start_watching', 'minimize_to_tray',
                       'log_level', 'keep_log_days'}
        
        if key in ui_keys:
            return 'ui'
        elif key in processing_keys:
            return 'processing'
        elif key in folder_keys:
            return 'folders'
        elif key in general_keys:
            return 'general'
        else:
            return None
    
    # 추상 메서드들
    @abstractmethod
    def load_settings(self) -> bool:
        """설정 파일 로드"""
        pass
    
    @abstractmethod
    def save_settings(self) -> bool:
        """설정 파일 저장"""
        pass
    
    @abstractmethod
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정값 조회"""
        pass
    
    @abstractmethod
    def set_setting(self, key: str, value: Any, save: bool = True) -> bool:
        """설정값 변경"""
        pass
    
    @abstractmethod
    def reset_settings(self, category: Optional[str] = None) -> bool:
        """설정 초기화"""
        pass