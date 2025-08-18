# src/reporting/base_builder.py
"""
기본 보고서 빌더

텍스트 기반 보고서 빌더의 공통 기능을 제공합니다.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .report_generator import ReportBuilder, ReportOptions
from ..core.quality_checker import QualityCheckResult
from ..core.models import QualityIssue
from ..core.models.quality_issue import IssueSeverity, IssueCategory


class BaseTextBuilder(ReportBuilder):
    """텍스트 기반 보고서 빌더 기본 클래스"""
    
    def format_header(self, title: str, char: str = '=', width: int = 80) -> str:
        """헤더 포맷팅"""
        line = char * width
        return f"\n{line}\n{title.center(width)}\n{line}\n"
    
    def format_section(self, title: str, char: str = '-', width: int = 80) -> str:
        """섹션 헤더 포맷팅"""
        return f"\n{title}\n{char * len(title)}\n"
    
    def format_key_value(self, key: str, value: Any, indent: int = 0) -> str:
        """키-값 쌍 포맷팅"""
        indent_str = ' ' * indent
        return f"{indent_str}{key}: {value}"
    
    def format_issue_text(self, issue: Dict[str, Any], index: int) -> str:
        """이슈 텍스트 포맷팅"""
        lines = []
        
        # 헤더
        lines.append(f"\n{index}. [{issue['severity'].upper()}] {issue['title']}")
        
        # 설명
        lines.append(f"   설명: {issue['description']}")
        
        # 페이지
        if issue.get('pages'):
            pages_str = ', '.join(map(str, issue['pages'][:20]))
            if len(issue['pages']) > 20:
                pages_str += f" 외 {len(issue['pages']) - 20}개"
            lines.append(f"   페이지: {pages_str}")
        
        # 개수
        if issue.get('count'):
            lines.append(f"   발생 횟수: {issue['count']}회")
        
        # 제안사항
        if issue.get('suggestions'):
            lines.append("   제안사항:")
            for suggestion in issue['suggestions']:
                lines.append(f"     - {suggestion}")
        
        return '\n'.join(lines)
    
    def format_summary_table(self, data: Dict[str, Any]) -> str:
        """요약 테이블 포맷팅"""
        lines = []
        
        # 파일 정보
        lines.append("파일 정보:")
        lines.append(f"  - 파일명: {data['file_info']['filename']}")
        lines.append(f"  - 크기: {data['file_info']['size_formatted']}")
        lines.append(f"  - 페이지: {data['file_info']['pages']} 페이지")
        lines.append(f"  - PDF 버전: {data['file_info']['pdf_version']}")
        
        # 검사 정보
        lines.append("\n검사 정보:")
        lines.append(f"  - 프로파일: {data['profile']}")
        lines.append(f"  - 품질 점수: {data['quality_score']}/100")
        lines.append(f"  - 검사 시간: {data['processing_time']['total']:.2f}초")
        
        # 이슈 요약
        lines.append("\n이슈 요약:")
        lines.append(f"  - 총 이슈: {data['issue_summary']['total']}개")
        lines.append(f"  - 오류: {data['issue_summary']['errors']}개")
        lines.append(f"  - 경고: {data['issue_summary']['warnings']}개")
        lines.append(f"  - 정보: {data['issue_summary']['info']}개")
        
        return '\n'.join(lines)
    
    def format_detailed_info(self, quality_result: QualityCheckResult) -> str:
        """상세 정보 포맷팅"""
        lines = []
        analysis = quality_result.analysis_result
        
        # 페이지 정보
        lines.append("페이지 정보:")
        page_sizes = {}
        for page in analysis.pages:
            size_key = f"{page.width_mm:.0f}x{page.height_mm:.0f}mm"
            page_sizes[size_key] = page_sizes.get(size_key, 0) + 1
        
        for size, count in page_sizes.items():
            lines.append(f"  - {size}: {count} 페이지")
        
        # 폰트 정보
        lines.append("\n폰트 정보:")
        lines.append(f"  - 총 폰트: {len(analysis.fonts)}개")
        embedded_count = sum(1 for f in analysis.fonts.values() if f.is_embedded)
        lines.append(f"  - 임베딩된 폰트: {embedded_count}/{len(analysis.fonts)}")
        
        # 주요 폰트 목록
        if analysis.fonts:
            lines.append("  - 사용된 폰트:")
            for name, font in list(analysis.fonts.items())[:5]:
                embed_status = "임베딩됨" if font.is_embedded else "누락"
                lines.append(f"    * {name} ({font.font_type}) - {embed_status}")
            if len(analysis.fonts) > 5:
                lines.append(f"    ... 외 {len(analysis.fonts) - 5}개")
        
        # 색상 정보
        lines.append("\n색상 정보:")
        lines.append(f"  - 색상 공간: {', '.join(analysis.colors.color_spaces)}")
        lines.append(f"  - 별색: {len(analysis.colors.spot_colors)}개")
        if analysis.colors.spot_colors:
            lines.append(f"    {', '.join(list(analysis.colors.spot_colors)[:5])}")
            if len(analysis.colors.spot_colors) > 5:
                lines.append(f"    ... 외 {len(analysis.colors.spot_colors) - 5}개")
        
        # 이미지 정보
        if analysis.images:
            lines.append("\n이미지 정보:")
            lines.append(f"  - 총 이미지: {len(analysis.images)}개")
            
            # 해상도 분포
            dpi_ranges = {'low': 0, 'medium': 0, 'high': 0}
            for img in analysis.images:
                if img.dpi_x < 150:
                    dpi_ranges['low'] += 1
                elif img.dpi_x < 300:
                    dpi_ranges['medium'] += 1
                else:
                    dpi_ranges['high'] += 1
            
            lines.append("  - 해상도 분포:")
            lines.append(f"    * 150 DPI 미만: {dpi_ranges['low']}개")
            lines.append(f"    * 150-300 DPI: {dpi_ranges['medium']}개")
            lines.append(f"    * 300 DPI 이상: {dpi_ranges['high']}개")
        
        return '\n'.join(lines)


class TextReportBuilder(BaseTextBuilder):
    """텍스트 보고서 빌더"""
    
    def build(self, 
              quality_result: QualityCheckResult,
              additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        텍스트 보고서 생성
        
        Args:
            quality_result: 품질 검사 결과
            additional_data: 추가 데이터
            
        Returns:
            str: 텍스트 보고서
        """
        # 데이터 준비
        data = self.prepare_data(quality_result)
        
        # 보고서 생성
        lines = []
        
        # 헤더
        lines.append(self.format_header("PDF 품질 검사 보고서"))
        lines.append(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 요약
        lines.append(self.format_section("검사 요약"))
        lines.append(self.format_summary_table(data))
        
        # 발견된 이슈
        if quality_result.issues:
            lines.append(self.format_section("발견된 문제"))
            
            # 심각도별 그룹화
            by_severity = data['issues_by_severity']
            
            issue_index = 1
            for severity in ['error', 'warning', 'info']:
                if severity in by_severity:
                    lines.append(f"\n[{severity.upper()}]")
                    for issue in by_severity[severity]:
                        lines.append(self.format_issue_text(issue, issue_index))
                        issue_index += 1
        else:
            lines.append(self.format_section("검사 결과"))
            lines.append("✅ 발견된 문제가 없습니다!")
        
        # 상세 정보 (옵션)
        if self.options.include_details:
            lines.append(self.format_section("상세 정보"))
            lines.append(self.format_detailed_info(quality_result))
        
        # 푸터
        lines.append(self.format_header("", char='-'))
        lines.append("PDF Quality Checker v2.0")
        
        return '\n'.join(lines)
    
    def get_file_extension(self) -> str:
        """파일 확장자"""
        return '.txt'