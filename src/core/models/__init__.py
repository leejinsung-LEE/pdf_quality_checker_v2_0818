# -*- coding: utf-8 -*-
"""
PDF Quality Checker v2.0 - 데이터 모델 패키지

이 패키지는 PDF 분석에 사용되는 모든 데이터 모델을 포함합니다.
"""

# PDF 문서 관련 모델
from .pdf_document import (
    PDFDocument,
    PageInfo,
    PageSize,
    Rectangle,
    BleedInfo,
    PaperSize
)

# 분석 결과 관련 모델
from .analysis_result import (
    AnalysisResult,
    FontInfo,
    ColorInfo,
    ImageInfo,
    ColorSpace,
    FontType,
    ImpositionReadiness
)

# 품질 이슈 관련 모델
from .quality_issue import (
    QualityIssue,
    IssueSeverity,
    IssueCategory,
    FixOption,
    create_font_not_embedded_issue,
    create_rgb_color_issue,
    create_low_resolution_image_issue,
    create_high_ink_coverage_issue,
    create_missing_bleed_issue
)

# 패키지 레벨에서 접근 가능한 모든 클래스들
__all__ = [
    # PDF 문서
    'PDFDocument',
    'PageInfo',
    'PageSize',
    'Rectangle',
    'BleedInfo',
    'PaperSize',
    
    # 분석 결과
    'AnalysisResult',
    'FontInfo',
    'ColorInfo',
    'ImageInfo',
    'ColorSpace',
    'FontType',
    'ImpositionReadiness',
    
    # 품질 이슈
    'QualityIssue',
    'IssueSeverity',
    'IssueCategory',
    'FixOption',
    
    # 팩토리 함수들
    'create_font_not_embedded_issue',
    'create_rgb_color_issue',
    'create_low_resolution_image_issue',
    'create_high_ink_coverage_issue',
    'create_missing_bleed_issue',
]