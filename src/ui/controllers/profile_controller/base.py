# src/ui/controllers/profile_controller/base.py
"""
프로파일 컨트롤러 기본 클래스

ProfileController의 핵심 구조와 데이터 모델을 정의합니다.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import logging

from ....core.profiles import ProfileManager, QualityProfile, get_profile_manager
from ....core.models.quality_issue import IssueSeverity, IssueCategory
from ....core.checkers import CheckerContext
from ....core.checkers.rule_registry import RuleRegistry


@dataclass
class ProfileInfo:
    """UI에 표시할 프로파일 정보"""
    name: str
    is_builtin: bool
    is_current: bool
    description: str
    parent_profile: Optional[str]
    created_at: str
    modified_at: str
    
    # 규칙 정보
    enabled_rules_count: int = 0
    total_rules_count: int = 14  # 전체 규칙 수
    
    # 설정 요약
    min_image_dpi: int = 300
    allow_rgb: bool = False
    allow_spot: bool = True
    check_ink_coverage: bool = False
    
    @property
    def rules_summary(self) -> str:
        """규칙 설정 요약"""
        if self.enabled_rules_count == 0:
            return "모든 규칙 비활성화"
        elif self.enabled_rules_count == self.total_rules_count:
            return "모든 규칙 활성화"
        else:
            return f"{self.enabled_rules_count}/{self.total_rules_count} 규칙 활성화"
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'name': self.name,
            'is_builtin': self.is_builtin,
            'is_current': self.is_current,
            'description': self.description,
            'parent_profile': self.parent_profile,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'rules_summary': self.rules_summary,
            'settings': {
                'min_image_dpi': self.min_image_dpi,
                'allow_rgb': self.allow_rgb,
                'allow_spot': self.allow_spot,
                'check_ink_coverage': self.check_ink_coverage
            }
        }


class ProfileControllerBase:
    """
    프로파일 관리 컨트롤러 기본 클래스
    
    v2의 ProfileManager를 UI와 연결하여 프로파일 관리 기능을 제공합니다.
    """
    
    # 사용 가능한 규칙 목록 (하드코딩)
    # 규칙 레지스트리에서 가져오기
    @property
    def AVAILABLE_RULES(self) -> List[Dict[str, str]]:
        """사용 가능한 규칙 목록 (규칙 레지스트리에서 가져옴)"""
        rules = []
        for rule in RuleRegistry.get_all_rules():
            rules.append({
                'name': rule.id,
                'category': rule.category.value,
                'display': rule.name,
                'severity': rule.default_severity.value,
                'description': rule.description
            })
        return rules
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        컨트롤러 초기화
        
        Args:
            logger: 로거 인스턴스
        """
        self.logger = logger or logging.getLogger(__name__)
        self.profile_manager = get_profile_manager()
    
    def _create_profile_info(self, profile: QualityProfile, 
                           is_current: bool = False) -> ProfileInfo:
        """프로파일을 UI용 정보로 변환"""
        # 활성화된 규칙 카운트
        enabled_rules_count = 0
        
        try:
            # 프로파일의 규칙 설정에서 활성화된 규칙 개수 계산
            check_options = profile.check_options or {}
            for rule in self.AVAILABLE_RULES:
                rule_name = rule['name']
                if check_options.get(rule_name, False):
                    enabled_rules_count += 1
        except Exception:
            enabled_rules_count = 0
        
        # 품질 기준 가져오기
        quality_standards = profile.quality_standards or {}
        check_options = profile.check_options or {}
        
        return ProfileInfo(
            name=profile.name,
            is_builtin=profile.is_builtin,
            is_current=is_current,
            description=profile.description or "",
            parent_profile=profile.parent_profile,
            created_at=profile.created_at,
            modified_at=profile.modified_at,
            enabled_rules_count=enabled_rules_count,
            min_image_dpi=quality_standards.get('min_image_dpi', 300),
            allow_rgb=check_options.get('allow_rgb', False),
            allow_spot=check_options.get('allow_spot', True),
            check_ink_coverage=check_options.get('ink_coverage', False)
        )