# src/reporting/html_builder/__init__.py
"""
HTML 보고서 빌더 모듈

이 모듈은 품질 검사 결과를 보기 좋은 HTML 보고서로 변환합니다:
- 스타일 관리
- 템플릿 관리
- 콘텐츠 생성
- 차트 생성
- 유틸리티 함수
"""

from typing import Dict, Any, Optional

from .base import HTMLReportBuilder as BaseHTMLReportBuilder
from .styles import StyleManager
from .template_manager import TemplateManager
from .content_builder import ContentBuilder
from .chart_generator import ChartGenerator
from .utils import ReportUtils

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..report_generator import ReportBuilder
    from ...core.quality_checker import QualityCheckResult


class HTMLReportBuilder(BaseHTMLReportBuilder):
    """
    HTML 보고서 빌더 - 통합 인터페이스
    
    ReportBuilder 인터페이스를 구현하며 기존 코드와 100% 호환됩니다.
    """
    
    def __init__(self):
        """초기화"""
        super().__init__()
        
        # 추가 구성요소 (필요시 직접 접근 가능)
        self.styles = StyleManager()
        self.charts = ChartGenerator()
        self.utils = ReportUtils()
    
    # ReportBuilder 인터페이스 구현 (base.py에서 상속)
    # - build()
    # - get_file_extension()
    # - prepare_data()
    
    # 추가 편의 메서드
    def build_print_version(self, 
                           quality_result: 'QualityCheckResult',
                           additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        인쇄용 버전 생성
        
        Args:
            quality_result: 품질 검사 결과
            additional_data: 추가 데이터
            
        Returns:
            인쇄 최적화된 HTML
        """
        data = self.prepare_data(quality_result)
        if additional_data:
            data.update(additional_data)
        
        return self.template_manager.create_print_template(data, quality_result)
    
    def build_minimal(self, 
                     quality_result: 'QualityCheckResult') -> str:
        """
        최소 버전 생성 (주요 정보만)
        
        Args:
            quality_result: 품질 검사 결과
            
        Returns:
            간소화된 HTML
        """
        data = self.prepare_data(quality_result)
        
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>품질 검사 요약</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; }}
        .score {{ font-size: 2em; font-weight: bold; }}
        .issues {{ margin-top: 20px; }}
        .issue {{ padding: 10px; margin: 5px 0; background: #f0f0f0; }}
    </style>
</head>
<body>
    <h1>{data['file_info']['filename']}</h1>
    <div class="score">품질 점수: {data['quality_score']}점</div>
    <div class="issues">
        <h2>발견된 문제: {data['issue_summary']['total']}개</h2>
        <div>오류: {data['issue_summary']['errors']}</div>
        <div>경고: {data['issue_summary']['warnings']}</div>
    </div>
</body>
</html>"""
        
        return html


# 공개 API
__all__ = [
    'HTMLReportBuilder',
    'StyleManager',
    'TemplateManager',
    'ContentBuilder',
    'ChartGenerator',
    'ReportUtils',
]