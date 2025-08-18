# -*- coding: utf-8 -*-
"""
폰트 분석 데이터 모델

폰트 분석과 관련된 데이터 구조를 정의합니다.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from enum import Enum


class FontAnalysisMethod(Enum):
    """폰트 분석 방법"""
    PIKEPDF = "pikepdf"
    PDFFONTS = "pdffonts"
    COMBINED = "combined"


@dataclass
class FontMetrics:
    """폰트 메트릭 정보"""
    name: str
    glyph_count: int = 0
    character_count: int = 0
    avg_width: float = 0.0
    avg_height: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'name': self.name,
            'glyph_count': self.glyph_count,
            'character_count': self.character_count,
            'avg_width': self.avg_width,
            'avg_height': self.avg_height
        }


@dataclass
class FontIssue:
    """폰트 관련 문제"""
    type: str  # missing_embedding, type3_font, encoding_issue 등
    font: str
    severity: str  # error, warning, info
    description: str = ""
    pages: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'type': self.type,
            'font': self.font,
            'severity': self.severity,
            'description': self.description,
            'pages': self.pages
        }


@dataclass
class PDFFontsResult:
    """pdffonts 도구 분석 결과"""
    fonts: Dict[str, Dict[str, Any]]
    raw_output: str = ""
    error_message: Optional[str] = None
    execution_time: float = 0.0
    
    @property
    def success(self) -> bool:
        """분석 성공 여부"""
        return self.error_message is None
        
    @property
    def font_count(self) -> int:
        """폰트 개수"""
        return len(self.fonts)


@dataclass
class FontAnalysisResult:
    """폰트 분석 최종 결과"""
    fonts: Dict[str, Any]  # FontInfo 객체들
    total_fonts: int
    embedded_fonts: int
    missing_fonts: int
    subset_fonts: int
    type3_fonts: int
    font_issues: List[FontIssue]
    analysis_method: FontAnalysisMethod
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'fonts': self.fonts,
            'total_fonts': self.total_fonts,
            'embedded_fonts': self.embedded_fonts,
            'missing_fonts': self.missing_fonts,
            'subset_fonts': self.subset_fonts,
            'type3_fonts': self.type3_fonts,
            'font_issues': [issue.to_dict() for issue in self.font_issues],
            'analysis_method': self.analysis_method.value,
            'warnings': self.warnings
        }
        
    def has_issues(self) -> bool:
        """문제가 있는지 확인"""
        return len(self.font_issues) > 0
        
    def get_critical_issues(self) -> List[FontIssue]:
        """심각한 문제만 반환"""
        return [issue for issue in self.font_issues if issue.severity == 'error']


@dataclass
class FontPageMapping:
    """폰트-페이지 매핑 정보"""
    font_to_pages: Dict[str, List[int]]
    page_to_fonts: Dict[int, Set[str]]
    
    def get_fonts_for_page(self, page_num: int) -> Set[str]:
        """특정 페이지의 폰트 목록"""
        return self.page_to_fonts.get(page_num, set())
        
    def get_pages_for_font(self, font_name: str) -> List[int]:
        """특정 폰트가 사용된 페이지 목록"""
        return self.font_to_pages.get(font_name, [])
        
    def get_most_used_font(self) -> Optional[str]:
        """가장 많이 사용된 폰트"""
        if not self.font_to_pages:
            return None
        return max(self.font_to_pages.items(), key=lambda x: len(x[1]))[0]