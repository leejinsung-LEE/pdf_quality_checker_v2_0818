# src/core/checkers/layout_checker.py
"""
레이아웃 품질 검사기

재단선(Bleed), 여백 등 레이아웃 관련 품질 문제를 검사합니다.
"""

from typing import Optional, List, Dict, Any

from .base_checker import BaseChecker, CheckRule, CheckerContext
from ..models import AnalysisResult, QualityIssue, PageInfo
from ..models.quality_issue import (
    IssueSeverity, IssueCategory,
    create_missing_bleed_issue
)


class BleedCheckRule(CheckRule):
    """재단선(Bleed) 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="bleed_check",
            category=IssueCategory.PAGE_BLEED,
            default_severity=IssueSeverity.WARNING
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """재단선 검사"""
        # 설정값 가져오기
        required_bleed = context.profile_settings.get('standard_bleed_size', 3.0)
        
        # 재단선이 부족한 페이지 찾기
        insufficient_pages = []
        no_bleed_pages = []
        
        for page in analysis_result.pages:
            if page.bleed_info:
                # 재단선이 있지만 부족한 경우
                min_bleed = page.bleed_info.minimum
                if min_bleed < required_bleed:
                    insufficient_pages.append({
                        'page': page.page_number,
                        'current_bleed': min_bleed,
                        'top': page.bleed_info.top,
                        'bottom': page.bleed_info.bottom,
                        'left': page.bleed_info.left,
                        'right': page.bleed_info.right
                    })
            else:
                # 재단선이 전혀 없는 경우
                no_bleed_pages.append(page.page_number)
        
        # 문제가 없으면 None 반환
        if not insufficient_pages and not no_bleed_pages:
            return None
        
        # 이슈 생성
        all_problem_pages = [p['page'] for p in insufficient_pages] + no_bleed_pages
        all_problem_pages.sort()
        
        # 심각도 결정 - 프로파일 설정에 따라
        if required_bleed == 0:
            # 재단선이 필요없는 경우 (웹용 등)
            return None
        
        severity = self.get_severity(context)
        
        # 설명 구성
        if no_bleed_pages and insufficient_pages:
            title = "재단선 누락 또는 부족"
            description = (f"{len(no_bleed_pages)}개 페이지에 재단선이 없고, "
                          f"{len(insufficient_pages)}개 페이지에 재단선이 부족합니다. "
                          f"최소 {required_bleed}mm의 재단선이 필요합니다.")
        elif no_bleed_pages:
            title = "재단선 누락"
            description = (f"{len(no_bleed_pages)}개 페이지에 재단선이 없습니다. "
                          f"재단 시 흰 여백이 생길 수 있습니다. "
                          f"최소 {required_bleed}mm의 재단선이 필요합니다.")
        else:
            title = "재단선 부족"
            description = (f"{len(insufficient_pages)}개 페이지의 재단선이 "
                          f"{required_bleed}mm 미만입니다. "
                          "재단 시 일부 여백이 생길 수 있습니다.")
        
        issue = QualityIssue(
            category=self.category,
            severity=severity,
            title=title,
            description=description,
            pages=all_problem_pages,
            details={
                'required_bleed': required_bleed,
                'no_bleed_count': len(no_bleed_pages),
                'insufficient_count': len(insufficient_pages),
                'no_bleed_pages': no_bleed_pages[:10],  # 최대 10개
                'insufficient_details': insufficient_pages[:5]  # 최대 5개 상세 정보
            }
        )
        
        # 수정 옵션 (위험도 높음)
        issue.add_fix_option(
            method="add_bleed",
            description=f"모든 페이지에 {required_bleed}mm 재단선 추가",
            parameters={'bleed_size': required_bleed},
            risk_level="high"
        )
        
        return issue
    
    def get_description(self) -> str:
        return "인쇄물 재단을 위한 여백(Bleed) 검사"


class NonUniformBleedRule(CheckRule):
    """불균일한 재단선 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="non_uniform_bleed",
            category=IssueCategory.PAGE_BLEED,
            default_severity=IssueSeverity.INFO
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """불균일한 재단선 검사"""
        # 재단선이 있는 페이지들의 불균일성 검사
        non_uniform_pages = []
        
        for page in analysis_result.pages:
            if page.bleed_info and not page.bleed_info.is_uniform:
                # 각 방향의 차이가 큰 경우
                bleeds = [
                    page.bleed_info.top,
                    page.bleed_info.bottom,
                    page.bleed_info.left,
                    page.bleed_info.right
                ]
                max_diff = max(bleeds) - min(bleeds)
                
                if max_diff > 1.0:  # 1mm 이상 차이
                    non_uniform_pages.append({
                        'page': page.page_number,
                        'top': page.bleed_info.top,
                        'bottom': page.bleed_info.bottom,
                        'left': page.bleed_info.left,
                        'right': page.bleed_info.right,
                        'difference': max_diff
                    })
        
        if not non_uniform_pages:
            return None
        
        issue = QualityIssue(
            category=self.category,
            severity=self.get_severity(context),
            title="불균일한 재단선",
            description=(f"{len(non_uniform_pages)}개 페이지에서 재단선이 균일하지 않습니다. "
                        "일관된 재단 결과를 위해 모든 방향의 재단선을 동일하게 설정하는 것을 권장합니다."),
            pages=[p['page'] for p in non_uniform_pages],
            details={
                'count': len(non_uniform_pages),
                'pages_detail': non_uniform_pages[:5]  # 최대 5개
            }
        )
        
        return issue
    
    def get_description(self) -> str:
        return "재단선의 균일성 검사"


class LargeFormatBleedRule(CheckRule):
    """대형 인쇄물 재단선 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="large_format_bleed",
            category=IssueCategory.PAGE_BLEED,
            default_severity=IssueSeverity.INFO
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """대형 인쇄물 재단선 검사"""
        # 대형 포맷 기준 (A2 이상)
        large_format_threshold = 420  # A2 width in mm
        large_format_bleed = context.profile_settings.get('large_format_bleed', 10.0)
        
        # 대형 페이지 찾기
        large_pages_insufficient = []
        
        for page in analysis_result.pages:
            # 대형 페이지인지 확인
            if page.width_mm >= large_format_threshold or page.height_mm >= large_format_threshold:
                # 재단선 확인
                if page.bleed_info:
                    min_bleed = page.bleed_info.minimum
                    if min_bleed < large_format_bleed:
                        large_pages_insufficient.append({
                            'page': page.page_number,
                            'size': f"{page.width_mm:.0f}x{page.height_mm:.0f}mm",
                            'current_bleed': min_bleed,
                            'required_bleed': large_format_bleed
                        })
                else:
                    large_pages_insufficient.append({
                        'page': page.page_number,
                        'size': f"{page.width_mm:.0f}x{page.height_mm:.0f}mm",
                        'current_bleed': 0,
                        'required_bleed': large_format_bleed
                    })
        
        if not large_pages_insufficient:
            return None
        
        issue = QualityIssue(
            category=self.category,
            severity=self.get_severity(context),
            title="대형 인쇄물 재단선 부족",
            description=(f"{len(large_pages_insufficient)}개 대형 페이지의 재단선이 부족합니다. "
                        f"대형 인쇄물은 {large_format_bleed}mm 이상의 재단선이 권장됩니다."),
            pages=[p['page'] for p in large_pages_insufficient],
            details={
                'count': len(large_pages_insufficient),
                'required_bleed': large_format_bleed,
                'pages': large_pages_insufficient
            }
        )
        
        return issue
    
    def get_description(self) -> str:
        return "대형 인쇄물을 위한 확장 재단선 검사"


class LayoutChecker(BaseChecker):
    """
    레이아웃 품질 검사기
    
    재단선, 여백 등 레이아웃 관련 요소를 검사합니다.
    """
    
    def __init__(self):
        super().__init__("Layout")
    
    def _initialize_rules(self):
        """레이아웃 관련 검사 규칙 초기화"""
        # 기본 재단선 검사
        self.add_rule(BleedCheckRule())
        
        # 불균일한 재단선 검사
        self.add_rule(NonUniformBleedRule())
        
        # 대형 인쇄물 재단선 검사
        self.add_rule(LargeFormatBleedRule())
    
    def get_description(self) -> str:
        return "재단선, 여백 등 레이아웃 품질을 검사합니다."
    
    def get_bleed_summary(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """재단선 요약 정보 반환"""
        summary = {
            'total_pages': len(analysis_result.pages),
            'pages_with_bleed': 0,
            'pages_without_bleed': 0,
            'uniform_bleed_pages': 0,
            'min_bleed_found': float('inf'),
            'max_bleed_found': 0,
            'avg_bleed': 0
        }
        
        bleed_values = []
        
        for page in analysis_result.pages:
            if page.bleed_info:
                summary['pages_with_bleed'] += 1
                min_bleed = page.bleed_info.minimum
                avg_bleed = page.bleed_info.average
                
                bleed_values.append(avg_bleed)
                summary['min_bleed_found'] = min(summary['min_bleed_found'], min_bleed)
                summary['max_bleed_found'] = max(summary['max_bleed_found'], page.bleed_info.top,
                                                page.bleed_info.bottom, page.bleed_info.left,
                                                page.bleed_info.right)
                
                if page.bleed_info.is_uniform:
                    summary['uniform_bleed_pages'] += 1
            else:
                summary['pages_without_bleed'] += 1
        
        # 평균 계산
        if bleed_values:
            summary['avg_bleed'] = sum(bleed_values) / len(bleed_values)
        
        if summary['min_bleed_found'] == float('inf'):
            summary['min_bleed_found'] = 0
        
        return summary