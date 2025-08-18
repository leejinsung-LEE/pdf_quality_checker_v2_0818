# src/reporting/html_builder/content_builder.py
"""
HTML 보고서 콘텐츠 생성
"""

from typing import Dict, Any, List
from datetime import datetime

from .utils import ReportUtils
from .chart_generator import ChartGenerator
from .styles import StyleManager

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.quality_checker import QualityCheckResult


class ContentBuilder:
    """콘텐츠 빌더"""
    
    def __init__(self):
        """초기화"""
        self.utils = ReportUtils()
        self.charts = ChartGenerator()
        self.styles = StyleManager()
    
    def create_header(self, data: Dict[str, Any]) -> str:
        """헤더 섹션 생성"""
        return f"""
        <header class="header">
            <h1>PDF 품질 검사 보고서</h1>
            <div class="subtitle">
                <strong>{data['file_info']['filename']}</strong> | 
                프로파일: {data['profile']} | 
                {datetime.fromisoformat(data['timestamp']).strftime('%Y년 %m월 %d일 %H:%M')}
            </div>
        </header>
        """
    
    def create_summary_section(self, data: Dict[str, Any]) -> str:
        """요약 섹션 생성"""
        return f"""
        <section class="section">
            <h2 class="section-title">검사 요약</h2>
            <div class="summary-cards">
                <div class="summary-card">
                    <div class="label">총 페이지</div>
                    <div class="value">{data['file_info']['pages']}</div>
                </div>
                <div class="summary-card">
                    <div class="label">파일 크기</div>
                    <div class="value">{data['file_info']['size_formatted']}</div>
                </div>
                <div class="summary-card">
                    <div class="label">발견된 문제</div>
                    <div class="value">{data['issue_summary']['total']}</div>
                </div>
                <div class="summary-card">
                    <div class="label">처리 시간</div>
                    <div class="value">{data['processing_time']['total']:.1f}초</div>
                </div>
            </div>
        </section>
        """
    
    def create_score_section(self, data: Dict[str, Any]) -> str:
        """품질 점수 섹션 생성"""
        score = data['quality_score']
        color, grade = self.styles.get_color_by_score(score)
        
        return f"""
        <section class="section quality-score">
            <h2 class="section-title">품질 점수</h2>
            {self.charts.create_score_circle(score, color)}
            <div class="score-label">품질 등급: <strong>{grade}</strong></div>
        </section>
        """
    
    def create_issues_section(self, data: Dict[str, Any], quality_result: 'QualityCheckResult') -> str:
        """이슈 섹션 생성"""
        if not quality_result.issues:
            return f"""
            <section class="section">
                <h2 class="section-title">검사 결과</h2>
                <p style="text-align: center; padding: 40px; color: #28a745; font-size: 1.2em;">
                    ✅ 발견된 문제가 없습니다!
                </p>
            </section>
            """
        
        html = """
        <section class="section">
            <h2 class="section-title">발견된 문제</h2>
        """
        
        # 심각도별 카운트 표시
        html += f"""
            <div style="margin-bottom: 30px;">
                <span class="tag error">오류 {data['issue_summary']['errors']}</span>
                <span class="tag warning">경고 {data['issue_summary']['warnings']}</span>
                <span class="tag info">정보 {data['issue_summary']['info']}</span>
            </div>
        """
        
        # 카테고리별로 이슈 표시
        for category, issues in data['issues_by_category'].items():
            html += f"""
            <div class="issue-group">
                <h3 class="issue-group-title">{self.utils.get_category_display_name(category)}</h3>
            """
            
            for issue in issues:
                html += self._create_issue_item(issue)
            
            html += '</div>'
        
        html += '</section>'
        return html
    
    def _create_issue_item(self, issue: Dict[str, Any]) -> str:
        """개별 이슈 아이템 생성"""
        severity_class = issue['severity']
        pages_text = ""
        
        if issue.get('pages'):
            pages_text = self.utils.format_pages_text(issue['pages'])
        
        html = f"""
        <div class="issue-item {severity_class}">
            <div class="issue-header">
                <span class="issue-severity">{issue['severity_emoji']}</span>
                <span class="issue-title">{issue['title']}</span>
                <span class="issue-pages">{pages_text}</span>
            </div>
            <div class="issue-description">{issue['description']}</div>
        """
        
        # 제안 사항
        if issue.get('suggestions'):
            html += '<div class="issue-suggestions">💡 '
            html += ' | '.join(issue['suggestions'])
            html += '</div>'
        
        html += '</div>'
        return html
    
    def create_details_section(self, data: Dict[str, Any], quality_result: 'QualityCheckResult') -> str:
        """상세 정보 섹션 생성"""
        analysis = quality_result.analysis_result
        
        return f"""
        <section class="section">
            <h2 class="section-title">상세 정보</h2>
            <div class="details-grid">
                {self._create_document_info_card(data, analysis)}
                {self._create_color_info_card(analysis)}
                {self._create_font_info_card(analysis)}
                {self._create_image_info_card(analysis)}
            </div>
        </section>
        """
    
    def _create_document_info_card(self, data: Dict[str, Any], analysis: Any) -> str:
        """문서 정보 카드 생성"""
        return f"""
        <div class="detail-card">
            <h3>📄 문서 정보</h3>
            <div class="detail-row">
                <span class="detail-label">PDF 버전</span>
                <span class="detail-value">{data['file_info']['pdf_version']}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">페이지 수</span>
                <span class="detail-value">{data['file_info']['pages']} 페이지</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">파일 크기</span>
                <span class="detail-value">{data['file_info']['size_formatted']}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">암호화</span>
                <span class="detail-value">{'예' if analysis.document.is_encrypted else '아니오'}</span>
            </div>
        </div>
        """
    
    def _create_color_info_card(self, analysis: Any) -> str:
        """색상 정보 카드 생성"""
        return f"""
        <div class="detail-card">
            <h3>🎨 색상 정보</h3>
            <div class="detail-row">
                <span class="detail-label">색상 공간</span>
                <span class="detail-value">{', '.join(analysis.colors.color_spaces)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">별색</span>
                <span class="detail-value">{len(analysis.colors.spot_colors)}개</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">투명도 사용</span>
                <span class="detail-value">{'예' if analysis.colors.has_transparency else '아니오'}</span>
            </div>
        </div>
        """
    
    def _create_font_info_card(self, analysis: Any) -> str:
        """폰트 정보 카드 생성"""
        total_fonts = len(analysis.fonts)
        embedded_fonts = sum(1 for f in analysis.fonts.values() if f.is_embedded)
        type3_fonts = sum(1 for f in analysis.fonts.values() if f.font_type == 'Type3')
        
        return f"""
        <div class="detail-card">
            <h3>🔤 폰트 정보</h3>
            <div class="detail-row">
                <span class="detail-label">총 폰트</span>
                <span class="detail-value">{total_fonts}개</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">임베딩</span>
                <span class="detail-value">{embedded_fonts}/{total_fonts}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Type3 폰트</span>
                <span class="detail-value">{type3_fonts}개</span>
            </div>
        </div>
        """
    
    def _create_image_info_card(self, analysis: Any) -> str:
        """이미지 정보 카드 생성"""
        total_images = len(analysis.images)
        min_dpi = min((img.dpi_x for img in analysis.images), default=0)
        formats = set(img.format for img in analysis.images) if analysis.images else set()
        
        return f"""
        <div class="detail-card">
            <h3>🖼️ 이미지 정보</h3>
            <div class="detail-row">
                <span class="detail-label">총 이미지</span>
                <span class="detail-value">{total_images}개</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">최소 해상도</span>
                <span class="detail-value">{min_dpi:.0f} DPI</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">이미지 형식</span>
                <span class="detail-value">{', '.join(formats) if formats else 'N/A'}</span>
            </div>
        </div>
        """
    
    def create_footer(self, data: Dict[str, Any]) -> str:
        """푸터 생성"""
        return f"""
        <footer style="text-align: center; padding: 30px; color: #6c757d;">
            <p>PDF Quality Checker v2.0 | 
               생성 시간: {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
        """