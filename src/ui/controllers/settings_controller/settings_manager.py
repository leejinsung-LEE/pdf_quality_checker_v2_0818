# src/ui/controllers/settings_controller/settings_manager.py
"""
설정 관리 모듈

설정값의 조회, 변경, 업데이트 등 핵심 설정 관리 기능을 담당합니다.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from pathlib import Path

from .base import SettingsControllerBase, UserSettings


class SettingsManager(SettingsControllerBase):
    """설정 관리자
    
    설정값의 조회, 변경, 업데이트 등을 담당하는 핵심 클래스입니다.
    """
    
    def __init__(self, settings_file: Optional[Path] = None, 
                 logger: Optional[logging.Logger] = None):
        """설정 관리자 초기화
        
        Args:
            settings_file: 설정 파일 경로
            logger: 로거 인스턴스
        """
        super().__init__(settings_file, logger)
        
        # 읽기 전용 설정 키들
        self._readonly_keys: Set[str] = set()
        
        # 검증 필요 설정 키들
        self._validation_required_keys: Set[str] = {
            'max_concurrent_files', 'processing_timeout', 'keep_log_days',
            'sidebar_width', 'log_level'
        }
        
        # 타입 제한 설정
        self._type_constraints: Dict[str, type] = {
            'theme': str,
            'language': str,
            'auto_start_watching': bool,
            'minimize_to_tray': bool,
            'default_profile': str,
            'auto_fix_enabled': bool,
            'move_completed_files': bool,
            'generate_report': bool,
            'report_formats': list,
            'watch_folders_on_startup': bool,
            'show_notifications': bool,
            'notification_sound': bool,
            'sidebar_width': int,
            'max_concurrent_files': int,
            'processing_timeout': int,
            'log_level': str,
            'keep_log_days': int,
            'column_visibility': dict
        }
    
    def get_settings(self) -> UserSettings:
        """전체 설정 객체 반환
        
        Returns:
            UserSettings: 현재 설정 객체
        """
        return self.settings
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정값 조회
        
        Args:
            key: 설정 키
            default: 기본값
            
        Returns:
            Any: 설정값
        """
        try:
            if hasattr(self.settings, key):
                value = getattr(self.settings, key)
                return value if value is not None else default
            else:
                self.logger.warning(f"알 수 없는 설정 키: {key}")
                return default
        except Exception as e:
            self.logger.error(f"설정 조회 실패: {key} - {e}")
            return default
    
    def get_settings_by_category(self, category: str) -> Dict[str, Any]:
        """카테고리별 설정 조회
        
        Args:
            category: 카테고리 이름
            
        Returns:
            Dict[str, Any]: 해당 카테고리의 설정들
        """
        return self.settings.get_category_fields(category)
    
    def set_setting(self, key: str, value: Any, save: bool = True) -> bool:
        """설정값 변경
        
        Args:
            key: 설정 키
            value: 설정값
            save: 파일에 저장 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 읽기 전용 검사
            if key in self._readonly_keys:
                self.logger.warning(f"읽기 전용 설정: {key}")
                return False
            
            # 설정 키 존재 여부 확인
            if not hasattr(self.settings, key):
                self.logger.error(f"존재하지 않는 설정 키: {key}")
                return False
            
            # 타입 검증
            if not self._validate_setting_type(key, value):
                return False
            
            # 값 검증
            if not self._validate_setting_value(key, value):
                return False
            
            # 현재 값과 비교
            old_value = getattr(self.settings, key, None)
            
            # 값이 동일한 경우 스킵
            if old_value == value:
                return True
            
            # 값 설정
            setattr(self.settings, key, value)
            
            # 파일 저장 (save_settings는 다른 모듈에서 구현)
            if save:
                success = self.save_settings()
                if not success:
                    # 저장 실패 시 이전 값으로 복원
                    setattr(self.settings, key, old_value)
                    return False
            
            # 변경 알림
            category = self._get_setting_category(key)
            self._notify_change(key, old_value, value, category)
            
            self.logger.debug(f"설정 변경 완료: {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 변경 실패: {key} = {value}, {e}")
            return False
    
    def update_settings(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """여러 설정 일괄 업데이트
        
        Args:
            updates: 업데이트할 설정들
            save: 파일에 저장 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 변경 사항 추적
            changes: Dict[str, tuple] = {}  # key: (old_value, new_value)
            categories_affected: Set[str] = set()
            
            # 모든 변경사항 검증 먼저 수행
            for key, value in updates.items():
                if key in self._readonly_keys:
                    self.logger.warning(f"읽기 전용 설정 무시: {key}")
                    continue
                
                if not hasattr(self.settings, key):
                    self.logger.warning(f"존재하지 않는 설정 키 무시: {key}")
                    continue
                
                if not self._validate_setting_type(key, value):
                    self.logger.error(f"타입 검증 실패: {key}")
                    return False
                
                if not self._validate_setting_value(key, value):
                    self.logger.error(f"값 검증 실패: {key}")
                    return False
                
                old_value = getattr(self.settings, key, None)
                if old_value != value:
                    changes[key] = (old_value, value)
                    category = self._get_setting_category(key)
                    if category:
                        categories_affected.add(category)
            
            # 실제 변경사항이 없는 경우
            if not changes:
                return True
            
            # 변경사항 적용
            for key, (old_value, new_value) in changes.items():
                setattr(self.settings, key, new_value)
            
            # 파일 저장
            if save:
                success = self.save_settings()
                if not success:
                    # 저장 실패 시 모든 변경사항 복원
                    for key, (old_value, new_value) in changes.items():
                        setattr(self.settings, key, old_value)
                    return False
            
            # 변경 알림
            for key, (old_value, new_value) in changes.items():
                category = self._get_setting_category(key)
                self._notify_change(key, old_value, new_value, category)
            
            self.logger.info(f"설정 일괄 업데이트 완료: {len(changes)}개 항목")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 일괄 업데이트 실패: {e}")
            return False
    
    def has_unsaved_changes(self) -> bool:
        """저장되지 않은 변경사항 확인
        
        Returns:
            bool: 저장되지 않은 변경사항 존재 여부
        """
        try:
            # 파일에서 설정 로드해서 비교
            if not self.settings_file.exists():
                return True
            
            import json
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            current_data = self.settings.to_dict()
            
            # last_saved 키는 비교에서 제외
            file_data.pop('last_saved', None)
            current_data.pop('last_saved', None)
            
            return file_data != current_data
            
        except Exception as e:
            self.logger.error(f"변경사항 확인 실패: {e}")
            return True
    
    def get_readonly_keys(self) -> Set[str]:
        """읽기 전용 키 목록 반환
        
        Returns:
            Set[str]: 읽기 전용 키들
        """
        return self._readonly_keys.copy()
    
    def set_readonly_key(self, key: str, readonly: bool = True) -> None:
        """키의 읽기 전용 상태 설정
        
        Args:
            key: 설정 키
            readonly: 읽기 전용 여부
        """
        if readonly:
            self._readonly_keys.add(key)
        else:
            self._readonly_keys.discard(key)
    
    def _validate_setting_type(self, key: str, value: Any) -> bool:
        """설정 타입 검증
        
        Args:
            key: 설정 키
            value: 검증할 값
            
        Returns:
            bool: 검증 성공 여부
        """
        if key not in self._type_constraints:
            return True
        
        expected_type = self._type_constraints[key]
        
        # None 값은 Optional 필드에서 허용
        if value is None:
            optional_keys = {'default_output_folder', 'default_completed_folder', 
                           'window_geometry', 'alarm_settings'}
            return key in optional_keys
        
        if not isinstance(value, expected_type):
            self.logger.error(f"타입 불일치: {key} 예상={expected_type.__name__}, 실제={type(value).__name__}")
            return False
        
        return True
    
    def _validate_setting_value(self, key: str, value: Any) -> bool:
        """설정값 검증
        
        Args:
            key: 설정 키
            value: 검증할 값
            
        Returns:
            bool: 검증 성공 여부
        """
        try:
            # 특정 키별 검증 로직
            if key == 'theme':
                valid_themes = {'light', 'dark', 'auto'}
                if value not in valid_themes:
                    self.logger.error(f"유효하지 않은 테마: {value}")
                    return False
            
            elif key == 'language':
                valid_languages = {'ko', 'en'}
                if value not in valid_languages:
                    self.logger.error(f"유효하지 않은 언어: {value}")
                    return False
            
            elif key == 'log_level':
                valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
                if value not in valid_levels:
                    self.logger.error(f"유효하지 않은 로그 레벨: {value}")
                    return False
            
            elif key == 'max_concurrent_files':
                if not (1 <= value <= 10):
                    self.logger.error(f"동시 처리 파일 수는 1-10 사이여야 함: {value}")
                    return False
            
            elif key == 'processing_timeout':
                if not (30 <= value <= 3600):
                    self.logger.error(f"처리 타임아웃은 30-3600초 사이여야 함: {value}")
                    return False
            
            elif key == 'keep_log_days':
                if not (1 <= value <= 365):
                    self.logger.error(f"로그 보관 일수는 1-365일 사이여야 함: {value}")
                    return False
            
            elif key == 'sidebar_width':
                if not (200 <= value <= 500):
                    self.logger.error(f"사이드바 너비는 200-500px 사이여야 함: {value}")
                    return False
            
            elif key == 'report_formats':
                valid_formats = {'html', 'pdf', 'json', 'csv'}
                if not all(fmt in valid_formats for fmt in value):
                    self.logger.error(f"유효하지 않은 리포트 형식: {value}")
                    return False
            
            elif key in {'default_output_folder', 'default_completed_folder'}:
                if value is not None:
                    path = Path(value)
                    # 존재하지 않는 경로여도 생성 가능한지 확인
                    if not path.parent.exists():
                        self.logger.error(f"유효하지 않은 폴더 경로: {value}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"설정값 검증 중 오류: {key} = {value}, {e}")
            return False
    
    # 추상 메서드 임시 구현 (다른 모듈에서 오버라이드)
    def load_settings(self) -> bool:
        """설정 로드 - 다른 모듈에서 구현"""
        return True
    
    def save_settings(self) -> bool:
        """설정 저장 - 다른 모듈에서 구현"""
        return True
    
    def reset_settings(self, category: Optional[str] = None) -> bool:
        """설정 초기화 - 다른 모듈에서 구현"""
        return True