# -*- coding: utf-8 -*-
"""
PDF 검사 규칙 레지스트리

모든 검사 규칙을 중앙에서 관리하는 레지스트리입니다.
GUI와 Checker들이 공통으로 참조합니다.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class RuleCategory(Enum):
    """규칙 카테고리"""
    FONT = "font"
    COLOR = "color"
    IMAGE = "image"
    LAYOUT = "layout"
    PRINT = "print"
    ADVANCED = "advanced"


class RuleSeverity(Enum):
    """규칙 심각도"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CheckRule:
    """검사 규칙 정의"""
    id: str  # 고유 ID
    name: str  # 표시 이름
    category: RuleCategory  # 카테고리
    default_severity: RuleSeverity  # 기본 심각도
    description: str  # 설명
    enabled_by_default: bool = True  # 기본 활성화 여부
    checker_class: str = ""  # 담당 Checker 클래스명


class RuleRegistry:
    """검사 규칙 레지스트리"""
    
    # 모든 검사 규칙 정의
    RULES = [
        # === 폰트 규칙 ===
        CheckRule(
            id="font_not_embedded",
            name="폰트 임베딩 확인",
            category=RuleCategory.FONT,
            default_severity=RuleSeverity.ERROR,
            description="PDF에 임베드되지 않은 폰트 검사",
            checker_class="FontChecker"
        ),
        CheckRule(
            id="type3_font",
            name="Type3 폰트 검사",
            category=RuleCategory.FONT,
            default_severity=RuleSeverity.WARNING,
            description="비트맵 Type3 폰트 사용 검사",
            checker_class="FontChecker"
        ),
        CheckRule(
            id="min_font_size",
            name="최소 폰트 크기",
            category=RuleCategory.FONT,
            default_severity=RuleSeverity.WARNING,
            description="너무 작은 텍스트 검사 (6pt 미만)",
            checker_class="FontChecker"
        ),
        CheckRule(
            id="font_substitution",
            name="폰트 대체 감지",
            category=RuleCategory.FONT,
            default_severity=RuleSeverity.ERROR,
            description="시스템 폰트로 대체된 폰트 검사",
            enabled_by_default=True,
            checker_class="AdvancedChecker"
        ),
        
        # === 색상 규칙 ===
        CheckRule(
            id="rgb_color_used",
            name="RGB 색상 사용",
            category=RuleCategory.COLOR,
            default_severity=RuleSeverity.ERROR,
            description="인쇄용 PDF에서 RGB 색상 사용 검사",
            checker_class="ColorChecker"
        ),
        CheckRule(
            id="high_ink_coverage",
            name="잉크 커버리지 초과",
            category=RuleCategory.COLOR,
            default_severity=RuleSeverity.WARNING,
            description="총 잉크량 320% 초과 검사",
            checker_class="ColorChecker"
        ),
        CheckRule(
            id="spot_color_limit",
            name="별색 개수 제한",
            category=RuleCategory.COLOR,
            default_severity=RuleSeverity.INFO,
            description="별색 4개 초과 사용 검사",
            checker_class="ColorChecker"
        ),
        CheckRule(
            id="white_overprint",
            name="흰색 오버프린트",
            category=RuleCategory.COLOR,
            default_severity=RuleSeverity.WARNING,
            description="흰색 객체의 오버프린트 설정 검사",
            enabled_by_default=True,
            checker_class="AdvancedChecker"
        ),
        CheckRule(
            id="devicen_color",
            name="DeviceN 색상 공간",
            category=RuleCategory.COLOR,
            default_severity=RuleSeverity.INFO,
            description="DeviceN 색상 공간 사용 검사",
            enabled_by_default=True,
            checker_class="AdvancedChecker"
        ),
        
        # === 이미지 규칙 ===
        CheckRule(
            id="low_resolution_image",
            name="저해상도 이미지",
            category=RuleCategory.IMAGE,
            default_severity=RuleSeverity.WARNING,
            description="300dpi 미만 이미지 검사",
            checker_class="ImageChecker"
        ),
        CheckRule(
            id="16bit_image",
            name="16비트 이미지",
            category=RuleCategory.IMAGE,
            default_severity=RuleSeverity.INFO,
            description="16비트 이미지 사용 검사",
            enabled_by_default=True,
            checker_class="AdvancedChecker"
        ),
        CheckRule(
            id="jpeg2000_compression",
            name="JPEG2000 압축",
            category=RuleCategory.IMAGE,
            default_severity=RuleSeverity.WARNING,
            description="JPEG2000 압축 사용 검사",
            enabled_by_default=True,
            checker_class="AdvancedChecker"
        ),
        CheckRule(
            id="jbig2_compression",
            name="JBIG2 압축",
            category=RuleCategory.IMAGE,
            default_severity=RuleSeverity.WARNING,
            description="JBIG2 압축 사용 검사",
            enabled_by_default=True,
            checker_class="AdvancedChecker"
        ),
        
        # === 레이아웃 규칙 ===
        CheckRule(
            id="missing_bleed",
            name="재단선 누락",
            category=RuleCategory.LAYOUT,
            default_severity=RuleSeverity.WARNING,
            description="3mm 재단선 여백 검사",
            checker_class="LayoutChecker"
        ),
        CheckRule(
            id="non_uniform_bleed",
            name="불균일한 재단선",
            category=RuleCategory.LAYOUT,
            default_severity=RuleSeverity.INFO,
            description="페이지별 재단선 차이 검사",
            checker_class="LayoutChecker"
        ),
        
        # === 인쇄 설정 규칙 ===
        CheckRule(
            id="overprint_settings",
            name="오버프린트 설정",
            category=RuleCategory.PRINT,
            default_severity=RuleSeverity.INFO,
            description="오버프린트 설정 검사",
            checker_class="PrintChecker"
        ),
        CheckRule(
            id="transparency_used",
            name="투명도 사용",
            category=RuleCategory.PRINT,
            default_severity=RuleSeverity.INFO,
            description="투명 효과 사용 검사",
            checker_class="PrintChecker"
        ),
        
        # === 고급 규칙 ===
        CheckRule(
            id="icc_profile_missing",
            name="ICC 프로파일 누락",
            category=RuleCategory.ADVANCED,
            default_severity=RuleSeverity.INFO,
            description="ICC 프로파일 포함 여부 검사",
            enabled_by_default=True,
            checker_class="AdvancedChecker"
        ),
        CheckRule(
            id="pdf_version_check",
            name="PDF 버전 확인",
            category=RuleCategory.ADVANCED,
            default_severity=RuleSeverity.INFO,
            description="PDF 버전 호환성 검사",
            enabled_by_default=False,
            checker_class="AdvancedChecker"
        ),
    ]
    
    @classmethod
    def get_all_rules(cls) -> List[CheckRule]:
        """모든 규칙 반환"""
        return cls.RULES
    
    @classmethod
    def get_rules_by_category(cls, category: RuleCategory) -> List[CheckRule]:
        """카테고리별 규칙 반환"""
        return [rule for rule in cls.RULES if rule.category == category]
    
    @classmethod
    def get_rule_by_id(cls, rule_id: str) -> CheckRule:
        """ID로 규칙 찾기"""
        for rule in cls.RULES:
            if rule.id == rule_id:
                return rule
        return None
    
    @classmethod
    def get_categories(cls) -> List[RuleCategory]:
        """모든 카테고리 반환"""
        return list(RuleCategory)
    
    @classmethod
    def get_default_enabled_rules(cls) -> List[str]:
        """기본 활성화된 규칙 ID 목록"""
        return [rule.id for rule in cls.RULES if rule.enabled_by_default]
    
    @classmethod
    def get_rules_for_checker(cls, checker_class: str) -> List[CheckRule]:
        """특정 Checker가 담당하는 규칙들"""
        return [rule for rule in cls.RULES if rule.checker_class == checker_class]
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """딕셔너리로 변환 (JSON 저장용)"""
        return {
            "rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "category": rule.category.value,
                    "default_severity": rule.default_severity.value,
                    "description": rule.description,
                    "enabled_by_default": rule.enabled_by_default,
                    "checker_class": rule.checker_class
                }
                for rule in cls.RULES
            ]
        }
    
    @classmethod
    def get_category_display_name(cls, category: RuleCategory) -> str:
        """카테고리 표시명"""
        display_names = {
            RuleCategory.FONT: "폰트",
            RuleCategory.COLOR: "색상",
            RuleCategory.IMAGE: "이미지",
            RuleCategory.LAYOUT: "레이아웃",
            RuleCategory.PRINT: "인쇄 설정",
            RuleCategory.ADVANCED: "고급"
        }
        return display_names.get(category, category.value)