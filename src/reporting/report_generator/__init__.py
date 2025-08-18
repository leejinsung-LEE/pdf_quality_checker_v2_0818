# src/reporting/report_generator/__init__.py
"""
보고서 생성 시스템 모듈

이 모듈은 품질 검사 결과를 다양한 형식의 보고서로 변환합니다:
- HTML, JSON, Text 등 다양한 형식 지원
- 확장 가능한 빌더 패턴
- 데이터 처리 및 차트 생성
- 썸네일 및 수정 제안 포함
"""

from typing import Optional
from pathlib import Path

from .base import ReportOptions, ReportBuilder
from .generator import ReportGenerator
from .data_processor import DataProcessor
from .format_handlers import FormatHandlerManager
from .utils import ReportUtils

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.quality_checker import QualityCheckResult


# 공개 API
__all__ = [
    'ReportOptions',
    'ReportBuilder',
    'ReportGenerator',
    'DataProcessor',
    'FormatHandlerManager',
    'ReportUtils',
    'generate_report',  # 편의 함수
]


# 편의 함수
def generate_report(quality_result: 'QualityCheckResult',
                   format_type: str = 'html',
                   output_folder: Optional[Path] = None) -> Optional[Path]:
    """
    보고서 생성 편의 함수
    
    Args:
        quality_result: 품질 검사 결과
        format_type: 보고서 형식 (html, json, text 등)
        output_folder: 출력 폴더
        
    Returns:
        생성된 보고서 경로 또는 None
        
    Example:
        >>> from core.quality_checker import check_pdf_quality
        >>> result = check_pdf_quality("sample.pdf")
        >>> report_path = generate_report(result, 'html')
        >>> print(f"보고서 생성: {report_path}")
    """
    generator = ReportGenerator()
    return generator.generate(quality_result, format_type, output_folder)