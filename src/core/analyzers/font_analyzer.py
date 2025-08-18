# -*- coding: utf-8 -*-
"""
PDF 폰트 분석기 - 호환성 래퍼

이 파일은 모듈화된 font_analyzer 패키지에 대한 호환성 래퍼입니다.
기존 코드와의 호환성을 유지하면서 새로운 모듈 구조를 사용합니다.
"""

# 모듈화된 컴포넌트 임포트
from .font_analyzer import (
    FontAnalyzer,
    FontAnalysisMethod,
    FontMetrics,
    FontIssue,
    PDFFontsResult,
    FontAnalysisResult,
    FontPageMapping,
    FontExtractor,
    ExternalToolsManager,
    FontValidator
)

# 공개 API
__all__ = [
    'FontAnalyzer',
    'FontAnalysisMethod',
    'FontMetrics',
    'FontIssue',
    'PDFFontsResult',
    'FontAnalysisResult',
    'FontPageMapping',
    'FontExtractor',
    'ExternalToolsManager',
    'FontValidator'
]

# 하위 호환성 유지를 위한 메시지
import logging
logger = logging.getLogger(__name__)
logger.debug("font_analyzer.py가 모듈화되었습니다. font_analyzer/ 패키지를 사용합니다.")