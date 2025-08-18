# src/core/profiles/profile_manager/manager.py
"""
프로파일 매니저 메인 클래스
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import QualityProfile, ProfileMetadata
from .builtin_profiles import BuiltinProfileProvider
from .io_handler import ProfileIOHandler
from .crud_operations import ProfileCRUD


class ProfileManager:
    """프로파일 관리자"""
    
    def __init__(self, profiles_dir: Optional[Path] = None):
        """
        프로파일 관리자 초기화
        
        Args:
            profiles_dir: 프로파일 저장 디렉토리
        """
        self.profiles_dir = profiles_dir or Path("data/profiles")
        self.profiles: Dict[str, QualityProfile] = {}
        self.current_profile_name: Optional[str] = None
        
        # 서브 컴포넌트 초기화
        self.io_handler = ProfileIOHandler(self.profiles_dir)
        self.crud = ProfileCRUD(self.profiles)
        
        # 프로파일 로드
        self._load_profiles()
    
    def _load_profiles(self):
        """프로파일 로드"""
        # 1. 기본 제공 프로파일 로드
        self.profiles.update(BuiltinProfileProvider.create_all_builtin_profiles())
        
        # 2. 개별 JSON 프로파일 파일 로드
        json_profiles = self.io_handler.load_json_profiles()
        self.profiles.update(json_profiles)
        
        # 3. 사용자 프로파일 로드 (구버전 호환)
        user_profiles, current_profile = self.io_handler.load_user_profiles()
        for name, profile in user_profiles.items():
            if name not in self.profiles:  # 기존 프로파일 덮어쓰지 않음
                self.profiles[name] = profile
        
        # 마지막 사용 프로파일 설정
        self.current_profile_name = current_profile or 'default'
    
    def save_profiles(self):
        """프로파일 저장"""
        self.io_handler.save_profiles(self.profiles, self.current_profile_name)
    
    def get_profile(self, name: str) -> Optional[QualityProfile]:
        """
        프로파일 가져오기
        
        Args:
            name: 프로파일 이름
            
        Returns:
            프로파일 또는 None
        """
        return self.crud.get_profile(name)
    
    def get_current_profile(self) -> Optional[QualityProfile]:
        """현재 프로파일 가져오기"""
        if self.current_profile_name:
            return self.get_profile(self.current_profile_name)
        return self.get_profile('default')
    
    def set_current_profile(self, name: str) -> bool:
        """
        현재 프로파일 설정
        
        Args:
            name: 프로파일 이름
            
        Returns:
            성공 여부
        """
        if name in self.profiles:
            self.current_profile_name = name
            self.save_profiles()
            return True
        return False
    
    def create_profile(self, 
                      name: str, 
                      base_profile: Optional[str] = None,
                      settings: Optional[Dict] = None) -> bool:
        """
        새 프로파일 생성
        
        Args:
            name: 프로파일 이름
            base_profile: 기반 프로파일
            settings: 프로파일 설정
            
        Returns:
            성공 여부
        """
        success = self.crud.create_profile(name, base_profile, settings)
        if success:
            self.save_profiles()
        return success
    
    def update_profile(self, name: str, settings: Dict[str, Any]) -> bool:
        """
        프로파일 업데이트
        
        Args:
            name: 프로파일 이름
            settings: 새로운 설정
            
        Returns:
            성공 여부
        """
        success = self.crud.update_profile(name, settings)
        if success:
            self.save_profiles()
        return success
    
    def delete_profile(self, name: str) -> bool:
        """
        프로파일 삭제
        
        Args:
            name: 프로파일 이름
            
        Returns:
            성공 여부
        """
        success = self.crud.delete_profile(name)
        if success:
            # 현재 프로파일이 삭제된 경우
            if self.current_profile_name == name:
                self.current_profile_name = 'default'
            
            # 파일 삭제
            self.io_handler.delete_profile_file(name)
            self.save_profiles()
        return success
    
    def duplicate_profile(self, source_name: str, new_name: str) -> bool:
        """
        프로파일 복제
        
        Args:
            source_name: 원본 프로파일 이름
            new_name: 새 프로파일 이름
            
        Returns:
            성공 여부
        """
        success = self.crud.duplicate_profile(source_name, new_name)
        if success:
            self.save_profiles()
        return success
    
    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """
        프로파일 이름 변경
        
        Args:
            old_name: 기존 이름
            new_name: 새 이름
            
        Returns:
            성공 여부
        """
        success = self.crud.rename_profile(old_name, new_name)
        if success:
            # 현재 프로파일 이름 업데이트
            if self.current_profile_name == old_name:
                self.current_profile_name = new_name
            
            # 파일 이름 변경
            self.io_handler.delete_profile_file(old_name)
            self.save_profiles()
        return success
    
    def get_profile_list(self) -> List[Dict[str, Any]]:
        """
        프로파일 목록 반환
        
        Returns:
            프로파일 정보 목록
        """
        metadata_list = self.crud.get_profile_list(self.current_profile_name)
        return [metadata.to_dict() for metadata in metadata_list]
    
    def export_profile(self, name: str, file_path: Path) -> bool:
        """
        프로파일 내보내기
        
        Args:
            name: 프로파일 이름
            file_path: 저장할 파일 경로
            
        Returns:
            성공 여부
        """
        profile = self.get_profile(name)
        if not profile:
            return False
        
        return self.io_handler.export_profile(profile, file_path)
    
    def import_profile(self, file_path: Path, new_name: Optional[str] = None) -> bool:
        """
        프로파일 가져오기
        
        Args:
            file_path: 가져올 파일 경로
            new_name: 새 이름 (옵션)
            
        Returns:
            성공 여부
        """
        profile_data = self.io_handler.import_profile(file_path)
        if not profile_data:
            return False
        
        name = new_name or profile_data.get('name', file_path.stem)
        
        # 이름 중복 확인
        if name in self.profiles:
            name = f"{name}_imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        profile = QualityProfile(name, profile_data, is_builtin=False)
        if profile.validate():
            self.profiles[name] = profile
            self.save_profiles()
            return True
        
        return False
    
    def validate_profile(self, name: str) -> bool:
        """
        프로파일 유효성 검사
        
        Args:
            name: 프로파일 이름
            
        Returns:
            유효 여부
        """
        return self.crud.validate_profile(name)
    
    def get_profile_count(self) -> Dict[str, int]:
        """
        프로파일 개수 통계
        
        Returns:
            통계 딕셔너리
        """
        return self.crud.get_profile_count()
    
    def reset_to_defaults(self):
        """기본 설정으로 초기화"""
        # 사용자 프로파일 제거
        user_profiles = [name for name, p in self.profiles.items() if not p.is_builtin]
        for name in user_profiles:
            del self.profiles[name]
        
        # 기본 프로파일로 설정
        self.current_profile_name = 'default'
        self.save_profiles()
    
    def has_profile(self, name: str) -> bool:
        """
        프로파일 존재 여부 확인
        
        Args:
            name: 프로파일 이름
            
        Returns:
            존재 여부
        """
        return name in self.profiles
    
    def is_builtin(self, name: str) -> bool:
        """
        기본 제공 프로파일 여부 확인
        
        Args:
            name: 프로파일 이름
            
        Returns:
            기본 제공 여부
        """
        profile = self.profiles.get(name)
        return profile.is_builtin if profile else False