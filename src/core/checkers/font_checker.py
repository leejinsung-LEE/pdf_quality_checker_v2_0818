# src/core/checkers/font_checker.py
"""
폰트 품질 검사기

폰트 임베딩, Type3 폰트, 텍스트 크기 등 
폰트 관련 품질 문제를 검사합니다.
"""

from typing import Optional, List, Dict, Any
import fitz  # PyMuPDF

from .base_checker import BaseChecker, CheckRule, CheckerContext
from ..models import AnalysisResult, QualityIssue
from ..models.quality_issue import (
    IssueSeverity, IssueCategory, FixOption,
    create_font_not_embedded_issue
)


class FontEmbeddingRule(CheckRule):
    """폰트 임베딩 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="font_embedding",
            category=IssueCategory.FONT_EMBEDDING,
            default_severity=IssueSeverity.ERROR
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """폰트 임베딩 검사"""
        # 임베딩되지 않은 폰트들 찾기
        non_embedded_fonts = []
        
        for font_name, font_info in analysis_result.fonts.items():
            if font_info.needs_embedding:
                non_embedded_fonts.append({
                    'name': font_name,
                    'pages': font_info.pages_used
                })
        
        # 문제가 없으면 None 반환
        if not non_embedded_fonts:
            return None
        
        # 모든 페이지 수집
        all_pages = []
        font_names = []
        for font in non_embedded_fonts:
            all_pages.extend(font['pages'])
            font_names.append(font['name'])
        
        # 중복 제거 및 정렬
        all_pages = sorted(set(all_pages))
        
        # QualityIssue 생성
        issue = QualityIssue(
            category=self.category,
            severity=self.get_severity(context),
            title="폰트가 임베딩되지 않음",
            description=f"{len(non_embedded_fonts)}개 폰트가 PDF에 임베딩되지 않았습니다. "
                       f"다른 시스템에서 글꼴이 변경될 수 있습니다.",
            pages=all_pages,
            details={
                'count': len(non_embedded_fonts),
                'fonts': font_names,
                'font_details': non_embedded_fonts
            },
            related_objects=font_names
        )
        
        # 수정 옵션 추가
        issue.add_fix_option(
            method="embed_fonts",
            description="모든 폰트를 PDF에 임베딩",
            risk_level="low"
        )
        issue.add_fix_option(
            method="outline_text",
            description="텍스트를 아웃라인으로 변환",
            risk_level="medium"
        )
        
        return issue
    
    def get_description(self) -> str:
        return "폰트가 PDF에 임베딩되어 있는지 확인합니다."


class Type3FontRule(CheckRule):
    """Type3 폰트 사용 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="type3_font",
            category=IssueCategory.FONT_TYPE,
            default_severity=IssueSeverity.WARNING
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """Type3 폰트 검사"""
        type3_fonts = []
        
        for font_name, font_info in analysis_result.fonts.items():
            if font_info.is_type3:
                type3_fonts.append({
                    'name': font_name,
                    'pages': font_info.pages_used
                })
        
        if not type3_fonts:
            return None
        
        # 모든 페이지 수집
        all_pages = []
        font_names = []
        for font in type3_fonts:
            all_pages.extend(font['pages'])
            font_names.append(font['name'])
        
        all_pages = sorted(set(all_pages))
        
        issue = QualityIssue(
            category=self.category,
            severity=self.get_severity(context),
            title="Type3 폰트 사용",
            description=f"{len(type3_fonts)}개의 Type3 폰트가 발견되었습니다. "
                       "Type3 폰트는 인쇄 품질이 낮을 수 있습니다.",
            pages=all_pages,
            details={
                'count': len(type3_fonts),
                'fonts': font_names
            },
            related_objects=font_names
        )
        
        issue.add_fix_option(
            method="replace_type3_fonts",
            description="Type3 폰트를 TrueType/Type1으로 교체",
            risk_level="medium"
        )
        
        return issue
    
    def get_description(self) -> str:
        return "품질이 낮은 Type3 폰트 사용을 확인합니다."


class MinimumTextSizeRule(CheckRule):
    """최소 텍스트 크기 검사 규칙"""
    
    def __init__(self, min_size: float = 4.0):
        super().__init__(
            name="minimum_text_size",
            category=IssueCategory.TEXT_SIZE,
            default_severity=IssueSeverity.WARNING
        )
        self.min_size = min_size
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """최소 텍스트 크기 검사"""
        # PDF 파일 경로가 필요하므로 document에서 가져옴
        pdf_path = analysis_result.document.path
        
        small_text_info = self._analyze_text_sizes(pdf_path)
        
        if not small_text_info['has_small_text']:
            return None
        
        # 설정에서 최소 크기 가져오기
        min_size = context.profile_settings.get('min_text_size', self.min_size)
        
        issue = QualityIssue(
            category=self.category,
            severity=self.get_severity(context),
            title="작은 텍스트 발견",
            description=f"{len(small_text_info['small_text_pages'])}개 페이지에서 "
                       f"{min_size}pt 미만의 텍스트가 발견되었습니다. "
                       f"인쇄 시 가독성 문제가 발생할 수 있습니다.",
            pages=[p['page'] for p in small_text_info['small_text_pages']],
            details={
                'min_found': small_text_info['min_size_found'],
                'required_min': min_size,
                'page_details': small_text_info['small_text_pages']
            }
        )
        
        # 심각도에 따라 수정 옵션 제공
        if issue.severity == IssueSeverity.ERROR:
            issue.add_fix_option(
                method="increase_text_size",
                description=f"모든 텍스트를 최소 {min_size}pt로 조정",
                risk_level="high"
            )
        
        return issue
    
    def _analyze_text_sizes(self, pdf_path) -> Dict[str, Any]:
        """텍스트 크기 분석 (v1 로직 재사용)"""
        text_size_info = {
            'min_size_found': 999,
            'small_text_pages': [],
            'has_small_text': False
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc, 1):
                blocks = page.get_text("dict")
                page_min_size = 999
                
                for block in blocks.get("blocks", []):
                    if block.get("type") == 0:  # 텍스트 블록
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                font_size = span.get("size", 0)
                                
                                if font_size > 0:
                                    if font_size < page_min_size:
                                        page_min_size = font_size
                                    
                                    if font_size < text_size_info['min_size_found']:
                                        text_size_info['min_size_found'] = font_size
                                    
                                    if font_size < self.min_size:
                                        text_size_info['has_small_text'] = True
                                        
                                        # 페이지별로 한 번만 기록
                                        existing_pages = [p['page'] for p in text_size_info['small_text_pages']]
                                        if page_num not in existing_pages:
                                            text_size_info['small_text_pages'].append({
                                                'page': page_num,
                                                'min_size': font_size
                                            })
            
            doc.close()
            
        except Exception as e:
            # 텍스트 크기 분석 중 오류 발생
            pass
        
        return text_size_info
    
    def get_description(self) -> str:
        return f"인쇄 가독성을 위한 최소 텍스트 크기({self.min_size}pt) 검사"


class FontChecker(BaseChecker):
    """
    폰트 품질 검사기
    
    폰트 임베딩, 타입, 크기 등을 종합적으로 검사합니다.
    """
    
    def __init__(self):
        super().__init__("Font")
    
    def _initialize_rules(self):
        """폰트 관련 검사 규칙 초기화"""
        # 폰트 임베딩 검사
        self.add_rule(FontEmbeddingRule())
        
        # Type3 폰트 검사
        self.add_rule(Type3FontRule())
        
        # 최소 텍스트 크기 검사
        self.add_rule(MinimumTextSizeRule())
    
    def get_description(self) -> str:
        return "폰트 임베딩, 타입, 크기 등 폰트 관련 품질을 검사합니다."
    
    def check_with_custom_settings(self, analysis_result: AnalysisResult, 
                                  min_text_size: float = 4.0,
                                  allow_type3: bool = False) -> List[QualityIssue]:
        """
        커스텀 설정으로 검사 수행
        
        Args:
            analysis_result: 분석 결과
            min_text_size: 최소 텍스트 크기
            allow_type3: Type3 폰트 허용 여부
            
        Returns:
            List[QualityIssue]: 발견된 이슈들
        """
        # 커스텀 컨텍스트 생성
        context = CheckerContext(
            profile_settings={'min_text_size': min_text_size}
        )
        
        # Type3 검사 비활성화 옵션
        if allow_type3:
            context.enabled_rules = {'font_embedding', 'minimum_text_size'}
        
        return self.check(analysis_result, context)