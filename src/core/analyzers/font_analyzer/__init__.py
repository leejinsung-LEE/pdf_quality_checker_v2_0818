# -*- coding: utf-8 -*-
"""
폰트 분석 모듈

PDF 파일의 폰트 정보를 분석하고 검증합니다.
"""

from .analyzer import FontAnalyzer
from .models import (
    FontAnalysisMethod,
    FontMetrics,
    FontIssue,
    PDFFontsResult,
    FontAnalysisResult,
    FontPageMapping
)
from .extractor import FontExtractor
from .external_tools import ExternalToolsManager
from .validator import FontValidator


# 공개 API
__all__ = [
    # 메인 클래스
    'FontAnalyzer',
    
    # 모델
    'FontAnalysisMethod',
    'FontMetrics',
    'FontIssue',
    'PDFFontsResult',
    'FontAnalysisResult',
    'FontPageMapping',
    
    # 컴포넌트
    'FontExtractor',
    'ExternalToolsManager',
    'FontValidator'
]