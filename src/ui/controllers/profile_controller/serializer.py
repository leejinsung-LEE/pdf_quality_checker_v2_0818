# src/ui/controllers/profile_controller/serializer.py
"""
프로파일 직렬화 및 가져오기/내보내기

프로파일의 JSON 내보내기/가져오기 기능을 담당합니다.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import json
from datetime import datetime

if TYPE_CHECKING:
    from .base import ProfileControllerBase


class ProfileSerializer:
    """프로파일 직렬화 관리 클래스"""
    
    def __init__(self, parent: 'ProfileControllerBase'):
        self.parent = parent
    
    def export_profile(self, name: str, file_path: Path) -> bool:
        """
        프로파일을 JSON 파일로 내보내기
        
        Args:
            name: 프로파일 이름
            file_path: 저장할 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            profile = self.parent.profile_manager.get_profile(name)
            if not profile:
                self.parent.logger.error(f"프로파일을 찾을 수 없습니다: {name}")
                return False
            
            # 내보낼 데이터 구성
            export_data = {
                'profile_info': {
                    'name': profile.name,
                    'description': profile.description,
                    'parent_profile': profile.parent_profile,
                    'created_at': profile.created_at,
                    'modified_at': profile.modified_at,
                    'is_builtin': profile.is_builtin,
                    'exported_at': datetime.now().isoformat(),
                    'exporter': 'PDF Quality Checker v2.0'
                },
                'profile_data': profile.data,
                'format_version': '2.0'
            }
            
            # JSON 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.parent.logger.info(f"프로파일 내보내기 완료: {name} -> {file_path}")
            return True
            
        except Exception as e:
            self.parent.logger.error(f"프로파일 내보내기 실패: {e}")
            return False
    
    def import_profile(self, file_path: Path, new_name: Optional[str] = None) -> bool:
        """
        JSON 파일에서 프로파일 가져오기
        
        Args:
            file_path: 가져올 파일 경로
            new_name: 새 프로파일 이름 (None이면 원본 이름 사용)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # JSON 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 데이터 유효성 검사
            if not self._validate_import_data(import_data):
                return False
            
            # 프로파일 정보 추출
            profile_info = import_data.get('profile_info', {})
            profile_data = import_data.get('profile_data', {})
            
            # 프로파일 이름 결정
            profile_name = new_name or profile_info.get('name', 'imported_profile')
            
            # 이름 중복 검사 및 조정
            profile_name = self._ensure_unique_name(profile_name)
            
            # 설명 업데이트
            description = profile_info.get('description', '') + ' (가져온 프로파일)'
            profile_data['description'] = description
            
            # 프로파일 생성
            if self.parent.profile_manager.create_profile(
                profile_name, 
                None,  # 기반 프로파일 없음
                description
            ):
                # 상세 설정 업데이트
                if self.parent.profile_manager.update_profile(profile_name, profile_data):
                    self.parent.logger.info(f"프로파일 가져오기 완료: {file_path} -> {profile_name}")
                    return True
                else:
                    # 생성은 되었지만 업데이트 실패 - 롤백
                    self.parent.profile_manager.delete_profile(profile_name)
            
        except json.JSONDecodeError as e:
            self.parent.logger.error(f"JSON 파싱 실패: {e}")
        except Exception as e:
            self.parent.logger.error(f"프로파일 가져오기 실패: {e}")
        
        return False
    
    def _validate_import_data(self, data: Dict[str, Any]) -> bool:
        """가져올 데이터 유효성 검사"""
        try:
            # 필수 키 확인
            if 'profile_data' not in data:
                self.parent.logger.error("프로파일 데이터가 없습니다.")
                return False
            
            # 포맷 버전 확인
            format_version = data.get('format_version', '1.0')
            if format_version not in ['1.0', '2.0']:
                self.parent.logger.warning(f"지원하지 않는 포맷 버전: {format_version}")
            
            # 프로파일 데이터 구조 확인
            profile_data = data['profile_data']
            if not isinstance(profile_data, dict):
                self.parent.logger.error("잘못된 프로파일 데이터 형식입니다.")
                return False
            
            # 필수 섹션 확인
            required_sections = ['quality_standards', 'check_options']
            for section in required_sections:
                if section not in profile_data:
                    self.parent.logger.warning(f"필수 섹션이 없습니다: {section}")
            
            return True
            
        except Exception as e:
            self.parent.logger.error(f"데이터 검증 실패: {e}")
            return False
    
    def _ensure_unique_name(self, base_name: str) -> str:
        """중복되지 않는 프로파일 이름 생성"""
        try:
            existing_profiles = self.parent.profile_manager.profiles.values()
            existing_names = {profile.name.lower() for profile in existing_profiles}
            
            # 기본 이름이 중복되지 않으면 그대로 사용
            if base_name.lower() not in existing_names:
                return base_name
            
            # 번호를 붙여서 고유한 이름 생성
            counter = 1
            while True:
                new_name = f"{base_name}_{counter}"
                if new_name.lower() not in existing_names:
                    return new_name
                counter += 1
                
                # 무한 루프 방지
                if counter > 100:
                    import uuid
                    return f"{base_name}_{str(uuid.uuid4())[:8]}"
                    
        except Exception:
            # 오류 발생 시 타임스탬프 기반 이름 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{base_name}_{timestamp}"
    
    def export_multiple_profiles(self, profile_names: list[str], file_path: Path) -> bool:
        """
        여러 프로파일을 하나의 JSON 파일로 내보내기
        
        Args:
            profile_names: 내보낼 프로파일 이름 목록
            file_path: 저장할 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            profiles_data = []
            
            for name in profile_names:
                profile = self.parent.profile_manager.get_profile(name)
                if profile:
                    profile_export = {
                        'profile_info': {
                            'name': profile.name,
                            'description': profile.description,
                            'parent_profile': profile.parent_profile,
                            'created_at': profile.created_at,
                            'modified_at': profile.modified_at,
                            'is_builtin': profile.is_builtin
                        },
                        'profile_data': profile.data
                    }
                    profiles_data.append(profile_export)
            
            if not profiles_data:
                self.parent.logger.error("내보낼 프로파일이 없습니다.")
                return False
            
            # 전체 데이터 구성
            export_data = {
                'profiles': profiles_data,
                'export_info': {
                    'exported_at': datetime.now().isoformat(),
                    'exporter': 'PDF Quality Checker v2.0',
                    'profile_count': len(profiles_data)
                },
                'format_version': '2.0'
            }
            
            # JSON 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.parent.logger.info(f"다중 프로파일 내보내기 완료: {len(profiles_data)}개 -> {file_path}")
            return True
            
        except Exception as e:
            self.parent.logger.error(f"다중 프로파일 내보내기 실패: {e}")
            return False
    
    def import_multiple_profiles(self, file_path: Path) -> tuple[bool, list[str]]:
        """
        다중 프로파일 JSON 파일에서 가져오기
        
        Args:
            file_path: 가져올 파일 경로
            
        Returns:
            tuple[bool, list[str]]: (성공 여부, 가져온 프로파일 이름 목록)
        """
        imported_names = []
        
        try:
            # JSON 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 다중 프로파일 형식인지 확인
            if 'profiles' not in import_data:
                # 단일 프로파일 형식으로 시도
                if self.import_profile(file_path):
                    return True, ['imported_profile']
                return False, []
            
            profiles = import_data['profiles']
            
            # 각 프로파일 가져오기
            for profile_data in profiles:
                profile_info = profile_data.get('profile_info', {})
                data = profile_data.get('profile_data', {})
                
                profile_name = self._ensure_unique_name(profile_info.get('name', 'imported_profile'))
                description = profile_info.get('description', '') + ' (가져온 프로파일)'
                
                # 프로파일 생성 및 설정
                if self.parent.profile_manager.create_profile(profile_name, None, description):
                    if self.parent.profile_manager.update_profile(profile_name, data):
                        imported_names.append(profile_name)
                    else:
                        # 업데이트 실패 시 롤백
                        self.parent.profile_manager.delete_profile(profile_name)
            
            if imported_names:
                self.parent.logger.info(f"다중 프로파일 가져오기 완료: {len(imported_names)}개")
                return True, imported_names
            
        except Exception as e:
            self.parent.logger.error(f"다중 프로파일 가져오기 실패: {e}")
        
        return False, imported_names