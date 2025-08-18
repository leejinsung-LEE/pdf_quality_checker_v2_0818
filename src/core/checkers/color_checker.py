# src/core/checkers/color_checker.py
"""
색상 품질 검사기

RGB 색상 사용, 별색 사용, 잉크량 등
색상 관련 품질 문제를 검사합니다.
"""

from typing import Optional, List, Dict, Any, Set
import fitz  # PyMuPDF

from .base_checker import BaseChecker, CheckRule, CheckerContext
from ..models import AnalysisResult, QualityIssue
from ..models.quality_issue import (
    IssueSeverity, IssueCategory, 
    create_rgb_color_issue, create_high_ink_coverage_issue
)


class RGBColorRule(CheckRule):
    """RGB 색상 사용 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="rgb_color_usage",
            category=IssueCategory.COLOR_SPACE,
            default_severity=IssueSeverity.ERROR  # 기본은 오류
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """RGB 색상 사용 검사"""
        # 색상 설정 가져오기
        allow_rgb = context.profile_settings.get('allow_rgb', False)
        check_rgb = context.profile_settings.get('check_rgb', True)
        
        # RGB 검사가 비활성화되어 있으면 건너뛰기
        if not check_rgb:
            return None
        
        # 분석 결과에서 RGB 사용 확인
        if not analysis_result.colors.uses_rgb:
            return None
        
        # RGB가 허용되면 심각도를 INFO로 낮춤
        severity = IssueSeverity.INFO if allow_rgb else self.get_severity(context)
        
        # RGB 사용 페이지 추가 분석 (필요시)
        rgb_pages = self._find_rgb_pages(analysis_result)
        
        issue = QualityIssue(
            category=self.category,
            severity=severity,
            title="RGB 색상 공간 사용",
            description="인쇄용 PDF에는 CMYK 색상을 사용해야 합니다. RGB 색상이 발견되었습니다.",
            pages=rgb_pages,
            details={
                'count': analysis_result.colors.rgb_object_count,
                'color_spaces': list(analysis_result.colors.color_spaces_used),
                'allow_rgb': allow_rgb
            }
        )
        
        # RGB가 허용되지 않을 때만 수정 옵션 제공
        if not allow_rgb:
            issue.add_fix_option(
                method="convert_rgb_to_cmyk",
                description="모든 RGB 색상을 CMYK로 변환",
                parameters={'profile': 'ISO Coated v2'},
                risk_level="low"
            )
        
        return issue
    
    def _find_rgb_pages(self, analysis_result: AnalysisResult) -> List[int]:
        """RGB가 사용된 페이지 찾기"""
        # page_color_info가 있으면 사용
        if hasattr(analysis_result, 'page_color_info'):
            rgb_pages = []
            for page_info in analysis_result.page_color_info:
                if 'RGB' in page_info.get('color_spaces', []):
                    rgb_pages.append(page_info['page_number'])
            return rgb_pages
        
        # 없으면 빈 리스트 (전체 문서)
        return []
    
    def get_description(self) -> str:
        return "인쇄용 PDF의 RGB 색상 사용을 검사합니다."


class SpotColorRule(CheckRule):
    """별색 사용 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="spot_color_usage",
            category=IssueCategory.SPOT_COLOR,
            default_severity=IssueSeverity.WARNING
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """별색 사용 검사"""
        # 설정 가져오기
        check_spot = context.profile_settings.get('check_spot', True)
        allow_spot = context.profile_settings.get('allow_spot', True)
        spot_limit = context.profile_settings.get('spot_color_limit', 2)
        
        if not check_spot:
            return None
        
        # 별색 사용 확인
        if not analysis_result.colors.uses_spot_colors:
            return None
        
        spot_count = len(analysis_result.colors.spot_colors)
        
        # 별색이 허용되지 않거나 제한을 초과한 경우
        if not allow_spot:
            severity = self.get_severity(context)
            title = "별색 사용 불가"
            description = f"{spot_count}개의 별색이 사용되었습니다. 이 프로파일에서는 별색을 허용하지 않습니다."
        elif spot_count > spot_limit:
            severity = IssueSeverity.WARNING
            title = "과도한 별색 사용"
            description = f"{spot_count}개의 별색이 사용되었습니다. 권장 제한({spot_limit}개)을 초과했습니다."
        else:
            severity = IssueSeverity.INFO
            title = "별색 사용 확인"
            description = f"{spot_count}개의 별색이 사용되었습니다. 추가 인쇄 비용이 발생할 수 있습니다."
        
        # PyMuPDF로 추가 별색 정보 수집
        spot_details = self._analyze_spot_colors_pymupdf(analysis_result.document.path)
        
        issue = QualityIssue(
            category=self.category,
            severity=severity,
            title=title,
            description=description,
            pages=spot_details.get('pages', []),
            details={
                'count': spot_count,
                'spot_colors': analysis_result.colors.spot_colors,
                'allow_spot': allow_spot,
                'spot_limit': spot_limit,
                'pantone_colors': spot_details.get('pantone_colors', [])
            },
            related_objects=analysis_result.colors.spot_colors
        )
        
        # 별색이 허용되지 않을 때 수정 옵션
        if not allow_spot:
            issue.add_fix_option(
                method="convert_spot_to_cmyk",
                description="모든 별색을 CMYK로 변환",
                risk_level="medium"
            )
        
        return issue
    
    def _analyze_spot_colors_pymupdf(self, pdf_path) -> Dict[str, Any]:
        """PyMuPDF를 사용한 별색 추가 분석"""
        spot_info = {
            'pages': [],
            'pantone_colors': [],
            'spot_details': {}
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc, 1):
                # 페이지의 색상 정보 추출
                # PyMuPDF는 별색 정보에 대한 직접적인 API가 제한적이므로
                # 리소스 딕셔너리를 통해 간접적으로 확인
                try:
                    # 페이지 리소스에서 ColorSpace 확인
                    xref = page.xref
                    if xref > 0:
                        # PDF 객체 직접 확인
                        obj_str = doc.xref_object(xref)
                        if isinstance(obj_str, str) and 'Separation' in obj_str:
                            spot_info['pages'].append(page_num)
                            
                            # PANTONE 색상 확인
                            if 'PANTONE' in obj_str.upper():
                                # 간단한 정규식으로 PANTONE 이름 추출 시도
                                import re
                                pantone_matches = re.findall(r'PANTONE[^)]+', obj_str, re.IGNORECASE)
                                spot_info['pantone_colors'].extend(pantone_matches)
                except (ValueError, RuntimeError, Exception) as e:
                    self.logger.debug(f"페이지 {page_num} 색상 정보 분석 실패: {e}")
                    continue
            
            doc.close()
            
            # 중복 제거
            spot_info['pages'] = sorted(set(spot_info['pages']))
            spot_info['pantone_colors'] = list(set(spot_info['pantone_colors']))
            
        except Exception as e:
            # PyMuPDF 별색 분석 중 오류 발생
            pass
        
        return spot_info
    
    def get_description(self) -> str:
        return "별색(Spot Color) 사용을 검사하고 제한을 확인합니다."


class InkCoverageRule(CheckRule):
    """잉크량 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="ink_coverage",
            category=IssueCategory.INK_COVERAGE,
            default_severity=IssueSeverity.ERROR
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """잉크량 검사"""
        # 잉크량 검사 활성화 여부 확인
        check_ink = context.profile_settings.get('ink_coverage', False)
        if not check_ink:
            return None
        
        # 잉크량 정보가 없으면 건너뛰기
        if not hasattr(analysis_result.colors, 'max_ink_coverage'):
            return None
        
        max_coverage = analysis_result.colors.max_ink_coverage
        if max_coverage <= 0:
            return None
        
        # 설정값 가져오기
        max_allowed = context.profile_settings.get('max_ink_coverage', 300)
        warning_level = context.profile_settings.get('warning_ink_coverage', 280)
        
        if max_coverage <= warning_level:
            return None
        
        # 심각도 결정
        if max_coverage > max_allowed:
            severity = IssueSeverity.ERROR
            title = "과도한 잉크량"
            description = f"최대 잉크량이 {max_coverage:.0f}%로 허용 기준({max_allowed}%)을 초과합니다."
        else:
            severity = IssueSeverity.WARNING
            title = "높은 잉크량"
            description = f"최대 잉크량이 {max_coverage:.0f}%로 경고 수준({warning_level}%)을 초과합니다."
        
        # 초과 영역 페이지 수집
        over_limit_pages = []
        if hasattr(analysis_result.colors, 'over_limit_areas'):
            for area in analysis_result.colors.over_limit_areas:
                if 'page' in area:
                    over_limit_pages.append(area['page'])
        
        over_limit_pages = sorted(set(over_limit_pages))
        
        issue = QualityIssue(
            category=self.category,
            severity=severity,
            title=title,
            description=description + " 인쇄 시 번짐이 발생할 수 있습니다.",
            pages=over_limit_pages,
            details={
                'max_coverage': max_coverage,
                'max_allowed': max_allowed,
                'warning_level': warning_level,
                'avg_coverage': analysis_result.colors.avg_ink_coverage
            }
        )
        
        issue.add_fix_option(
            method="reduce_ink_coverage",
            description="잉크량 감소 (GCR/UCR 적용)",
            parameters={'target_coverage': max_allowed - 20},
            risk_level="medium"
        )
        
        return issue
    
    def get_description(self) -> str:
        return "총 잉크량(TAC)이 인쇄 기준을 초과하는지 검사합니다."


class ColorChecker(BaseChecker):
    """
    색상 품질 검사기
    
    RGB 사용, 별색 사용, 잉크량 등을 종합적으로 검사합니다.
    """
    
    def __init__(self):
        super().__init__("Color")
    
    def _initialize_rules(self):
        """색상 관련 검사 규칙 초기화"""
        # RGB 색상 검사
        self.add_rule(RGBColorRule())
        
        # 별색 검사
        self.add_rule(SpotColorRule())
        
        # 잉크량 검사 (선택적)
        self.add_rule(InkCoverageRule())
    
    def get_description(self) -> str:
        return "색상 공간, 별색 사용, 잉크량 등 색상 관련 품질을 검사합니다."
    
    def check_print_ready(self, analysis_result: AnalysisResult) -> List[QualityIssue]:
        """
        인쇄 준비 상태 검사 (엄격 모드)
        
        Returns:
            List[QualityIssue]: 인쇄 준비와 관련된 이슈들
        """
        # 인쇄용 엄격한 설정
        context = CheckerContext(
            profile_name="print_ready",
            profile_settings={
                'check_rgb': True,
                'allow_rgb': False,  # RGB 불허
                'check_spot': True,
                'allow_spot': False,  # 별색 불허
                'spot_color_limit': 0,
                'ink_coverage': True,  # 잉크량 검사 활성화
                'max_ink_coverage': 300,
                'warning_ink_coverage': 280
            }
        )
        
        return self.check(analysis_result, context)