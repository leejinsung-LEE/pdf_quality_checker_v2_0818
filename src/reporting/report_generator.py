# src/reporting/report_generator.py
"""
보고서 생성 시스템 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위해 유지됩니다.
실제 구현은 report_generator/ 디렉토리의 모듈로 분리되었습니다.
"""

# 모든 공개 API를 재노출
from .report_generator import (
    ReportOptions,
    ReportBuilder,
    ReportGenerator,
    generate_report
)

# 추가 모듈 접근 (필요시)
from .report_generator.data_processor import DataProcessor
from .report_generator.format_handlers import FormatHandlerManager
from .report_generator.utils import ReportUtils

__all__ = [
    'ReportOptions',
    'ReportBuilder',
    'ReportGenerator',
    'generate_report',
    # 추가 모듈 (선택적)
    'DataProcessor',
    'FormatHandlerManager',
    'ReportUtils',
]

# 하위 호환성 메시지
def __getattr__(name):
    """동적 속성 접근 처리"""
    import warnings
    warnings.warn(
        f"'{name}'에 대한 직접 접근은 deprecated 되었습니다. "
        f"'from reporting.report_generator import {name}'를 사용하세요.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # 모듈에서 속성 찾기
    from . import report_generator
    if hasattr(report_generator, name):
        return getattr(report_generator, name)
    
    raise AttributeError(f"module 'reporting.report_generator' has no attribute '{name}'")