# src/ui/controllers/settings_controller/defaults.py
"""
기본값 관리 모듈

설정의 기본값 정의, 초기화, 리셋 등을 담당합니다.
"""

import logging
from typing import Dict, Any, Optional, Set, List
from pathlib import Path
from copy import deepcopy

from .base import SettingsControllerBase, UserSettings


class DefaultsManager(SettingsControllerBase):
    """기본값 관리자
    
    설정의 기본값을 관리하고 초기화 기능을 제공합니다.
    """
    
    def __init__(self, settings_file: Optional[Path] = None, 
                 logger: Optional[logging.Logger] = None):
        """기본값 관리자 초기화
        
        Args:
            settings_file: 설정 파일 경로
            logger: 로거 인스턴스
        """
        super().__init__(settings_file, logger)
        
        # 카테고리별 기본값 정의
        self._category_defaults = self._define_category_defaults()
        
        # 시스템별 기본값 (OS에 따라 다를 수 있음)
        self._system_defaults = self._define_system_defaults()
        
        # 보존할 설정 (리셋 시에도 유지)
        self._preserved_settings: Set[str] = {
            'window_geometry',  # 창 위치/크기는 사용자가 설정한 것 유지
        }
    
    def _define_category_defaults(self) -> Dict[str, Dict[str, Any]]:
        """카테고리별 기본값 정의
        
        Returns:
            Dict[str, Dict[str, Any]]: 카테고리별 기본값
        """
        return {
            'general': {
                'language': 'ko',
                'auto_start_watching': False,
                'minimize_to_tray': False,
                'log_level': 'INFO',
                'keep_log_days': 30
            },
            'ui': {
                'theme': 'dark',
                'show_notifications': True,
                'notification_sound': True,
                'window_geometry': None,
                'sidebar_width': 250,
                'column_visibility': {
                    'icon': True,
                    'filename': True,
                    'folder': True,
                    'pagesize': True,
                    'pages': True,
                    'issues': True,
                    'time': True,
                    'report': True
                }
            },
            'processing': {
                'default_profile': 'default',
                'auto_fix_enabled': False,
                'move_completed_files': False,
                'generate_report': True,
                'report_formats': ['html'],
                'max_concurrent_files': 3,
                'processing_timeout': 300
            },
            'folders': {
                'default_output_folder': None,
                'default_completed_folder': None,
                'watch_folders_on_startup': True
            },
            'advanced': {
                'alarm_settings': None  # AlarmSettings 객체로 초기화됨
            }
        }
    
    def _define_system_defaults(self) -> Dict[str, Any]:
        """시스템별 기본값 정의
        
        Returns:
            Dict[str, Any]: 시스템별 기본값
        """
        import platform
        system = platform.system().lower()
        
        defaults = {}
        
        # OS별 기본 테마
        if system == 'darwin':  # macOS
            defaults['theme'] = 'auto'
        elif system == 'windows':
            defaults['theme'] = 'dark'
        else:  # Linux 등
            defaults['theme'] = 'dark'
        
        # OS별 기본 폴더
        home = Path.home()
        if system == 'windows':
            defaults['default_output_folder'] = str(home / 'Documents' / 'PDF_Output')
            defaults['default_completed_folder'] = str(home / 'Documents' / 'PDF_Completed')
        else:
            defaults['default_output_folder'] = str(home / 'pdf_output')
            defaults['default_completed_folder'] = str(home / 'pdf_completed')
        
        return defaults
    
    def get_default_settings(self, use_system_defaults: bool = True) -> UserSettings:
        """기본 설정 객체 생성
        
        Args:
            use_system_defaults: 시스템별 기본값 사용 여부
            
        Returns:
            UserSettings: 기본 설정 객체
        """
        # 표준 기본값으로 시작
        settings = UserSettings()
        
        # 시스템별 기본값 적용
        if use_system_defaults:
            for key, value in self._system_defaults.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
        
        return settings
    
    def get_category_defaults(self, category: str) -> Dict[str, Any]:
        """카테고리별 기본값 조회
        
        Args:
            category: 카테고리 이름
            
        Returns:
            Dict[str, Any]: 해당 카테고리의 기본값들
        """
        return self._category_defaults.get(category, {}).copy()
    
    def reset_settings(self, category: Optional[str] = None, 
                      preserve_user_data: bool = True) -> bool:
        """설정 초기화
        
        Args:
            category: 초기화할 카테고리 (None이면 전체)
            preserve_user_data: 사용자 데이터 보존 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            if category is None:
                return self._reset_all_settings(preserve_user_data)
            else:
                return self._reset_category_settings(category, preserve_user_data)
                
        except Exception as e:
            self.logger.error(f"설정 초기화 실패: {e}")
            return False
    
    def _reset_all_settings(self, preserve_user_data: bool) -> bool:
        """전체 설정 초기화
        
        Args:
            preserve_user_data: 사용자 데이터 보존 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 보존할 데이터 백업
            preserved_data = {}
            if preserve_user_data:
                for key in self._preserved_settings:
                    if hasattr(self.settings, key):
                        preserved_data[key] = getattr(self.settings, key)
            
            # 새 기본 설정 생성
            self.settings = self.get_default_settings()
            
            # 보존 데이터 복원
            for key, value in preserved_data.items():
                if value is not None:
                    setattr(self.settings, key, value)
            
            # 저장
            if self.save_settings():
                self.logger.info("전체 설정이 기본값으로 초기화됨")
                
                # 전체 변경 알림
                self._notify_reset_complete('all')
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"전체 설정 초기화 실패: {e}")
            return False
    
    def _reset_category_settings(self, category: str, preserve_user_data: bool) -> bool:
        """카테고리별 설정 초기화
        
        Args:
            category: 카테고리 이름
            preserve_user_data: 사용자 데이터 보존 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            if category not in self._category_defaults:
                self.logger.error(f"알 수 없는 카테고리: {category}")
                return False
            
            # 카테고리 기본값 가져오기
            defaults = self.get_category_defaults(category)
            
            # 변경 사항 추적
            changes = {}
            
            # 설정 적용
            for key, default_value in defaults.items():
                if hasattr(self.settings, key):
                    # 보존 설정 확인
                    if preserve_user_data and key in self._preserved_settings:
                        current_value = getattr(self.settings, key)
                        if current_value is not None:
                            continue
                    
                    old_value = getattr(self.settings, key)
                    
                    # 값이 다른 경우만 변경
                    if old_value != default_value:
                        setattr(self.settings, key, default_value)
                        changes[key] = (old_value, default_value)
            
            if not changes:
                self.logger.info(f"카테고리 '{category}'는 이미 기본값 상태입니다")
                return True
            
            # 저장
            if self.save_settings():
                self.logger.info(f"카테고리 '{category}' 설정이 기본값으로 초기화됨")
                
                # 변경 알림
                for key, (old_value, new_value) in changes.items():
                    self._notify_change(key, old_value, new_value, category)
                
                return True
            
            # 저장 실패 시 롤백
            for key, (old_value, new_value) in changes.items():
                setattr(self.settings, key, old_value)
            
            return False
            
        except Exception as e:
            self.logger.error(f"카테고리 '{category}' 설정 초기화 실패: {e}")
            return False
    
    def restore_defaults_for_keys(self, keys: List[str]) -> bool:
        """특정 키들을 기본값으로 복원
        
        Args:
            keys: 복원할 키 목록
            
        Returns:
            bool: 성공 여부
        """
        try:
            default_settings = self.get_default_settings()
            changes = {}
            
            for key in keys:
                if not hasattr(self.settings, key):
                    self.logger.warning(f"존재하지 않는 설정 키: {key}")
                    continue
                
                old_value = getattr(self.settings, key)
                default_value = getattr(default_settings, key)
                
                if old_value != default_value:
                    setattr(self.settings, key, default_value)
                    changes[key] = (old_value, default_value)
            
            if not changes:
                return True
            
            # 저장
            if self.save_settings():
                self.logger.info(f"{len(changes)}개 설정이 기본값으로 복원됨")
                
                # 변경 알림
                for key, (old_value, new_value) in changes.items():
                    category = self._get_setting_category(key)
                    self._notify_change(key, old_value, new_value, category)
                
                return True
            
            # 저장 실패 시 롤백
            for key, (old_value, new_value) in changes.items():
                setattr(self.settings, key, old_value)
            
            return False
            
        except Exception as e:
            self.logger.error(f"키 기본값 복원 실패: {e}")
            return False
    
    def is_default_value(self, key: str) -> bool:
        """설정이 기본값인지 확인
        
        Args:
            key: 확인할 설정 키
            
        Returns:
            bool: 기본값 여부
        """
        try:
            if not hasattr(self.settings, key):
                return False
            
            current_value = getattr(self.settings, key)
            default_settings = self.get_default_settings()
            default_value = getattr(default_settings, key)
            
            return current_value == default_value
            
        except Exception as e:
            self.logger.error(f"기본값 확인 실패: {key} - {e}")
            return False
    
    def get_non_default_settings(self) -> Dict[str, Any]:
        """기본값이 아닌 설정들 조회
        
        Returns:
            Dict[str, Any]: 기본값이 아닌 설정들
        """
        try:
            non_defaults = {}
            default_settings = self.get_default_settings()
            current_dict = self.settings.to_dict()
            default_dict = default_settings.to_dict()
            
            for key, current_value in current_dict.items():
                default_value = default_dict.get(key)
                if current_value != default_value:
                    non_defaults[key] = current_value
            
            return non_defaults
            
        except Exception as e:
            self.logger.error(f"비기본값 설정 조회 실패: {e}")
            return {}
    
    def create_reset_plan(self, category: Optional[str] = None) -> Dict[str, Any]:
        """리셋 계획 생성 (실제 리셋 전 미리보기)
        
        Args:
            category: 리셋할 카테고리
            
        Returns:
            Dict[str, Any]: 리셋 계획 정보
        """
        try:
            plan = {
                'category': category or 'all',
                'changes': {},
                'preserved': [],
                'warnings': []
            }
            
            default_settings = self.get_default_settings()
            
            if category is None:
                # 전체 리셋 계획
                current_dict = self.settings.to_dict()
                default_dict = default_settings.to_dict()
                
                for key, current_value in current_dict.items():
                    default_value = default_dict.get(key)
                    
                    if key in self._preserved_settings and current_value is not None:
                        plan['preserved'].append(key)
                    elif current_value != default_value:
                        plan['changes'][key] = {
                            'current': current_value,
                            'default': default_value
                        }
            
            else:
                # 카테고리별 리셋 계획
                if category in self._category_defaults:
                    defaults = self.get_category_defaults(category)
                    
                    for key, default_value in defaults.items():
                        if hasattr(self.settings, key):
                            current_value = getattr(self.settings, key)
                            
                            if key in self._preserved_settings and current_value is not None:
                                plan['preserved'].append(key)
                            elif current_value != default_value:
                                plan['changes'][key] = {
                                    'current': current_value,
                                    'default': default_value
                                }
                else:
                    plan['warnings'].append(f"알 수 없는 카테고리: {category}")
            
            return plan
            
        except Exception as e:
            self.logger.error(f"리셋 계획 생성 실패: {e}")
            return {'error': str(e)}
    
    def _notify_reset_complete(self, category: str) -> None:
        """리셋 완료 알림
        
        Args:
            category: 리셋된 카테고리
        """
        try:
            # 카테고리별 알림
            if self.on_category_changed and category != 'all':
                category_fields = self.settings.get_category_fields(category)
                self.on_category_changed(category, category_fields)
            
            # 전체 변경 알림 (커스텀 이벤트)
            for listener in self._change_listeners:
                try:
                    # 특별한 리셋 이벤트 생성
                    from .base import SettingsChangeEvent
                    event = SettingsChangeEvent('__reset__', None, category, category)
                    listener(event)
                except Exception as e:
                    self.logger.error(f"리셋 알림 실패: {e}")
                    
        except Exception as e:
            self.logger.error(f"리셋 완료 알림 실패: {e}")
    
    # 추상 메서드 임시 구현
    def load_settings(self) -> bool:
        """설정 로드 - 다른 모듈에서 구현"""
        return True
    
    def save_settings(self) -> bool:
        """설정 저장 - 다른 모듈에서 구현"""
        return True
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정 조회 - 다른 모듈에서 구현"""
        return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any, save: bool = True) -> bool:
        """설정 변경 - 다른 모듈에서 구현"""
        return True