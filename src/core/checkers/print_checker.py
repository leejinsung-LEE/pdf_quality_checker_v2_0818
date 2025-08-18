# src/core/checkers/print_checker.py
"""
인쇄 설정 검사기

오버프린트 설정 등 인쇄 관련 품질 문제를 검사합니다.
"""

from typing import Optional, List, Dict, Any

from .base_checker import BaseChecker, CheckRule, CheckerContext
from ..models import AnalysisResult, QualityIssue
from ..models.quality_issue import IssueSeverity, IssueCategory


class OverprintRule(CheckRule):
    """오버프린트 설정 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="overprint_check",
            category=IssueCategory.OVERPRINT,
            default_severity=IssueSeverity.WARNING
        )
        self.external_tools_available = self._check_tools()
    
    def _check_tools(self) -> bool:
        """외부 도구 사용 가능 여부 확인"""
        try:
            from ...external import get_tool_manager
            tool_manager = get_tool_manager()
            return tool_manager.has_tool('ghostscript')
        except (ImportError, AttributeError, Exception) as e:
            self.logger.debug(f"도구 확인 실패: {e}")
            return False
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """오버프린트 설정 검사"""
        # 오버프린트 검사 활성화 여부
        if not context.profile_settings.get('overprint', True):
            return None
        
        # 외부 도구가 없으면 검사 불가
        if not self.external_tools_available:
            return self._create_tool_missing_issue()
        
        # 오버프린트 정보 가져오기
        overprint_info = self._get_overprint_info(analysis_result)
        
        if not overprint_info or not overprint_info.get('has_overprint'):
            return None
        
        # 문제가 있는 오버프린트 확인
        if overprint_info.get('has_problematic_overprint'):
            return self._create_problematic_overprint_issue(overprint_info)
        
        # 일반 오버프린트 정보 제공
        return self._create_overprint_info_issue(overprint_info)
    
    def _get_overprint_info(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """분석 결과에서 오버프린트 정보 추출"""
        # AnalysisResult에 오버프린트 정보가 있는지 확인
        # 실제로는 별도 오버프린트 분석이 필요할 수 있음
        
        # 임시 구현 - 실제로는 Ghostscript를 통한 분석 필요
        return {
            'has_overprint': False,
            'has_problematic_overprint': False,
            'overprint_objects': [],
            'pages_with_overprint': []
        }
    
    def _create_tool_missing_issue(self) -> QualityIssue:
        """도구 누락 이슈 생성"""
        return QualityIssue(
            category=self.category,
            severity=IssueSeverity.INFO,
            title="오버프린트 검사 불가",
            description="Ghostscript가 설치되지 않아 오버프린트 검사를 수행할 수 없습니다.",
            pages=[],
            details={'tool_required': 'ghostscript'}
        )
    
    def _create_problematic_overprint_issue(self, overprint_info: Dict) -> QualityIssue:
        """문제가 있는 오버프린트 이슈 생성"""
        pages = overprint_info.get('pages_with_overprint', [])
        white_overprint = overprint_info.get('white_overprint_pages', [])
        light_color = overprint_info.get('light_color_overprint_pages', [])
        
        # 가장 심각한 문제 기준으로 설명 구성
        if white_overprint:
            title = "위험한 오버프린트 설정"
            description = (f"{len(white_overprint)}개 페이지에서 흰색 오버프린트가 발견되었습니다. "
                          "인쇄 시 해당 요소가 사라질 수 있습니다.")
            severity = IssueSeverity.ERROR
        elif light_color:
            title = "주의가 필요한 오버프린트"
            description = (f"{len(light_color)}개 페이지에서 밝은 색상의 오버프린트가 발견되었습니다. "
                          "인쇄 시 예상과 다른 결과가 나올 수 있습니다.")
            severity = IssueSeverity.WARNING
        else:
            title = "오버프린트 설정 확인 필요"
            description = "일부 오버프린트 설정이 의도적인지 확인이 필요합니다."
            severity = self.get_severity(context)
        
        issue = QualityIssue(
            category=self.category,
            severity=severity,
            title=title,
            description=description,
            pages=sorted(set(pages)),
            details={
                'total_pages': len(pages),
                'white_overprint_pages': white_overprint[:5],
                'light_color_pages': light_color[:5],
                'k_only_pages': overprint_info.get('k_only_overprint_pages', [])[:5]
            }
        )
        
        issue.add_fix_option(
            method="remove_overprint",
            description="문제가 있는 오버프린트 설정 제거",
            risk_level="medium"
        )
        
        return issue
    
    def _create_overprint_info_issue(self, overprint_info: Dict) -> QualityIssue:
        """일반 오버프린트 정보 이슈 생성"""
        pages = overprint_info.get('pages_with_overprint', [])
        
        return QualityIssue(
            category=self.category,
            severity=IssueSeverity.INFO,
            title="오버프린트 설정 발견",
            description=(f"{len(pages)}개 페이지에서 오버프린트 설정이 발견되었습니다. "
                        "의도적인 설정인지 확인하세요."),
            pages=pages[:10],  # 최대 10개
            details={
                'total_pages': len(pages),
                'overprint_types': overprint_info.get('overprint_types', {})
            }
        )
    
    def get_description(self) -> str:
        return "인쇄 시 문제가 될 수 있는 오버프린트 설정 검사"


class WhiteOverprintRule(CheckRule):
    """흰색 오버프린트 전용 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="white_overprint",
            category=IssueCategory.OVERPRINT,
            default_severity=IssueSeverity.ERROR
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """흰색 오버프린트 검사"""
        # 오버프린트 세부 설정 확인
        check_white = context.profile_settings.get('check_white_overprint', True)
        if not check_white:
            return None
        
        # 실제 구현에서는 Ghostscript를 통해 흰색 오버프린트를 찾아야 함
        # 여기서는 구조만 제공
        
        return None
    
    def get_description(self) -> str:
        return "인쇄 시 사라질 수 있는 흰색 오버프린트 검사"


class PrintChecker(BaseChecker):
    """
    인쇄 설정 검사기
    
    오버프린트 등 인쇄 관련 설정을 검사합니다.
    """
    
    def __init__(self):
        super().__init__("Print")
        self._check_external_tools()
    
    def _check_external_tools(self):
        """외부 도구 상태 확인"""
        try:
            from ...external import get_tool_manager
            self.tool_manager = get_tool_manager()
            self.has_ghostscript = self.tool_manager.has_tool('ghostscript')
        except (ImportError, AttributeError, Exception) as e:
            self.logger.debug(f"외부 도구 초기화 실패: {e}")
            self.tool_manager = None
            self.has_ghostscript = False
    
    def _initialize_rules(self):
        """인쇄 관련 검사 규칙 초기화"""
        # 오버프린트 검사
        self.add_rule(OverprintRule())
        
        # 흰색 오버프린트 전용 검사
        self.add_rule(WhiteOverprintRule())
    
    def get_description(self) -> str:
        return "오버프린트 등 인쇄 설정을 검사합니다."
    
    def check_with_external_analysis(self, analysis_result: AnalysisResult, 
                                   overprint_data: Dict[str, Any],
                                   context: Optional[CheckerContext] = None) -> List[QualityIssue]:
        """
        외부 분석 데이터를 포함한 검사
        
        Args:
            analysis_result: 기본 분석 결과
            overprint_data: Ghostscript 등으로 분석한 오버프린트 데이터
            context: 검사 컨텍스트
            
        Returns:
            List[QualityIssue]: 발견된 이슈들
        """
        if context is None:
            context = CheckerContext()
        
        issues = []
        
        # 오버프린트 데이터가 있으면 상세 검사
        if overprint_data and overprint_data.get('success'):
            # 문제가 있는 오버프린트 확인
            if overprint_data.get('has_problematic_overprint'):
                issue = self._create_detailed_overprint_issue(overprint_data, context)
                if issue:
                    issues.append(issue)
            elif overprint_data.get('has_overprint'):
                # 일반 오버프린트 정보
                issue = self._create_overprint_info(overprint_data, context)
                if issue:
                    issues.append(issue)
        
        return issues
    
    def _create_detailed_overprint_issue(self, overprint_data: Dict, 
                                       context: CheckerContext) -> Optional[QualityIssue]:
        """상세 오버프린트 이슈 생성"""
        white_pages = overprint_data.get('white_overprint_pages', [])
        light_pages = overprint_data.get('light_color_overprint_pages', [])
        
        if white_pages:
            severity = IssueSeverity.ERROR
            title = "흰색 오버프린트 발견"
            description = (f"{len(white_pages)}개 페이지에서 흰색 오버프린트가 발견되었습니다. "
                          "인쇄 시 해당 요소가 완전히 사라집니다.")
            problem_type = 'white_overprint'
        elif light_pages:
            severity = IssueSeverity.WARNING
            title = "밝은 색상 오버프린트"
            description = (f"{len(light_pages)}개 페이지에서 20% 미만의 밝은 색상 오버프린트가 발견되었습니다.")
            problem_type = 'light_color_overprint'
        else:
            return None
        
        all_pages = sorted(set(white_pages + light_pages))
        
        issue = QualityIssue(
            category=IssueCategory.OVERPRINT,
            severity=severity,
            title=title,
            description=description,
            pages=all_pages[:20],  # 최대 20개
            details={
                'problem_type': problem_type,
                'white_pages': white_pages[:10],
                'light_pages': light_pages[:10],
                'total_affected': len(all_pages)
            }
        )
        
        issue.add_fix_option(
            method="fix_overprint",
            description="문제가 있는 오버프린트 설정 수정",
            risk_level="medium"
        )
        
        return issue
    
    def _create_overprint_info(self, overprint_data: Dict, 
                              context: CheckerContext) -> Optional[QualityIssue]:
        """일반 오버프린트 정보 생성"""
        pages = overprint_data.get('pages_with_overprint', [])
        
        if not pages:
            return None
        
        return QualityIssue(
            category=IssueCategory.OVERPRINT,
            severity=IssueSeverity.INFO,
            title="오버프린트 설정 사용",
            description=(f"{len(pages)}개 페이지에서 오버프린트가 사용되었습니다. "
                        "K100% 텍스트의 오버프린트는 정상입니다."),
            pages=pages[:10],
            details={
                'total_pages': len(pages),
                'k_only_pages': overprint_data.get('k_only_overprint_pages', [])[:5]
            }
        )