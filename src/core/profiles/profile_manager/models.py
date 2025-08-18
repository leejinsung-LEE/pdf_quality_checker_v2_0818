# src/core/profiles/profile_manager/models.py
"""
프로파일 데이터 모델
"""

from typing import Dict, Any, Optional, Set
from datetime import datetime

from ...checkers import CheckerContext
from ...models.quality_issue import IssueSeverity


class QualityProfile:
    """품질 검사 프로파일"""
    
    def __init__(self, name: str, data: Dict[str, Any], is_builtin: bool = False):
        """
        프로파일 초기화
        
        Args:
            name: 프로파일 이름
            data: 프로파일 데이터
            is_builtin: 기본 제공 프로파일 여부
        """
        self.name = name
        self.data = data
        self.is_builtin = is_builtin
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.modified_at = data.get('modified_at', datetime.now().isoformat())
        self.parent_profile = data.get('parent_profile')  # 상속 기능
    
    def to_dict(self) -> Dict[str, Any]:
        """프로파일을 딕셔너리로 변환"""
        return {
            'name': self.name,
            'is_builtin': self.is_builtin,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'parent_profile': self.parent_profile,
            'settings': self.data
        }
    
    def to_checker_context(self) -> CheckerContext:
        """프로파일을 CheckerContext로 변환"""
        context = CheckerContext(profile_name=self.name)
        
        # 품질 기준을 프로파일 설정으로 변환
        if 'quality_standards' in self.data:
            context.profile_settings.update(self.data['quality_standards'])
        
        # 검사 옵션
        if 'check_options' in self.data:
            context.profile_settings.update(self.data['check_options'])
        
        # 색상 설정
        if 'color_settings' in self.data:
            context.profile_settings.update(self.data['color_settings'])
        
        # 활성화된 규칙 설정
        if 'enabled_rules' in self.data and self.data['enabled_rules'] is not None:
            context.enabled_rules = set(self.data['enabled_rules'])
        else:
            # enabled_rules가 None이거나 없으면 빈 세트로 초기화
            context.enabled_rules = set()
        
        # 규칙별 심각도 설정
        if 'rule_severities' in self.data:
            for rule_name, severity_str in self.data['rule_severities'].items():
                try:
                    context.rule_severities[rule_name] = IssueSeverity(severity_str)
                except ValueError:
                    # Unknown severity: {severity_str}
                    pass
        
        return context
    
    def get_description(self) -> str:
        """프로파일 설명 반환"""
        return self.data.get('description', '')
    
    # Property accessors for backward compatibility
    @property
    def quality_standards(self) -> Dict[str, Any]:
        """품질 기준 속성 접근자"""
        return self.data.get('quality_standards', {})
    
    @property
    def check_options(self) -> Dict[str, Any]:
        """검사 옵션 속성 접근자"""
        return self.data.get('check_options', {})
    
    @property
    def description(self) -> str:
        """설명 속성 접근자"""
        return self.data.get('description', '')
    
    def validate(self) -> bool:
        """프로파일 유효성 검사"""
        required_fields = ['quality_standards', 'check_options']
        for field in required_fields:
            if field not in self.data:
                return False
        return True
    
    def export(self, file_path) -> bool:
        """
        프로파일을 파일로 내보내기
        
        Args:
            file_path: 저장할 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        import json
        try:
            export_data = self.to_dict()
            export_data['exported_at'] = datetime.now().isoformat()
            export_data['version'] = '2.0'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"프로파일 내보내기 실패: {e}")
            return False
    
    def update_settings(self, settings: Dict[str, Any]):
        """
        프로파일 설정 업데이트
        
        Args:
            settings: 새로운 설정
        """
        self.data = settings
        self.modified_at = datetime.now().isoformat()
    
    def clone(self, new_name: str) -> 'QualityProfile':
        """
        프로파일 복제
        
        Args:
            new_name: 새 프로파일 이름
            
        Returns:
            복제된 프로파일
        """
        import copy
        cloned_data = copy.deepcopy(self.data)
        cloned_data['created_at'] = datetime.now().isoformat()
        cloned_data['modified_at'] = datetime.now().isoformat()
        cloned_data['parent_profile'] = self.name
        
        return QualityProfile(new_name, cloned_data, is_builtin=False)


class ProfileMetadata:
    """프로파일 메타데이터"""
    
    def __init__(self, 
                 name: str,
                 is_builtin: bool = False,
                 is_current: bool = False,
                 description: str = "",
                 parent_profile: Optional[str] = None,
                 created_at: Optional[str] = None,
                 modified_at: Optional[str] = None):
        """
        메타데이터 초기화
        
        Args:
            name: 프로파일 이름
            is_builtin: 기본 제공 여부
            is_current: 현재 프로파일 여부
            description: 설명
            parent_profile: 부모 프로파일
            created_at: 생성 시간
            modified_at: 수정 시간
        """
        self.name = name
        self.is_builtin = is_builtin
        self.is_current = is_current
        self.description = description
        self.parent_profile = parent_profile
        self.created_at = created_at or datetime.now().isoformat()
        self.modified_at = modified_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'name': self.name,
            'is_builtin': self.is_builtin,
            'is_current': self.is_current,
            'description': self.description,
            'parent_profile': self.parent_profile,
            'created': self.created_at,
            'modified': self.modified_at
        }