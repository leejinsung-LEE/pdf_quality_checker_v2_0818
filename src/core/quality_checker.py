# src/core/quality_checker.py
"""
PDF 품질 검사 시스템 - 통합 인터페이스

PDF 분석과 품질 검사를 연결하는 메인 클래스입니다.
프로파일 기반으로 동작하며, 다양한 검사 옵션을 제공합니다.
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import time

from .models import AnalysisResult, QualityIssue
from .analyzers import PDFAnalyzer
from .checkers import (
    CompositeChecker, CheckerContext,
    FontChecker, ColorChecker, ImageChecker, 
    LayoutChecker, PrintChecker
)
from .profiles import ProfileManager, QualityProfile, get_profile_manager
from ..config.alarm_config import AlarmConditionType, AlarmLevel
from ..utils.alarm_manager import get_alarm_manager


class QualityCheckResult:
    """품질 검사 결과 래퍼 클래스"""
    
    def __init__(self, analysis_result: AnalysisResult, issues: List[QualityIssue],
                 profile_name: str, check_duration: float):
        self.analysis_result = analysis_result
        self.issues = issues
        self.profile_name = profile_name
        self.check_duration = check_duration
        self.timestamp = datetime.now()
    
    @property
    def has_errors(self) -> bool:
        """오류가 있는지 확인"""
        return any(issue.severity.value == 'error' for issue in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        """경고가 있는지 확인"""
        return any(issue.severity.value == 'warning' for issue in self.issues)
    
    @property
    def error_count(self) -> int:
        """오류 개수"""
        return sum(1 for issue in self.issues if issue.severity.value == 'error')
    
    @property
    def warning_count(self) -> int:
        """경고 개수"""
        return sum(1 for issue in self.issues if issue.severity.value == 'warning')
    
    @property
    def info_count(self) -> int:
        """정보 개수"""
        return sum(1 for issue in self.issues if issue.severity.value == 'info')
    
    @property
    def quality_score(self) -> float:
        """품질 점수 (0-100)"""
        if not self.issues:
            return 100.0
        
        # 이슈별 감점
        deductions = {
            'error': 10,
            'warning': 3,
            'info': 1
        }
        
        total_deduction = sum(
            deductions.get(issue.severity.value, 0)
            for issue in self.issues
        )
        
        return max(0, 100 - total_deduction)
    
    def get_summary(self) -> Dict[str, Any]:
        """결과 요약"""
        return {
            'file': self.analysis_result.document.full_filename,
            'profile': self.profile_name,
            'quality_score': self.quality_score,
            'issues': {
                'errors': self.error_count,
                'warnings': self.warning_count,
                'info': self.info_count,
                'total': len(self.issues)
            },
            'duration': {
                'analysis': self.analysis_result.analysis_duration,
                'check': self.check_duration,
                'total': self.analysis_result.analysis_duration + self.check_duration
            },
            'timestamp': self.timestamp.isoformat()
        }


class PDFQualityChecker:
    """
    PDF 품질 검사 메인 클래스
    
    PDF 파일의 분석과 품질 검사를 통합 관리합니다.
    """
    
    def __init__(self, profile_manager: Optional[ProfileManager] = None):
        """
        품질 검사기 초기화
        
        Args:
            profile_manager: 프로파일 관리자 (없으면 기본값 사용)
        """
        self.profile_manager = profile_manager or get_profile_manager()
        self.analyzer = PDFAnalyzer()
        self._setup_checkers()
    
    def _setup_checkers(self):
        """검사기 설정"""
        self.checkers = {
            'font': FontChecker(),
            'color': ColorChecker(),
            'image': ImageChecker(),
            'layout': LayoutChecker(),
            'print': PrintChecker()
        }
        
        # 복합 검사기
        self.composite_checker = CompositeChecker()
        for checker in self.checkers.values():
            self.composite_checker.add_checker(checker)
    
    def check(self, pdf_path: Union[str, Path], 
              profile_name: Optional[str] = None,
              analysis_result: Optional[AnalysisResult] = None,
              check_options: Optional[Dict[str, bool]] = None) -> QualityCheckResult:
        """
        PDF 품질 검사 수행
        
        Args:
            pdf_path: PDF 파일 경로
            profile_name: 사용할 프로파일 이름 (없으면 현재 프로파일)
            analysis_result: 기존 분석 결과 (없으면 새로 분석)
            
        Returns:
            QualityCheckResult: 검사 결과
        """
        start_time = time.time()
        
        # 경로 정규화
        pdf_path = Path(pdf_path)
        
        # 1. PDF 분석 (필요시)
        if analysis_result is None:
            # PDF Analysis: Analyzing {pdf_path.name}
            analysis_result = self.analyzer.analyze(pdf_path)
        
        # 2. 프로파일 로드
        if profile_name:
            profile = self.profile_manager.get_profile(profile_name)
            if not profile:
                raise ValueError(f"프로파일 '{profile_name}'을 찾을 수 없습니다")
        else:
            profile = self.profile_manager.get_current_profile()
            profile_name = profile.name
        
        # Quality Check: Starting (Profile: {profile_name})
        
        # 3. 프로파일을 컨텍스트로 변환
        context = profile.to_checker_context()
        
        # 4. check_options에 따라 체커 필터링
        if check_options:
            # 임시 컴포지트 체커 생성
            temp_composite = CompositeChecker()
            
            # 요청된 체커만 추가
            checker_mapping = {
                'check_color': 'color',
                'check_font': 'font',
                'check_image': 'image',
                'check_bleed': 'layout',
                'check_metadata': 'print'
            }
            
            for option_key, enabled in check_options.items():
                if enabled and option_key in checker_mapping:
                    checker_name = checker_mapping[option_key]
                    if checker_name in self.checkers:
                        temp_composite.add_checker(self.checkers[checker_name])
            
            # 필터링된 체커로 검사
            issues = temp_composite.check(analysis_result, context)
        else:
            # 모든 체커로 검사
            issues = self.composite_checker.check(analysis_result, context)
        
        # 5. 분석 결과에 이슈 추가
        for issue in issues:
            analysis_result.add_issue(issue)
        
        check_duration = time.time() - start_time
        
        # Complete: Quality check done: {len(issues)} issues found ({check_duration:.2f}s)
        
        # 결과 생성
        result = QualityCheckResult(
            analysis_result=analysis_result,
            issues=issues,
            profile_name=profile_name,
            check_duration=check_duration
        )
        
        # 알람 처리
        self._process_alarms(result)
        
        return result
    
    def check_with_profile(self, pdf_path: Union[str, Path], 
                          profile: Union[str, QualityProfile]) -> QualityCheckResult:
        """특정 프로파일로 검사"""
        if isinstance(profile, str):
            profile_name = profile
        else:
            profile_name = profile.name
        
        return self.check(pdf_path, profile_name)
    
    def quick_check(self, pdf_path: Union[str, Path]) -> QualityCheckResult:
        """빠른 검사 (필수 항목만)"""
        return self.check_with_profile(pdf_path, 'quick')
    
    def strict_check(self, pdf_path: Union[str, Path]) -> QualityCheckResult:
        """엄격한 검사"""
        return self.check_with_profile(pdf_path, 'strict')
    
    def check_specific(self, pdf_path: Union[str, Path],
                      checkers: List[str],
                      profile_name: Optional[str] = None) -> QualityCheckResult:
        """
        특정 검사기만 사용하여 검사
        
        Args:
            pdf_path: PDF 파일 경로
            checkers: 사용할 검사기 이름 목록 ['font', 'color', ...]
            profile_name: 프로파일 이름
            
        Returns:
            QualityCheckResult: 검사 결과
        """
        # PDF 분석
        analysis_result = self.analyzer.analyze(pdf_path)
        
        # 프로파일 로드
        if profile_name:
            profile = self.profile_manager.get_profile(profile_name)
        else:
            profile = self.profile_manager.get_current_profile()
            profile_name = profile.name
        
        context = profile.to_checker_context()
        
        # 선택된 검사기만 사용
        selected_checker = CompositeChecker()
        for checker_name in checkers:
            if checker_name in self.checkers:
                selected_checker.add_checker(self.checkers[checker_name])
        
        # 검사 수행
        start_time = time.time()
        issues = selected_checker.check(analysis_result, context)
        check_duration = time.time() - start_time
        
        return QualityCheckResult(
            analysis_result=analysis_result,
            issues=issues,
            profile_name=profile_name,
            check_duration=check_duration
        )
    
    def batch_check(self, pdf_paths: List[Union[str, Path]], 
                   profile_name: Optional[str] = None) -> List[QualityCheckResult]:
        """
        여러 PDF 파일 일괄 검사
        
        Args:
            pdf_paths: PDF 파일 경로 목록
            profile_name: 프로파일 이름
            
        Returns:
            List[QualityCheckResult]: 각 파일의 검사 결과
        """
        results = []
        total = len(pdf_paths)
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            # [{i}/{total}] Checking: {Path(pdf_path).name}
            try:
                result = self.check(pdf_path, profile_name)
                results.append(result)
            except Exception as e:
                # [ERROR] Check failed: {e}
                # 실패한 경우도 결과에 포함 (에러 정보와 함께)
                # 실제 구현에서는 에러 처리 개선 필요
                pass
        
        return results
    
    def get_available_profiles(self) -> List[Dict[str, Any]]:
        """사용 가능한 프로파일 목록"""
        return self.profile_manager.get_profile_list()
    
    def set_profile(self, profile_name: str) -> bool:
        """현재 프로파일 설정"""
        return self.profile_manager.set_current_profile(profile_name)
    
    def _process_alarms(self, result: QualityCheckResult):
        """검사 결과에 따른 알람 처리"""
        alarm_manager = get_alarm_manager()
        
        # 오류 수준별 알람
        if result.has_errors:
            alarm_manager.check_and_notify(
                AlarmConditionType.ERROR_LEVEL,
                value=AlarmLevel.ERROR,
                title=f"오류 발생: {result.analysis_result.document.full_filename}",
                message=f"{result.error_count}개의 오류가 발견되었습니다."
            )
        elif result.has_warnings:
            alarm_manager.check_and_notify(
                AlarmConditionType.ERROR_LEVEL,
                value=AlarmLevel.WARNING,
                title=f"경고 발생: {result.analysis_result.document.full_filename}",
                message=f"{result.warning_count}개의 경고가 발견되었습니다."
            )
        
        # 문제 유형별 알람
        for issue in result.issues:
            # DPI 문제
            if issue.category == 'image' and 'DPI' in issue.description:
                # DPI 값 추출 (예: "이미지 해상도 부족: 150 DPI")
                try:
                    dpi_value = int(''.join(filter(str.isdigit, issue.description.split('DPI')[0])))
                    alarm_manager.check_and_notify(
                        AlarmConditionType.LOW_DPI,
                        value=dpi_value,
                        title="낮은 해상도 감지",
                        message=f"{issue.description}"
                    )
                except:
                    pass
            
            # 폰트 문제
            elif issue.category == 'font' and '임베딩' in issue.description:
                alarm_manager.check_and_notify(
                    AlarmConditionType.FONT_ISSUE,
                    title="폰트 문제 감지",
                    message=issue.description
                )
            
            # 잉크 커버리지 문제
            elif issue.category == 'color' and '잉크' in issue.description:
                # 잉크 커버리지 값 추출
                try:
                    coverage_value = int(''.join(filter(str.isdigit, issue.description.split('%')[0])))
                    alarm_manager.check_and_notify(
                        AlarmConditionType.INK_COVERAGE,
                        value=coverage_value,
                        title="잉크 커버리지 초과",
                        message=issue.description
                    )
                except:
                    pass
            
            # 재단선 문제
            elif issue.category == 'layout' and '재단' in issue.description:
                alarm_manager.check_and_notify(
                    AlarmConditionType.BLEED_ISSUE,
                    title="재단선 문제",
                    message=issue.description
                )
        
        # 처리 완료 알람
        if len(result.issues) == 0:
            alarm_manager.check_and_notify(
                AlarmConditionType.PROCESSING_COMPLETE,
                title="검사 완료",
                message=f"{result.analysis_result.document.full_filename} 파일 검사 완료 - 문제 없음"
            )
        else:
            alarm_manager.check_and_notify(
                AlarmConditionType.PROCESSING_COMPLETE,
                title="검사 완료",
                message=f"{result.analysis_result.document.full_filename} 파일 검사 완료 - {len(result.issues)}개 문제 발견"
            )
    
    def get_checker_info(self) -> Dict[str, Dict[str, Any]]:
        """검사기 정보 반환"""
        info = {}
        for name, checker in self.checkers.items():
            info[name] = {
                'name': checker.name,
                'description': checker.get_description(),
                'rules': [
                    {
                        'name': rule.name,
                        'category': rule.category.value,
                        'default_severity': rule.default_severity.value,
                        'description': rule.get_description()
                    }
                    for rule in checker.rules
                ]
            }
        return info


# 편의 함수들
def check_pdf(pdf_path: Union[str, Path], profile: str = 'default') -> QualityCheckResult:
    """PDF 품질 검사 편의 함수"""
    checker = PDFQualityChecker()
    return checker.check_with_profile(pdf_path, profile)


def quick_check_pdf(pdf_path: Union[str, Path]) -> QualityCheckResult:
    """빠른 PDF 검사 편의 함수"""
    checker = PDFQualityChecker()
    return checker.quick_check(pdf_path)


def strict_check_pdf(pdf_path: Union[str, Path]) -> QualityCheckResult:
    """엄격한 PDF 검사 편의 함수"""
    checker = PDFQualityChecker()
    return checker.strict_check(pdf_path)