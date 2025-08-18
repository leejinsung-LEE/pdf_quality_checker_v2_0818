# src/core/profiles/profile_manager/io_handler.py
"""
프로파일 파일 입출력 처리
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import QualityProfile


class ProfileIOHandler:
    """프로파일 파일 입출력 처리기"""
    
    def __init__(self, profiles_dir: Path):
        """
        초기화
        
        Args:
            profiles_dir: 프로파일 저장 디렉토리
        """
        self.profiles_dir = profiles_dir
        self.profiles_file = profiles_dir / "quality_profiles.json"
        self._ensure_profiles_dir()
    
    def _ensure_profiles_dir(self):
        """프로파일 디렉토리 확인/생성"""
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
    
    def load_json_profiles(self) -> Dict[str, QualityProfile]:
        """개별 JSON 프로파일 파일 로드"""
        profiles = {}
        
        json_profiles = list(self.profiles_dir.glob("*.json"))
        for profile_path in json_profiles:
            # quality_profiles.json은 프로파일이 아니라 설정 파일이므로 제외
            if profile_path.name == 'quality_profiles.json':
                continue
            
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    
                    # name 필드가 없으면 파일명에서 추출
                    if 'name' not in profile_data:
                        profile_data['name'] = profile_path.stem
                    
                    # JSON 파일에서 로드한 프로파일 추가
                    profile = QualityProfile(
                        name=profile_data['name'],
                        data=profile_data,
                        is_builtin=profile_data.get('is_builtin', False)
                    )
                    profiles[profile.name] = profile
                    
            except Exception as e:
                # Failed to load profile {profile_path.name}: {e}
                pass
        
        return profiles
    
    def load_user_profiles(self) -> tuple[Dict[str, QualityProfile], Optional[str]]:
        """
        사용자 프로파일 로드 (구버전 호환)
        
        Returns:
            (프로파일 딕셔너리, 현재 프로파일 이름)
        """
        profiles = {}
        current_profile = None
        
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 사용자 프로파일 로드
                    for profile_data in data.get('user_profiles', []):
                        profile = QualityProfile(
                            name=profile_data['name'],
                            data=profile_data.get('settings', profile_data),
                            is_builtin=False
                        )
                        if profile.validate():
                            profiles[profile.name] = profile
                    
                    # 마지막 사용 프로파일
                    current_profile = data.get('current_profile', 'default')
                    
            except Exception as e:
                # Failed to load user profiles: {e}
                pass
        
        return profiles, current_profile
    
    def save_profiles(self, profiles: Dict[str, QualityProfile], 
                     current_profile_name: Optional[str]) -> bool:
        """
        프로파일 저장
        
        Args:
            profiles: 프로파일 딕셔너리
            current_profile_name: 현재 프로파일 이름
            
        Returns:
            성공 여부
        """
        data = {
            'current_profile': current_profile_name,
            'user_profiles': []
        }
        
        # 사용자 프로파일만 저장
        for profile in profiles.values():
            if not profile.is_builtin:
                data['user_profiles'].append(profile.to_dict())
        
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            # Failed to save profiles: {e}
            return False
    
    def export_profile(self, profile: QualityProfile, file_path: Path) -> bool:
        """
        프로파일 내보내기
        
        Args:
            profile: 내보낼 프로파일
            file_path: 저장할 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            export_data = profile.to_dict()
            export_data['exported_at'] = datetime.now().isoformat()
            export_data['version'] = '2.0'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            # 프로파일 내보내기 오류: {e}
            return False
    
    def import_profile(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        프로파일 가져오기
        
        Args:
            file_path: 가져올 파일 경로
            
        Returns:
            프로파일 데이터 또는 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 설정 데이터 추출
            profile_data = data.get('settings', data)
            
            # 메타데이터 복사
            if 'name' in data:
                profile_data['name'] = data['name']
            if 'description' in data:
                profile_data['description'] = data['description']
            if 'parent_profile' in data:
                profile_data['parent_profile'] = data['parent_profile']
                
            return profile_data
            
        except Exception as e:
            # 프로파일 가져오기 오류: {e}
            return None
    
    def save_profile_to_file(self, profile: QualityProfile) -> bool:
        """
        프로파일을 개별 파일로 저장
        
        Args:
            profile: 저장할 프로파일
            
        Returns:
            성공 여부
        """
        try:
            file_path = self.profiles_dir / f"{profile.name}.json"
            return self.export_profile(profile, file_path)
        except Exception:
            return False
    
    def delete_profile_file(self, profile_name: str) -> bool:
        """
        프로파일 파일 삭제
        
        Args:
            profile_name: 삭제할 프로파일 이름
            
        Returns:
            성공 여부
        """
        try:
            file_path = self.profiles_dir / f"{profile_name}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception:
            return False