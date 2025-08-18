# src/reporting/html_builder.py
"""
HTML 보고서 빌더 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 html_builder/ 디렉토리의 모듈로 분리되었습니다.
"""

# 모든 공개 API를 재노출
from .html_builder import (
    HTMLReportBuilder,
    StyleManager,
    TemplateManager,
    ContentBuilder,
    ChartGenerator,
    ReportUtils
)

# ReportBuilder 관련 임포트 (하위 호환성)
from .report_generator import ReportBuilder, ReportOptions

__all__ = [
    'HTMLReportBuilder',
    'StyleManager',
    'TemplateManager',
    'ContentBuilder',
    'ChartGenerator',
    'ReportUtils',
    # ReportBuilder 관련 (하위 호환성)
    'ReportBuilder',
    'ReportOptions',
]

# 하위 호환성 메시지
def __getattr__(name):
    """동적 속성 접근 처리"""
    import warnings
    warnings.warn(
        f"'{name}'에 대한 직접 접근은 deprecated 되었습니다. "
        f"'from reporting.html_builder import {name}'를 사용하세요.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 모듈에서 속성 찾기
    from . import html_builder
    if hasattr(html_builder, name):
        return getattr(html_builder, name)
    
    raise AttributeError(f"module 'reporting.html_builder' has no attribute '{name}'")