# src/core/checkers/base_checker.py
"""
기본 검사기 추상 클래스

모든 품질 검사기가 상속받아야 하는 베이스 클래스입니다.
각 검사기는 여러 검사 규칙(Rule)을 포함하며, 
분석 결과를 바탕으로 품질 이슈를 검출합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

from ..models import AnalysisResult, QualityIssue
from ..models.quality_issue import IssueSeverity, IssueCategory


@dataclass
class CheckerContext:
    """검사기 실행 컨텍스트"""
    profile_name: str = "default"
    profile_settings: Dict[str, Any] = field(default_factory=dict)
    enabled_rules: Set[str] = field(default_factory=set)
    rule_severities: Dict[str, IssueSeverity] = field(default_factory=dict)
    check_options: Dict[str, bool] = field(default_factory=dict)  # 큰 범주별 온/오프
    
    def is_rule_enabled(self, rule_name: str) -> bool:
        """규칙 활성화 여부 확인"""
        if not self.enabled_rules:  # 비어있으면 모든 규칙 활성화
            return True
        return rule_name in self.enabled_rules
    
    def get_rule_severity(self, rule_name: str, default: IssueSeverity) -> IssueSeverity:
        """규칙의 심각도 가져오기"""
        return self.rule_severities.get(rule_name, default)
    
    def is_check_enabled(self, check_name: str) -> bool:
        """검사 옵션 활성화 여부 확인"""
        if not self.check_options:  # 비어있으면 모든 검사 활성화
            return True
        return self.check_options.get(check_name, True)


class CheckRule(ABC):
    """개별 검사 규칙 추상 클래스"""
    
    def __init__(self, name: str, category: IssueCategory, 
                 default_severity: IssueSeverity = IssueSeverity.WARNING):
        """
        검사 규칙 초기화
        
        Args:
            name: 규칙 이름 (고유해야 함)
            category: 이슈 카테고리
            default_severity: 기본 심각도
        """
        self.name = name
        self.category = category
        self.default_severity = default_severity
        self.enabled = True
    
    @abstractmethod
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """
        규칙 검사 수행
        
        Args:
            analysis_result: PDF 분석 결과
            context: 검사 컨텍스트
            
        Returns:
            QualityIssue: 발견된 이슈 또는 None
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """규칙 설명 반환"""
        pass
    
    def get_severity(self, context: CheckerContext) -> IssueSeverity:
        """컨텍스트를 고려한 심각도 반환"""
        return context.get_rule_severity(self.name, self.default_severity)


class BaseChecker(ABC):
    """
    품질 검사기 추상 베이스 클래스
    
    각 검사기는 특정 도메인(폰트, 색상 등)의 검사를 담당하며,
    여러 개의 검사 규칙을 포함합니다.
    """
    
    def __init__(self, name: str):
        """
        검사기 초기화
        
        Args:
            name: 검사기 이름
        """
        self.name = name
        self.rules: List[CheckRule] = []
        self._initialize_rules()
    
    @abstractmethod
    def _initialize_rules(self):
        """검사 규칙 초기화 - 하위 클래스에서 구현"""
        pass
    
    def add_rule(self, rule: CheckRule):
        """검사 규칙 추가"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str):
        """검사 규칙 제거"""
        self.rules = [r for r in self.rules if r.name != rule_name]
    
    def get_rule(self, rule_name: str) -> Optional[CheckRule]:
        """이름으로 규칙 찾기"""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def check(self, analysis_result: AnalysisResult, 
              context: Optional[CheckerContext] = None) -> List[QualityIssue]:
        """
        모든 활성화된 규칙을 실행하여 이슈 검출
        
        Args:
            analysis_result: PDF 분석 결과
            context: 검사 컨텍스트 (없으면 기본값 사용)
            
        Returns:
            List[QualityIssue]: 발견된 이슈 목록
        """
        if context is None:
            context = CheckerContext()
        
        issues = []
        
        # 각 규칙 실행
        for rule in self.rules:
            # 규칙이 활성화되어 있는지 확인
            if not context.is_rule_enabled(rule.name):
                continue
            
            try:
                # 규칙 검사 수행
                issue = rule.check(analysis_result, context)
                
                # 이슈가 발견되었으면 추가
                if issue:
                    # 컨텍스트의 심각도로 업데이트
                    issue.severity = rule.get_severity(context)
                    issues.append(issue)
                    
            except Exception as e:
                # 개별 규칙 실패는 전체 검사를 중단시키지 않음
                # 규칙 실행 중 오류 발생
                continue
        
        return issues
    
    def get_enabled_rules(self, context: CheckerContext) -> List[CheckRule]:
        """활성화된 규칙 목록 반환"""
        return [rule for rule in self.rules if context.is_rule_enabled(rule.name)]
    
    def get_rules_by_category(self, category: IssueCategory) -> List[CheckRule]:
        """카테고리별 규칙 필터링"""
        return [rule for rule in self.rules if rule.category == category]
    
    @abstractmethod
    def get_description(self) -> str:
        """검사기 설명 반환"""
        pass
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"{self.name} Checker ({len(self.rules)} rules)"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return f"{self.__class__.__name__}(name='{self.name}', rules={len(self.rules)})"


class CompositeChecker(BaseChecker):
    """
    여러 검사기를 조합하는 복합 검사기
    
    전체 품질 검사를 수행할 때 사용됩니다.
    """
    
    def __init__(self):
        super().__init__("Composite")
        self.checkers: List[BaseChecker] = []
    
    def _initialize_rules(self):
        """복합 검사기는 직접 규칙을 갖지 않음"""
        pass
    
    def add_checker(self, checker: BaseChecker):
        """검사기 추가"""
        self.checkers.append(checker)
        # 하위 검사기의 모든 규칙을 상위로 등록
        for rule in checker.rules:
            self.add_rule(rule)
    
    def check(self, analysis_result: AnalysisResult, 
              context: Optional[CheckerContext] = None) -> List[QualityIssue]:
        """모든 하위 검사기 실행"""
        if context is None:
            context = CheckerContext()
        
        all_issues = []
        
        for checker in self.checkers:
            try:
                issues = checker.check(analysis_result, context)
                all_issues.extend(issues)
            except Exception as e:
                # 검사 중 오류 발생
                continue
        
        # 이슈를 심각도와 카테고리별로 정렬
        all_issues.sort()
        
        return all_issues
    
    def get_description(self) -> str:
        """검사기 설명"""
        return f"종합 품질 검사 ({len(self.checkers)}개 검사기)"