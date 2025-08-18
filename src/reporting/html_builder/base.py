# src/reporting/html_builder/base.py
"""
HTML 보고서 빌더 기본 클래스
"""

from typing import Dict, Any, Optional
from pathlib import Path

from .template_manager import TemplateManager

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..report_generator import ReportBuilder, ReportOptions
    from ...core.quality_checker import QualityCheckResult


class HTMLReportBuilder:
    """HTML 보고서 빌더 - ReportBuilder 인터페이스 구현"""
    
    def __init__(self):
        """초기화"""
        self.template_manager = TemplateManager()
    
    def build(self, 
              quality_result: 'QualityCheckResult',
              additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        HTML 보고서 생성
        
        Args:
            quality_result: 품질 검사 결과
            additional_data: 추가 데이터
            
        Returns:
            str: HTML 보고서
        """
        # 데이터 준비
        data = self.prepare_data(quality_result)
        if additional_data:
            data.update(additional_data)
        
        # HTML 생성
        html = self.template_manager.create_html_structure(data, quality_result)
        return html
    
    def get_file_extension(self) -> str:
        """파일 확장자"""
        return '.html'
    
    def prepare_data(self, quality_result: 'QualityCheckResult') -> Dict[str, Any]:
        """
        보고서용 데이터 준비
        
        Args:
            quality_result: 품질 검사 결과
            
        Returns:
            Dict: 준비된 데이터
        """
        # 기본 파일 정보
        file_info = {
            'filename': quality_result.file_path.name if quality_result.file_path else 'Unknown',
            'path': str(quality_result.file_path) if quality_result.file_path else '',
            'size': quality_result.file_path.stat().st_size if quality_result.file_path and quality_result.file_path.exists() else 0,
            'size_formatted': self._format_file_size(quality_result.file_path.stat().st_size) if quality_result.file_path and quality_result.file_path.exists() else '0 B',
            'pages': quality_result.analysis_result.document.page_count if quality_result.analysis_result else 0,
            'pdf_version': quality_result.analysis_result.document.pdf_version if quality_result.analysis_result else 'Unknown'
        }
        
        # 이슈 요약
        issue_summary = {
            'total': len(quality_result.issues),
            'errors': quality_result.error_count,
            'warnings': quality_result.warning_count,
            'info': len([i for i in quality_result.issues if i.severity.value == 'info'])
        }
        
        # 카테고리별 이슈 그룹화
        issues_by_category = {}
        for issue in quality_result.issues:
            category = issue.category.value
            if category not in issues_by_category:
                issues_by_category[category] = []
            
            # 이슈 데이터 준비
            issue_data = {
                'title': issue.category.value,
                'description': issue.description,
                'severity': issue.severity.value,
                'severity_emoji': self._get_severity_emoji(issue.severity.value),
                'pages': issue.pages,
                'suggestions': issue.suggestions,
                'is_fixable': issue.is_fixable
            }
            issues_by_category[category].append(issue_data)
        
        # 처리 시간
        processing_time = {
            'total': quality_result.processing_time,
            'analysis': getattr(quality_result, 'analysis_time', 0),
            'checking': getattr(quality_result, 'checking_time', 0)
        }
        
        return {
            'file_info': file_info,
            'quality_score': quality_result.quality_score,
            'profile': quality_result.profile_name,
            'issue_summary': issue_summary,
            'issues_by_category': issues_by_category,
            'processing_time': processing_time,
            'timestamp': quality_result.timestamp.isoformat() if quality_result.timestamp else ''
        }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """파일 크기 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _get_severity_emoji(self, severity: str) -> str:
        """심각도 이모지"""
        emoji_map = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        return emoji_map.get(severity, '❓')
    
    def save_report(self, html_content: str, output_path: Path) -> bool:
        """
        보고서 파일로 저장
        
        Args:
            html_content: HTML 콘텐츠
            output_path: 출력 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"보고서 저장 실패: {e}")
            return False