# src/ui/controllers/profile_controller/__init__.py
"""
프로파일 컨트롤러 모듈

모듈화된 프로파일 컨트롤러를 통합하고 외부에 ProfileController를 제공합니다.
기존 API 호환성을 유지하면서 내부 구조를 모듈화했습니다.

모듈 구조:
- base.py: 기본 클래스와 데이터 모델 (ProfileControllerBase, ProfileInfo)
- profile_manager.py: 프로파일 CRUD 작업 관리
- validator.py: 프로파일 유효성 검사 및 규칙 관리
- serializer.py: 가져오기/내보내기 기능
- event_handler.py: 이벤트 처리 및 콜백 관리
"""

from typing import Dict, List, Optional, Callable, Any, Tuple
from pathlib import Path
import logging

from .base import ProfileControllerBase, ProfileInfo
from .profile_manager import ProfileCRUDHelper
from .validator import ProfileValidator
from .serializer import ProfileSerializer
from .event_handler import ProfileEventHandler


class ProfileController(ProfileControllerBase):
    """
    프로파일 관리 컨트롤러 - 모듈화된 버전
    
    기존 API와 호환성을 유지하면서 내부를 모듈화한 프로파일 컨트롤러입니다.
    각 기능별로 모듈이 분리되어 있어 유지보수가 용이합니다.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        # 기본 클래스 초기화
        super().__init__(logger)
        
        # 모듈 초기화
        self.profile_mgr = ProfileCRUDHelper(self)
        self.validator = ProfileValidator(self)
        self.serializer = ProfileSerializer(self)
        self.event_handler = ProfileEventHandler(self)
        
        # 이벤트 콜백 연결
        self.profile_mgr.set_callbacks(
            on_created=self.event_handler.emit_profile_created,
            on_updated=self.event_handler.emit_profile_updated,
            on_deleted=self.event_handler.emit_profile_deleted
        )
    
    # === 프로파일 조회 메서드들 (ProfileManager에서 위임) ===
    
    def get_profile_list(self) -> List[ProfileInfo]:
        """프로파일 목록 조회"""
        return self.profile_mgr.get_profile_list()
    
    def get_profile(self, name: str) -> Optional[Any]:
        """특정 프로파일 조회"""
        return self.profile_mgr.get_profile(name)
    
    def get_current_profile(self) -> Tuple[str, Any]:
        """현재 프로파일 조회"""
        return self.profile_mgr.get_current_profile()
    
    def set_current_profile(self, name: str) -> bool:
        """현재 프로파일 설정"""
        result = self.profile_mgr.set_current_profile(name)
        if result:
            self.event_handler.emit_current_profile_changed(name)
        return result
    
    # === 프로파일 CRUD 메서드들 (ProfileManager에서 위임) ===
    
    def create_profile(self, 
                      name: str,
                      base_profile: Optional[str] = None,
                      description: str = "") -> bool:
        """새 프로파일 생성"""
        return self.profile_mgr.create_profile(name, base_profile, description)
    
    def update_profile(self, name: str, settings: Dict[str, Any]) -> bool:
        """프로파일 업데이트"""
        return self.profile_mgr.update_profile(name, settings)
    
    def update_profile_description(self, name: str, description: str) -> bool:
        """프로파일 설명 업데이트"""
        return self.profile_mgr.update_profile_description(name, description)
    
    def delete_profile(self, name: str) -> bool:
        """프로파일 삭제"""
        return self.profile_mgr.delete_profile(name)
    
    def duplicate_profile(self, source_name: str, new_name: str) -> bool:
        """프로파일 복제"""
        return self.profile_mgr.duplicate_profile(source_name, new_name)
    
    def reset_profile(self, name: str, base_profile: str = "default") -> bool:
        """프로파일 초기화"""
        return self.profile_mgr.reset_profile(name, base_profile)
    
    def refresh_profiles(self):
        """프로파일 목록 새로고침"""
        self.profile_mgr.refresh_profiles()
    
    def get_profile_info(self, name: str) -> Optional[Dict[str, Any]]:
        """프로파일 상세 정보 조회"""
        return self.profile_mgr.get_profile_info(name)
    
    # === 가져오기/내보내기 메서드들 (ProfileSerializer에서 위임) ===
    
    def export_profile(self, name: str, file_path: Path) -> bool:
        """프로파일 내보내기"""
        result = self.serializer.export_profile(name, file_path)
        if result:
            self.event_handler.emit_profile_exported(name)
        return result
    
    def import_profile(self, file_path: Path, new_name: Optional[str] = None) -> bool:
        """프로파일 가져오기"""
        result = self.serializer.import_profile(file_path, new_name)
        if result:
            imported_name = new_name or "imported_profile"
            self.event_handler.emit_profile_imported(imported_name)
        return result
    
    def export_multiple_profiles(self, profile_names: List[str], file_path: Path) -> bool:
        """다중 프로파일 내보내기"""
        return self.serializer.export_multiple_profiles(profile_names, file_path)
    
    def import_multiple_profiles(self, file_path: Path) -> Tuple[bool, List[str]]:
        """다중 프로파일 가져오기"""
        return self.serializer.import_multiple_profiles(file_path)
    
    # === 규칙 및 유효성 검사 메서드들 (ProfileValidator에서 위임) ===
    
    def get_available_rules(self) -> List[Dict[str, str]]:
        """사용 가능한 규칙 목록"""
        return self.validator.get_available_rules()
    
    def get_rule_categories(self) -> List[str]:
        """규칙 카테고리 목록"""
        return self.validator.get_rule_categories()
    
    def get_rules_by_category(self, category: str) -> List[Dict[str, str]]:
        """카테고리별 규칙 목록"""
        return self.validator.get_rules_by_category(category)
    
    def validate_profile_name(self, name: str) -> Tuple[bool, str]:
        """프로파일 이름 유효성 검사"""
        return self.validator.validate_profile_name(name)
    
    def validate_profile_settings(self, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """프로파일 설정 유효성 검사"""
        return self.validator.validate_profile_settings(settings)
    
    def update_rule_settings(self, 
                           profile_name: str,
                           enabled_rules: List[str],
                           rule_severities: Optional[Dict[str, str]] = None) -> bool:
        """규칙 설정 업데이트"""
        result = self.validator.update_rule_settings(profile_name, enabled_rules, rule_severities)
        if result:
            self.event_handler.emit_rules_updated(profile_name, enabled_rules)
        return result
    
    def update_quality_standards(self,
                               profile_name: str,
                               standards: Dict[str, Any]) -> bool:
        """품질 기준 업데이트"""
        result = self.validator.update_quality_standards(profile_name, standards)
        if result:
            self.event_handler.emit_quality_standards_updated(profile_name, standards)
        return result
    
    def get_profile_validation_summary(self, profile_name: str) -> Dict[str, Any]:
        """프로파일 유효성 검사 요약"""
        return self.validator.get_profile_validation_summary(profile_name)
    
    # === 이벤트 관리 메서드들 (EventHandler에서 위임) ===
    
    def set_event_callbacks(self,
                          on_created: Optional[Callable] = None,
                          on_updated: Optional[Callable] = None,
                          on_deleted: Optional[Callable] = None,
                          on_imported: Optional[Callable] = None,
                          on_exported: Optional[Callable] = None,
                          on_current_changed: Optional[Callable] = None,
                          on_rules_updated: Optional[Callable] = None,
                          on_quality_updated: Optional[Callable] = None):
        """이벤트 콜백 설정"""
        self.event_handler.set_event_callbacks(
            on_created, on_updated, on_deleted, on_imported, 
            on_exported, on_current_changed, on_rules_updated, on_quality_updated
        )
    
    def get_callback_status(self) -> Dict[str, bool]:
        """콜백 설정 상태"""
        return self.event_handler.get_callback_status()
    
    def clear_all_callbacks(self):
        """모든 콜백 제거"""
        self.event_handler.clear_all_callbacks()
    
    # === 기존 호환성을 위한 메서드들 ===
    
    # 기존 API에서 사용하던 콜백 설정 (하위 호환성)
    @property
    def on_profile_created(self):
        return self.event_handler.on_profile_created
    
    @on_profile_created.setter
    def on_profile_created(self, callback):
        self.event_handler.on_profile_created = callback
    
    @property
    def on_profile_updated(self):
        return self.event_handler.on_profile_updated
    
    @on_profile_updated.setter
    def on_profile_updated(self, callback):
        self.event_handler.on_profile_updated = callback
    
    @property
    def on_profile_deleted(self):
        return self.event_handler.on_profile_deleted
    
    @on_profile_deleted.setter
    def on_profile_deleted(self, callback):
        self.event_handler.on_profile_deleted = callback


# 전역 프로파일 컨트롤러 인스턴스
from functools import lru_cache


@lru_cache(maxsize=1)
def get_profile_controller() -> ProfileController:
    """전역 프로파일 컨트롤러 인스턴스 반환 (스레드 안전)
    
    LRU 캐시를 사용하여 싱글톤 패턴을 구현합니다.
    Python 내장 기능으로 스레드 안전성이 보장됩니다.
    
    Returns:
        ProfileController: 싱글톤 인스턴스
    """
    return ProfileController()


# 외부 사용을 위한 export
__all__ = ['ProfileController', 'ProfileInfo', 'get_profile_controller']