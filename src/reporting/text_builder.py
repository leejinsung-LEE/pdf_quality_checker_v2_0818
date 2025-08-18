# src/reporting/text_builder.py
"""
텍스트 보고서 빌더

품질 검사 결과를 읽기 쉬운 텍스트 보고서로 변환합니다.
"""

from typing import Dict, Any, Optional

from .base_builder import TextReportBuilder


# TextReportBuilder는 이미 base_builder.py에 구현되어 있으므로
# 여기서는 그대로 사용하거나 추가 기능만 구현합니다.

class SimpleTextReportBuilder(TextReportBuilder):
    """간단한 텍스트 보고서 빌더 (별칭)"""
    pass