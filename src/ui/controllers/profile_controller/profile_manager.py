# src/ui/controllers/profile_controller/profile_manager.py
"""
프로파일 CRUD 작업 관리

프로파일의 생성, 수정, 삭제, 복제, 가져오기/내보내기 기능을 담당합니다.
"""

from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from pathlib import Path
import json

if TYPE_CHECKING:
    from .base import ProfileControllerBase, ProfileInfo, QualityProfile


class ProfileCRUDHelper:
    """프로파일 CRUD 작업 관리 헬퍼 클래스
    
    UI 컨트롤러에서 프로파일 생성, 수정, 삭제, 복제 등의 작업을 처리합니다.
    core.profiles.ProfileManager와 구분하기 위해 ProfileCRUDHelper로 명명합니다.
    """
    
    def __init__(self, parent: 'ProfileControllerBase'):
        self.parent = parent
        
        # 이벤트 콜백
        self.on_profile_created: Optional[callable] = None
        self.on_profile_updated: Optional[callable] = None
        self.on_profile_deleted: Optional[callable] = None
    
    def get_profile_list(self) -> List['ProfileInfo']:
        """프로파일 목록 조회"""
        try:
            profiles = []
            current_name = self.parent.profile_manager.current_profile_name
            
            for profile in self.parent.profile_manager.profiles.values():
                profile_info = self.parent._create_profile_info(
                    profile, 
                    is_current=(profile.name == current_name)
                )
                profiles.append(profile_info)
            
            return profiles
            
        except Exception as e:
            self.parent.logger.error(f"프로파일 목록 조회 실패: {e}")
            return []
    
    def get_profile(self, name: str) -> Optional['QualityProfile']:
        """특정 프로파일 조회"""
        try:
            return self.parent.profile_manager.get_profile(name)
        except Exception as e:
            self.parent.logger.error(f"프로파일 조회 실패: {e}")
            return None
    
    def get_current_profile(self) -> Tuple[str, 'QualityProfile']:
        """현재 프로파일 조회"""
        try:
            current_name = self.parent.profile_manager.current_profile_name
            current_profile = self.parent.profile_manager.get_current_profile()
            return current_name, current_profile
        except Exception as e:
            self.parent.logger.error(f"현재 프로파일 조회 실패: {e}")
            return "default", self.parent.profile_manager.get_profile("default")
    
    def set_current_profile(self, name: str) -> bool:
        """현재 프로파일 설정"""
        try:
            if self.parent.profile_manager.set_current_profile(name):
                self.parent.logger.info(f"현재 프로파일 변경: {name}")
                return True
        except Exception as e:
            self.parent.logger.error(f"프로파일 설정 실패: {e}")
        return False
    
    def create_profile(self, 
                      name: str,
                      base_profile: Optional[str] = None,
                      description: str = "") -> bool:
        """
        새 프로파일 생성
        
        Args:
            name: 프로파일 이름
            base_profile: 기반 프로파일
            description: 설명
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 기본 설정 준비
            settings = None
            if base_profile:
                # 기존 프로파일 복사
                base = self.parent.profile_manager.get_profile(base_profile)
                if base:
                    settings = base.data.copy()
            
            if settings is None:
                # 기본 구조
                settings = {
                    'description': description,
                    'quality_standards': {
                        'min_image_dpi': 300,
                        'warning_image_dpi': 200,
                        'optimal_image_dpi': 300,
                        'standard_bleed_size': 3.0,
                        'min_text_size': 6.0,
                        'max_ink_coverage': 320,
                        'warning_ink_coverage': 300
                    },
                    'check_options': {
                        'check_rgb': True,
                        'check_spot': True,
                        'allow_rgb': False,
                        'allow_spot': True,
                        'spot_color_limit': 2,
                        'ink_coverage': False
                    },
                    'enabled_rules': None,
                    'rule_severities': {}
                }
            else:
                settings['description'] = description
            
            # 프로파일 생성
            if self.parent.profile_manager.create_profile(name, base_profile, settings):
                if self.on_profile_created:
                    self.on_profile_created(name)
                self.parent.logger.info(f"프로파일 생성: {name}")
                return True
                
        except Exception as e:
            self.parent.logger.error(f"프로파일 생성 실패: {e}")
        
        return False
    
    def update_profile(self, name: str, settings: Dict[str, Any]) -> bool:
        """
        프로파일 업데이트
        
        Args:
            name: 프로파일 이름
            settings: 새 설정
            
        Returns:
            bool: 성공 여부
        """
        if self.parent.profile_manager.update_profile(name, settings):
            if self.on_profile_updated:
                self.on_profile_updated(name)
            self.parent.logger.info(f"프로파일 업데이트: {name}")
            return True
        return False
    
    def update_profile_description(self, name: str, description: str) -> bool:
        """
        프로파일 설명 업데이트
        
        Args:
            name: 프로파일 이름
            description: 새 설명
            
        Returns:
            bool: 성공 여부
        """
        profile = self.parent.profile_manager.get_profile(name)
        if profile and not profile.is_builtin:
            profile.data['description'] = description
            return self.update_profile(name, profile.data)
        return False
    
    def delete_profile(self, name: str) -> bool:
        """
        프로파일 삭제
        
        Args:
            name: 프로파일 이름
            
        Returns:
            bool: 성공 여부
        """
        if self.parent.profile_manager.delete_profile(name):
            if self.on_profile_deleted:
                self.on_profile_deleted(name)
            self.parent.logger.info(f"프로파일 삭제: {name}")
            return True
        return False
    
    def duplicate_profile(self, source_name: str, new_name: str) -> bool:
        """
        프로파일 복제
        
        Args:
            source_name: 원본 프로파일 이름
            new_name: 새 프로파일 이름
            
        Returns:
            bool: 성공 여부
        """
        try:
            source_profile = self.parent.profile_manager.get_profile(source_name)
            if source_profile:
                return self.create_profile(
                    new_name, 
                    source_name, 
                    f"{source_profile.description} (복사본)"
                )
        except Exception as e:
            self.parent.logger.error(f"프로파일 복제 실패: {e}")
        return False
    
    def reset_profile(self, name: str, base_profile: str = "default") -> bool:
        """
        프로파일을 기본값으로 초기화
        
        Args:
            name: 프로파일 이름
            base_profile: 기반 프로파일
            
        Returns:
            bool: 성공 여부
        """
        try:
            profile = self.parent.profile_manager.get_profile(name)
            if profile and not profile.is_builtin:
                # 기반 프로파일의 설정으로 재설정
                base = self.parent.profile_manager.get_profile(base_profile)
                if base:
                    new_settings = base.data.copy()
                    new_settings['description'] = profile.description
                    
                    if self.update_profile(name, new_settings):
                        self.parent.logger.info(f"프로파일 초기화: {name}")
                        return True
        except Exception as e:
            self.parent.logger.error(f"프로파일 초기화 실패: {e}")
        return False
    
    def refresh_profiles(self):
        """프로파일 목록 새로고침"""
        try:
            self.parent.profile_manager.load_profiles()
            self.parent.logger.info("프로파일 목록 새로고침 완료")
        except Exception as e:
            self.parent.logger.error(f"프로파일 새로고침 실패: {e}")
    
    def get_profile_info(self, name: str) -> Optional[Dict[str, Any]]:
        """프로파일 상세 정보 조회"""
        try:
            profile = self.parent.profile_manager.get_profile(name)
            if profile:
                return {
                    'name': profile.name,
                    'description': profile.description,
                    'is_builtin': profile.is_builtin,
                    'parent_profile': profile.parent_profile,
                    'created_at': profile.created_at,
                    'modified_at': profile.modified_at,
                    'data': profile.data
                }
        except Exception as e:
            self.parent.logger.error(f"프로파일 정보 조회 실패: {e}")
        return None
    
    def set_callbacks(self, 
                     on_created: Optional[callable] = None,
                     on_updated: Optional[callable] = None,
                     on_deleted: Optional[callable] = None):
        """이벤트 콜백 설정"""
        if on_created:
            self.on_profile_created = on_created
        if on_updated:
            self.on_profile_updated = on_updated
        if on_deleted:
            self.on_profile_deleted = on_deleted