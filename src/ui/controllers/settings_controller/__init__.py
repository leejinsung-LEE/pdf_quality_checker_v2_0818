# src/ui/controllers/settings_controller/__init__.py
"""
설정 컨트롤러 통합 모듈

모든 설정 관리 기능을 통합한 완전한 SettingsController를 제공합니다.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, TYPE_CHECKING

# 모든 모듈 임포트
from .base import UserSettings, SettingsControllerBase, SettingsChangeEvent
from .settings_manager import SettingsManager
from .persistence import PersistenceManager
from .validator import SettingsValidator, ValidationResult
from .defaults import DefaultsManager
from .external_tools import ExternalToolsManager, ToolInfo

if TYPE_CHECKING:
    from ....external import ToolManager


class SettingsController(
    SettingsManager,
    PersistenceManager, 
    SettingsValidator,
    DefaultsManager,
    ExternalToolsManager
):
    """
    통합 설정 컨트롤러
    
    모든 설정 관리 기능을 통합한 완전한 설정 컨트롤러입니다.
    기존 API와 100% 호환성을 유지하면서 확장된 기능을 제공합니다.
    """
    
    def __init__(self, settings_file: Optional[Path] = None, 
                 logger: Optional[logging.Logger] = None):
        """
        통합 설정 컨트롤러 초기화
        
        Args:
            settings_file: 설정 파일 경로
            logger: 로거 인스턴스
        """
        # 로거 설정
        self.logger = logger or logging.getLogger(__name__)
        self.settings_file = settings_file or Path("user_settings.json")
        
        # 외부 도구 관리자 (ExternalToolsManager에서 필요)
        self.tool_manager = None
        self._initialize_tool_manager()
        
        # 기본 설정 초기화
        self.settings = UserSettings()
        
        # 이벤트 시스템 초기화 (SettingsControllerBase에서)
        self.on_settings_changed: Optional[Callable[[str, Any], None]] = None
        self.on_theme_changed: Optional[Callable[[str], None]] = None
        self.on_category_changed: Optional[Callable[[str, Dict[str, Any]], None]] = None
        self._change_listeners: List[Callable[[SettingsChangeEvent], None]] = []
        
        # SettingsManager 초기화
        self._readonly_keys = set()
        self._validation_required_keys = {
            'max_concurrent_files', 'processing_timeout', 'keep_log_days',
            'sidebar_width', 'log_level'
        }
        self._type_constraints = {
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
        
        # PersistenceManager 초기화
        self.backup_file = self.settings_file.with_suffix('.json.bak')
        self.emergency_backup_file = self.settings_file.with_suffix('.json.emergency')
        
        # SettingsValidator 초기화
        self._validation_rules = []
        self._setup_validation_rules()
        
        # DefaultsManager 초기화
        self._category_defaults = self._define_category_defaults()
        self._system_defaults = self._define_system_defaults()
        self._preserved_settings = {'window_geometry'}
        
        # ExternalToolsManager 초기화
        self._supported_tools = {
            'ghostscript': ToolInfo(
                name='ghostscript',
                description='PDF 최적화 및 변환을 위한 도구',
                required=False
            ),
            'pdffonts': ToolInfo(
                name='pdffonts',
                description='PDF 폰트 정보 분석을 위한 도구 (poppler 패키지)',
                required=False
            )
        }
        
        # 백업 정리 (PersistenceManager에서)
        self._cleanup_old_backups()
        
        # 설정 로드
        self.load_settings()
    
    def _initialize_tool_manager(self) -> None:
        """외부 도구 관리자 초기화"""
        try:
            from ....external import get_tool_manager
            self.tool_manager = get_tool_manager()
        except Exception as e:
            self.logger.error(f"외부 도구 관리자 초기화 실패: {e}")
            self.tool_manager = None
    
    # MRO(Method Resolution Order) 최적화를 위한 메서드 오버라이드
    
    def load_settings(self) -> bool:
        """설정 파일 로드 (PersistenceManager 우선)"""
        return PersistenceManager.load_settings(self)
    
    def save_settings(self) -> bool:
        """설정 파일 저장 (PersistenceManager 우선)"""
        return PersistenceManager.save_settings(self)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정값 조회 (SettingsManager 우선)"""
        return SettingsManager.get_setting(self, key, default)
    
    def set_setting(self, key: str, value: Any, save: bool = True) -> bool:
        """설정값 변경 (SettingsManager 우선)"""
        return SettingsManager.set_setting(self, key, value, save)
    
    def update_settings(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """설정 일괄 업데이트 (SettingsManager 우선)"""
        return SettingsManager.update_settings(self, updates, save)
    
    def reset_settings(self, category: Optional[str] = None) -> bool:
        """설정 초기화 (DefaultsManager 우선)"""
        return DefaultsManager.reset_settings(self, category)
    
    def export_settings(self, export_path: Path, include_metadata: bool = True) -> bool:
        """설정 내보내기 (PersistenceManager 우선)"""
        return PersistenceManager.export_settings(self, export_path, include_metadata)
    
    def import_settings(self, import_path: Path, create_backup: bool = True) -> bool:
        """설정 가져오기 (PersistenceManager 우선)"""
        return PersistenceManager.import_settings(self, import_path, create_backup)
    
    def validate_setting(self, key: str, value: Any) -> ValidationResult:
        """설정 검증 (SettingsValidator 사용)"""
        return SettingsValidator.validate_setting(self, key, value)
    
    def validate_all_settings(self, settings: Optional[UserSettings] = None) -> ValidationResult:
        """전체 설정 검증 (SettingsValidator 사용)"""
        return SettingsValidator.validate_all_settings(self, settings)
    
    def validate_folders(self, settings: Optional[UserSettings] = None) -> Dict[str, ValidationResult]:
        """폴더 검증 (SettingsValidator 사용)"""
        return SettingsValidator.validate_folders(self, settings)
    
    def get_external_tools_status(self) -> Dict[str, ToolInfo]:
        """외부 도구 상태 조회 (ExternalToolsManager 사용)"""
        return ExternalToolsManager.get_external_tools_status(self)
    
    def configure_external_tool(self, tool_name: str, tool_path: Path) -> bool:
        """외부 도구 설정 (ExternalToolsManager 사용)"""
        return ExternalToolsManager.configure_external_tool(self, tool_name, tool_path)
    
    # 호환성을 위한 기존 API 메서드들
    
    def get_settings(self) -> UserSettings:
        """전체 설정 객체 반환 (호환성)"""
        return SettingsManager.get_settings(self)
    
    # 추가 유틸리티 메서드들
    
    def get_settings_summary(self) -> Dict[str, Any]:
        """설정 요약 정보
        
        Returns:
            Dict[str, Any]: 설정 요약
        """
        try:
            summary = {
                'file_path': str(self.settings_file),
                'file_exists': self.settings_file.exists(),
                'has_unsaved_changes': self.has_unsaved_changes(),
                'validation_status': self.validate_all_settings(),
                'external_tools': {},
                'categories': {}
            }
            
            # 외부 도구 상태
            tools_status = self.get_external_tools_status()
            for tool_name, tool_info in tools_status.items():
                summary['external_tools'][tool_name] = {
                    'available': tool_info.available,
                    'version': tool_info.version,
                    'status': tool_info.status_message
                }
            
            # 카테고리별 정보
            categories = ['general', 'ui', 'processing', 'folders']
            for category in categories:
                summary['categories'][category] = self.get_settings_by_category(category)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"설정 요약 생성 실패: {e}")
            return {'error': str(e)}
    
    def perform_health_check(self) -> Dict[str, Any]:
        """설정 시스템 상태 점검
        
        Returns:
            Dict[str, Any]: 상태 점검 결과
        """
        try:
            health = {
                'overall_status': 'healthy',
                'issues': [],
                'warnings': [],
                'recommendations': []
            }
            
            # 설정 검증
            validation = self.validate_all_settings()
            if validation.errors:
                health['overall_status'] = 'error'
                health['issues'].extend(validation.errors)
            if validation.warnings:
                health['warnings'].extend(validation.warnings)
            
            # 폴더 검증
            folder_validation = self.validate_folders()
            for folder, result in folder_validation.items():
                if result.errors:
                    health['overall_status'] = 'error'
                    health['issues'].extend([f"{folder}: {err}" for err in result.errors])
                if result.warnings:
                    health['warnings'].extend([f"{folder}: {warn}" for warn in result.warnings])
            
            # 외부 도구 검증
            tools_validation = self.validate_external_tools()
            for tool, result in tools_validation.items():
                if result.errors:
                    health['warnings'].extend([f"{tool}: {err}" for err in result.errors])
                if result.warnings:
                    health['warnings'].extend([f"{tool}: {warn}" for warn in result.warnings])
            
            # 권장사항
            if not self.settings.generate_report:
                health['recommendations'].append("리포트 생성을 활성화하는 것을 권장합니다")
            
            if self.settings.move_completed_files and not self.settings.default_completed_folder:
                health['recommendations'].append("완료된 파일 이동을 위해 완료 폴더를 설정하세요")
            
            # 전체 상태 결정
            if health['issues']:
                health['overall_status'] = 'error'
            elif health['warnings']:
                health['overall_status'] = 'warning'
            
            return health
            
        except Exception as e:
            self.logger.error(f"상태 점검 실패: {e}")
            return {
                'overall_status': 'error',
                'issues': [f"상태 점검 중 오류 발생: {e}"],
                'warnings': [],
                'recommendations': []
            }
    
    def create_backup_with_metadata(self) -> bool:
        """메타데이터 포함 백업 생성
        
        Returns:
            bool: 백업 성공 여부
        """
        try:
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.settings_file.with_suffix(f'.{timestamp}.backup')
            
            return self.export_settings(backup_path, include_metadata=True)
            
        except Exception as e:
            self.logger.error(f"메타데이터 백업 생성 실패: {e}")
            return False


# 전역 설정 컨트롤러 인스턴스
from functools import lru_cache


@lru_cache(maxsize=1)
def get_settings_controller() -> SettingsController:
    """
    전역 설정 컨트롤러 인스턴스 반환 (스레드 안전)
    
    LRU 캐시를 사용하여 싱글톤 패턴을 구현합니다.
    Python 내장 기능으로 스레드 안전성이 보장됩니다.
    
    Returns:
        SettingsController: 싱글톤 인스턴스
    """
    return SettingsController()


def reset_settings_controller() -> None:
    """전역 설정 컨트롤러 인스턴스 리셋"""
    get_settings_controller.cache_clear()


# 호환성을 위한 익스포트
__all__ = [
    'SettingsController',
    'UserSettings',
    'SettingsChangeEvent',
    'ValidationResult',
    'ToolInfo',
    'get_settings_controller',
    'reset_settings_controller'
]