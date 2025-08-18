# src/core/profiles/profile_manager/crud_operations.py
"""
프로파일 CRUD(Create, Read, Update, Delete) 작업
"""

import copy
from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import QualityProfile, ProfileMetadata
from .builtin_profiles import BuiltinProfileProvider


class ProfileCRUD:
    """프로파일 CRUD 작업 처리"""
    
    def __init__(self, profiles: Dict[str, QualityProfile]):
        """
        초기화
        
        Args:
            profiles: 프로파일 딕셔너리
        """
        self.profiles = profiles
    
    def create_profile(self, 
                      name: str, 
                      base_profile: Optional[str] = None,
                      settings: Optional[Dict] = None) -> bool:
        """
        새 프로파일 생성
        
        Args:
            name: 프로파일 이름
            base_profile: 기반 프로파일 이름
            settings: 프로파일 설정
            
        Returns:
            성공 여부
        """
        if name in self.profiles:
            return False  # 이미 존재
        
        # 기반 프로파일 또는 빈 설정
        if settings:
            profile_data = settings
        elif base_profile and base_profile in self.profiles:
            base = self.get_profile(base_profile)
            if base:
                profile_data = copy.deepcopy(base.data)
            else:
                profile_data = BuiltinProfileProvider.get_empty_profile_template()
        else:
            profile_data = BuiltinProfileProvider.get_empty_profile_template()
        
        profile_data['parent_profile'] = base_profile
        profile_data['created_at'] = datetime.now().isoformat()
        profile_data['modified_at'] = datetime.now().isoformat()
        
        profile = QualityProfile(name, profile_data, is_builtin=False)
        self.profiles[name] = profile
        return True
    
    def get_profile(self, name: str) -> Optional[QualityProfile]:
        """
        프로파일 가져오기 (상속 처리 포함)
        
        Args:
            name: 프로파일 이름
            
        Returns:
            프로파일 또는 None
        """
        profile = self.profiles.get(name)
        if profile and profile.parent_profile:
            parent = self.profiles.get(profile.parent_profile)
            if parent:
                # 부모 프로파일의 설정을 복사하고 현재 설정으로 덮어쓰기
                merged_data = copy.deepcopy(parent.data)
                self._deep_merge(merged_data, profile.data)
                return QualityProfile(profile.name, merged_data, profile.is_builtin)
        
        return profile
    
    def update_profile(self, name: str, settings: Dict[str, Any]) -> bool:
        """
        프로파일 업데이트
        
        Args:
            name: 프로파일 이름
            settings: 새로운 설정
            
        Returns:
            성공 여부
        """
        if name not in self.profiles or self.profiles[name].is_builtin:
            return False
        
        profile = self.profiles[name]
        profile.data = settings
        profile.modified_at = datetime.now().isoformat()
        return True
    
    def delete_profile(self, name: str) -> bool:
        """
        프로파일 삭제
        
        Args:
            name: 프로파일 이름
            
        Returns:
            성공 여부
        """
        if name not in self.profiles or self.profiles[name].is_builtin:
            return False
        
        del self.profiles[name]
        return True
    
    def duplicate_profile(self, source_name: str, new_name: str) -> bool:
        """
        프로파일 복제
        
        Args:
            source_name: 원본 프로파일 이름
            new_name: 새 프로파일 이름
            
        Returns:
            성공 여부
        """
        if source_name not in self.profiles or new_name in self.profiles:
            return False
        
        source = self.get_profile(source_name)
        if not source:
            return False
        
        cloned = source.clone(new_name)
        self.profiles[new_name] = cloned
        return True
    
    def get_profile_list(self, current_profile_name: Optional[str] = None) -> List[ProfileMetadata]:
        """
        프로파일 목록 반환
        
        Args:
            current_profile_name: 현재 프로파일 이름
            
        Returns:
            프로파일 메타데이터 목록
        """
        profiles = []
        
        for name, profile in self.profiles.items():
            metadata = ProfileMetadata(
                name=name,
                is_builtin=profile.is_builtin,
                is_current=(name == current_profile_name),
                description=profile.get_description(),
                parent_profile=profile.parent_profile,
                created_at=profile.created_at,
                modified_at=profile.modified_at
            )
            profiles.append(metadata)
        
        # 기본 제공 먼저, 그 다음 사용자 프로파일
        profiles.sort(key=lambda p: (not p.is_builtin, p.name))
        
        return profiles
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """
        프로파일 이름 변경
        
        Args:
            old_name: 기존 이름
            new_name: 새 이름
            
        Returns:
            성공 여부
        """
        if old_name not in self.profiles or new_name in self.profiles:
            return False
        
        if self.profiles[old_name].is_builtin:
            return False
        
        profile = self.profiles[old_name]
        profile.name = new_name
        profile.modified_at = datetime.now().isoformat()
        
        self.profiles[new_name] = profile
        del self.profiles[old_name]
        
        return True
    
    def _deep_merge(self, base: Dict, override: Dict):
        """
        딕셔너리 깊은 병합
        
        Args:
            base: 기본 딕셔너리
            override: 덮어쓸 딕셔너리
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def validate_profile(self, name: str) -> bool:
        """
        프로파일 유효성 검사
        
        Args:
            name: 프로파일 이름
            
        Returns:
            유효 여부
        """
        profile = self.profiles.get(name)
        if not profile:
            return False
        return profile.validate()
    
    def get_profile_count(self) -> Dict[str, int]:
        """
        프로파일 개수 통계
        
        Returns:
            {'total': 전체, 'builtin': 기본제공, 'user': 사용자}
        """
        total = len(self.profiles)
        builtin = sum(1 for p in self.profiles.values() if p.is_builtin)
        user = total - builtin
        
        return {
            'total': total,
            'builtin': builtin,
            'user': user
        }