# src/ui/controllers/settings_controller/validator.py
"""
설정 검증 모듈

설정값의 유효성 검사, 폴더 경로 검증, 제약조건 관리 등을 담당합니다.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass

from .base import SettingsControllerBase, UserSettings


@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    def add_error(self, message: str) -> None:
        """오류 추가"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """경고 추가"""
        self.warnings.append(message)
    
    def has_issues(self) -> bool:
        """문제점 존재 여부"""
        return bool(self.errors or self.warnings)


@dataclass
class ValidationRule:
    """검증 규칙"""
    field: str
    validator: callable
    error_message: str
    warning_message: Optional[str] = None


class SettingsValidator(SettingsControllerBase):
    """설정 검증자
    
    설정값의 유효성을 검사하고 제약조건을 관리합니다.
    """
    
    def __init__(self, settings_file: Optional[Path] = None, 
                 logger: Optional[logging.Logger] = None):
        """검증자 초기화
        
        Args:
            settings_file: 설정 파일 경로
            logger: 로거 인스턴스
        """
        super().__init__(settings_file, logger)
        
        # 검증 규칙들
        self._validation_rules: List[ValidationRule] = []
        self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> None:
        """검증 규칙 설정"""
        # 테마 검증
        self._validation_rules.append(ValidationRule(
            field='theme',
            validator=lambda x: x in {'light', 'dark', 'auto'},
            error_message="테마는 'light', 'dark', 'auto' 중 하나여야 합니다"
        ))
        
        # 언어 검증
        self._validation_rules.append(ValidationRule(
            field='language',
            validator=lambda x: x in {'ko', 'en'},
            error_message="언어는 'ko', 'en' 중 하나여야 합니다"
        ))
        
        # 로그 레벨 검증
        self._validation_rules.append(ValidationRule(
            field='log_level',
            validator=lambda x: x in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'},
            error_message="로그 레벨이 유효하지 않습니다"
        ))
        
        # 동시 처리 파일 수 검증
        self._validation_rules.append(ValidationRule(
            field='max_concurrent_files',
            validator=lambda x: isinstance(x, int) and 1 <= x <= 10,
            error_message="동시 처리 파일 수는 1-10 사이의 정수여야 합니다"
        ))
        
        # 처리 타임아웃 검증
        self._validation_rules.append(ValidationRule(
            field='processing_timeout',
            validator=lambda x: isinstance(x, int) and 30 <= x <= 3600,
            error_message="처리 타임아웃은 30-3600초 사이여야 합니다"
        ))
        
        # 로그 보관 일수 검증
        self._validation_rules.append(ValidationRule(
            field='keep_log_days',
            validator=lambda x: isinstance(x, int) and 1 <= x <= 365,
            error_message="로그 보관 일수는 1-365일 사이여야 합니다"
        ))
        
        # 사이드바 너비 검증
        self._validation_rules.append(ValidationRule(
            field='sidebar_width',
            validator=lambda x: isinstance(x, int) and 200 <= x <= 500,
            error_message="사이드바 너비는 200-500px 사이여야 합니다"
        ))
        
        # 리포트 형식 검증
        self._validation_rules.append(ValidationRule(
            field='report_formats',
            validator=self._validate_report_formats,
            error_message="리포트 형식이 유효하지 않습니다"
        ))
    
    def validate_setting(self, key: str, value: Any) -> ValidationResult:
        """단일 설정 검증
        
        Args:
            key: 설정 키
            value: 검증할 값
            
        Returns:
            ValidationResult: 검증 결과
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # 타입 검증
            if not self._validate_type(key, value, result):
                return result
            
            # 규칙 기반 검증
            for rule in self._validation_rules:
                if rule.field == key:
                    if not rule.validator(value):
                        result.add_error(rule.error_message)
                        if rule.warning_message:
                            result.add_warning(rule.warning_message)
            
            # 특별 검증
            self._validate_special_cases(key, value, result)
            
        except Exception as e:
            result.add_error(f"검증 중 오류 발생: {e}")
            self.logger.error(f"설정 검증 오류: {key} = {value}, {e}")
        
        return result
    
    def validate_all_settings(self, settings: Optional[UserSettings] = None) -> ValidationResult:
        """전체 설정 검증
        
        Args:
            settings: 검증할 설정 (None이면 현재 설정)
            
        Returns:
            ValidationResult: 검증 결과
        """
        if settings is None:
            settings = self.settings
        
        result = ValidationResult(is_valid=True)
        
        try:
            settings_dict = settings.to_dict()
            
            # 각 설정 개별 검증
            for key, value in settings_dict.items():
                field_result = self.validate_setting(key, value)
                if field_result.errors:
                    result.errors.extend([f"{key}: {error}" for error in field_result.errors])
                    result.is_valid = False
                if field_result.warnings:
                    result.warnings.extend([f"{key}: {warning}" for warning in field_result.warnings])
            
            # 설정 간 관계 검증
            self._validate_setting_relationships(settings, result)
            
        except Exception as e:
            result.add_error(f"전체 설정 검증 중 오류: {e}")
            self.logger.error(f"전체 설정 검증 오류: {e}")
        
        return result
    
    def validate_folders(self, settings: Optional[UserSettings] = None) -> Dict[str, ValidationResult]:
        """폴더 설정 유효성 검사
        
        Args:
            settings: 검증할 설정 (None이면 현재 설정)
            
        Returns:
            Dict[str, ValidationResult]: 폴더별 검증 결과
        """
        if settings is None:
            settings = self.settings
        
        results = {}
        
        # 출력 폴더 검증
        results['output_folder'] = self._validate_folder_path(
            settings.default_output_folder,
            "출력 폴더",
            allow_none=True,
            create_if_missing=True
        )
        
        # 완료 폴더 검증
        results['completed_folder'] = self._validate_folder_path(
            settings.default_completed_folder,
            "완료 폴더",
            allow_none=True,
            create_if_missing=True
        )
        
        return results
    
    def validate_external_tools(self) -> Dict[str, ValidationResult]:
        """외부 도구 유효성 검사
        
        Returns:
            Dict[str, ValidationResult]: 도구별 검증 결과
        """
        results = {}
        
        try:
            from ....external import get_tool_manager
            tool_manager = get_tool_manager()
            
            tools = ['ghostscript', 'pdffonts']
            
            for tool_name in tools:
                result = ValidationResult(is_valid=True)
                
                if tool_manager.is_tool_available(tool_name):
                    tool_path = tool_manager.get_tool_path(tool_name)
                    if tool_path and Path(tool_path).exists():
                        result.add_warning(f"{tool_name} 사용 가능: {tool_path}")
                    else:
                        result.add_error(f"{tool_name} 경로가 유효하지 않음")
                else:
                    result.add_warning(f"{tool_name} 사용 불가 - 일부 기능이 제한될 수 있습니다")
                
                results[tool_name] = result
                
        except Exception as e:
            self.logger.error(f"외부 도구 검증 오류: {e}")
            for tool_name in ['ghostscript', 'pdffonts']:
                result = ValidationResult(is_valid=False)
                result.add_error(f"도구 검증 중 오류 발생: {e}")
                results[tool_name] = result
        
        return results
    
    def _validate_type(self, key: str, value: Any, result: ValidationResult) -> bool:
        """타입 검증
        
        Args:
            key: 설정 키
            value: 값
            result: 검증 결과
            
        Returns:
            bool: 타입 검증 통과 여부
        """
        type_map = {
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
        
        if key in type_map:
            expected_type = type_map[key]
            if value is not None and not isinstance(value, expected_type):
                result.add_error(f"타입 불일치: 예상={expected_type.__name__}, 실제={type(value).__name__}")
                return False
        
        return True
    
    def _validate_special_cases(self, key: str, value: Any, result: ValidationResult) -> None:
        """특별한 경우의 검증
        
        Args:
            key: 설정 키
            value: 값
            result: 검증 결과
        """
        # 폴더 경로 검증
        if key in {'default_output_folder', 'default_completed_folder'}:
            if value is not None:
                folder_result = self._validate_folder_path(value, key, allow_none=False)
                if folder_result.errors:
                    result.errors.extend(folder_result.errors)
                if folder_result.warnings:
                    result.warnings.extend(folder_result.warnings)
        
        # 윈도우 지오메트리 검증
        elif key == 'window_geometry':
            if value is not None and not self._validate_geometry_string(value):
                result.add_warning("윈도우 지오메트리 형식이 올바르지 않을 수 있습니다")
    
    def _validate_setting_relationships(self, settings: UserSettings, result: ValidationResult) -> None:
        """설정 간 관계 검증
        
        Args:
            settings: 설정 객체
            result: 검증 결과
        """
        # 파일 이동 설정과 완료 폴더 관계
        if settings.move_completed_files and not settings.default_completed_folder:
            result.add_warning("파일 이동이 활성화되었지만 완료 폴더가 설정되지 않았습니다")
        
        # 알림 설정 관계
        if settings.notification_sound and not settings.show_notifications:
            result.add_warning("알림 소리가 활성화되었지만 알림 표시가 비활성화되었습니다")
        
        # 리포트 생성과 형식 관계
        if settings.generate_report and not settings.report_formats:
            result.add_error("리포트 생성이 활성화되었지만 리포트 형식이 지정되지 않았습니다")
    
    def _validate_folder_path(self, path: Optional[str], name: str, 
                            allow_none: bool = True, create_if_missing: bool = False) -> ValidationResult:
        """폴더 경로 검증
        
        Args:
            path: 폴더 경로
            name: 폴더 이름 (오류 메시지용)
            allow_none: None 허용 여부
            create_if_missing: 없으면 생성 여부
            
        Returns:
            ValidationResult: 검증 결과
        """
        result = ValidationResult(is_valid=True)
        
        if path is None:
            if not allow_none:
                result.add_error(f"{name} 경로가 지정되지 않았습니다")
            return result
        
        try:
            folder_path = Path(path)
            
            # 경로 형식 검증
            if not str(folder_path).strip():
                result.add_error(f"{name} 경로가 비어있습니다")
                return result
            
            # 절대 경로 권장
            if not folder_path.is_absolute():
                result.add_warning(f"{name}에 상대 경로가 사용되었습니다. 절대 경로를 권장합니다")
            
            # 존재 여부 확인
            if folder_path.exists():
                if not folder_path.is_dir():
                    result.add_error(f"{name} 경로가 디렉토리가 아닙니다: {path}")
                else:
                    # 권한 확인
                    if not os.access(folder_path, os.W_OK):
                        result.add_error(f"{name}에 대한 쓰기 권한이 없습니다: {path}")
            else:
                # 부모 디렉토리 확인
                parent = folder_path.parent
                if not parent.exists():
                    result.add_error(f"{name}의 부모 디렉토리가 존재하지 않습니다: {parent}")
                elif not os.access(parent, os.W_OK):
                    result.add_error(f"{name}의 부모 디렉토리에 쓰기 권한이 없습니다: {parent}")
                elif create_if_missing:
                    try:
                        folder_path.mkdir(parents=True, exist_ok=True)
                        result.add_warning(f"{name} 디렉토리를 생성했습니다: {path}")
                    except Exception as e:
                        result.add_error(f"{name} 디렉토리 생성 실패: {e}")
                else:
                    result.add_warning(f"{name} 디렉토리가 존재하지 않습니다: {path}")
            
        except Exception as e:
            result.add_error(f"{name} 경로 검증 중 오류: {e}")
        
        return result
    
    def _validate_report_formats(self, formats: List[str]) -> bool:
        """리포트 형식 검증
        
        Args:
            formats: 형식 목록
            
        Returns:
            bool: 유효성
        """
        if not isinstance(formats, list):
            return False
        
        valid_formats = {'html', 'pdf', 'json', 'csv'}
        return all(fmt in valid_formats for fmt in formats)
    
    def _validate_geometry_string(self, geometry: str) -> bool:
        """윈도우 지오메트리 문자열 검증
        
        Args:
            geometry: 지오메트리 문자열
            
        Returns:
            bool: 유효성
        """
        try:
            # 기본적인 형식 검증 (예: "800x600+100+50")
            import re
            pattern = r'^\d+x\d+[+-]\d+[+-]\d+$'
            return bool(re.match(pattern, geometry))
        except:
            return False
    
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
    
    def reset_settings(self, category: Optional[str] = None) -> bool:
        """설정 초기화 - 다른 모듈에서 구현"""
        return True