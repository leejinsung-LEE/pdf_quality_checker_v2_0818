# src/reporting/html_builder/template_manager.py
"""
HTML 템플릿 관리
"""

from typing import Dict, Any

from .styles import StyleManager
from .utils import ReportUtils
from .content_builder import ContentBuilder

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.quality_checker import QualityCheckResult


class TemplateManager:
    """HTML 템플릿 관리자"""
    
    def __init__(self):
        """초기화"""
        self.styles = StyleManager()
        self.utils = ReportUtils()
        self.content = ContentBuilder()
    
    def create_html_structure(self, data: Dict[str, Any], quality_result: 'QualityCheckResult') -> str:
        """
        완전한 HTML 구조 생성
        
        Args:
            data: 보고서 데이터
            quality_result: 품질 검사 결과
            
        Returns:
            완성된 HTML 문자열
        """
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    {self._create_head(data)}
</head>
<body>
    <div class="container">
        {self.content.create_header(data)}
        {self.content.create_summary_section(data)}
        {self.content.create_score_section(data)}
        {self.content.create_issues_section(data, quality_result)}
        {self.content.create_details_section(data, quality_result)}
        {self.content.create_footer(data)}
    </div>
    {self.utils.get_javascript_code()}
</body>
</html>"""
    
    def _create_head(self, data: Dict[str, Any]) -> str:
        """HTML head 섹션 생성"""
        return f"""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="PDF Quality Checker v2.0">
    <meta name="author" content="PDF Quality Checker">
    <meta name="description" content="PDF 품질 검사 보고서 - {data['file_info']['filename']}">
    <title>PDF 품질 검사 보고서 - {data['file_info']['filename']}</title>
    {self.styles.get_main_styles()}
    {self._get_additional_styles()}
        """
    
    def _get_additional_styles(self) -> str:
        """추가 스타일 (애니메이션 등)"""
        return """
    <style>
        /* 애니메이션 */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .section {
            opacity: 0;
            animation: fadeIn 0.6s ease forwards;
        }
        
        .section:nth-child(1) { animation-delay: 0.1s; }
        .section:nth-child(2) { animation-delay: 0.2s; }
        .section:nth-child(3) { animation-delay: 0.3s; }
        .section:nth-child(4) { animation-delay: 0.4s; }
        .section:nth-child(5) { animation-delay: 0.5s; }
        
        /* 툴팁 */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* 로딩 애니메이션 */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0,0,0,.1);
            border-radius: 50%;
            border-top-color: #007bff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
        """
    
    def create_print_template(self, data: Dict[str, Any], quality_result: 'QualityCheckResult') -> str:
        """
        인쇄용 템플릿 생성
        
        Args:
            data: 보고서 데이터
            quality_result: 품질 검사 결과
            
        Returns:
            인쇄 최적화된 HTML
        """
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>PDF 품질 검사 보고서 - {data['file_info']['filename']}</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.5;
            color: #000;
            background: white;
        }}
        
        h1 {{ font-size: 18pt; page-break-after: avoid; }}
        h2 {{ font-size: 14pt; page-break-after: avoid; }}
        h3 {{ font-size: 12pt; page-break-after: avoid; }}
        
        .page-break {{ page-break-after: always; }}
        .no-break {{ page-break-inside: avoid; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10pt 0;
        }}
        
        th, td {{
            border: 1pt solid #000;
            padding: 5pt;
            text-align: left;
        }}
        
        @page {{
            margin: 2cm;
            size: A4;
        }}
    </style>
</head>
<body>
    {self._create_print_content(data, quality_result)}
</body>
</html>"""
    
    def _create_print_content(self, data: Dict[str, Any], quality_result: 'QualityCheckResult') -> str:
        """인쇄용 콘텐츠 생성"""
        # 간소화된 인쇄용 콘텐츠
        content = f"""
        <h1>PDF 품질 검사 보고서</h1>
        <p><strong>파일:</strong> {data['file_info']['filename']}</p>
        <p><strong>검사일:</strong> {data['timestamp']}</p>
        <p><strong>품질 점수:</strong> {data['quality_score']}점</p>
        
        <h2>검사 요약</h2>
        <table>
            <tr><th>항목</th><th>값</th></tr>
            <tr><td>총 페이지</td><td>{data['file_info']['pages']}</td></tr>
            <tr><td>파일 크기</td><td>{data['file_info']['size_formatted']}</td></tr>
            <tr><td>발견된 문제</td><td>{data['issue_summary']['total']}</td></tr>
        </table>
        """
        
        if quality_result.issues:
            content += "<h2>발견된 문제</h2>"
            for issue in quality_result.issues:
                content += f"<p class='no-break'><strong>{issue.category}:</strong> {issue.description}</p>"
        
        return content