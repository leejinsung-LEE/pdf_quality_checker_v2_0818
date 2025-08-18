# src/reporting/__init__.py
"""
보고서 생성 시스템

PDF 품질 검사 결과를 다양한 형식의 보고서로 변환합니다.
"""

from .report_generator import (
    ReportGenerator,
    ReportOptions,
    ReportBuilder,
    generate_report
)

from .html_builder import HTMLReportBuilder
from .thumbnail_generator import ThumbnailGenerator

# 텍스트 빌더
try:
    from .base_builder import TextReportBuilder
    from .text_builder import SimpleTextReportBuilder
    HAS_TEXT_BUILDER = True
except ImportError:
    HAS_TEXT_BUILDER = False

# JSON 빌더는 선택적 import
try:
    from .json_builder import JSONReportBuilder
    HAS_JSON_BUILDER = True
except ImportError:
    HAS_JSON_BUILDER = False

__all__ = [
    # Report Generator
    'ReportGenerator',
    'ReportOptions',
    'ReportBuilder',
    'generate_report',
    
    # Builders
    'HTMLReportBuilder',
    
    # Utilities
    'ThumbnailGenerator',
]

# 텍스트 빌더가 있으면 추가
if HAS_TEXT_BUILDER:
    __all__.extend(['TextReportBuilder', 'SimpleTextReportBuilder'])

# JSON 빌더가 있으면 추가
if HAS_JSON_BUILDER:
    __all__.append('JSONReportBuilder')