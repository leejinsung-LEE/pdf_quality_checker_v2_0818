# src/reporting/report_generator/base.py
"""
보고서 생성 기본 클래스 및 데이터 모델
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.quality_checker import QualityCheckResult
    from ...core.models import QualityIssue


@dataclass
class ReportOptions:
    """보고서 생성 옵션"""
    include_summary: bool = True
    include_details: bool = True
    include_charts: bool = True
    include_thumbnails: bool = False
    max_thumbnails: int = 5
    include_fix_suggestions: bool = True
    include_metadata: bool = True
    language: str = "ko"  # 한국어
    
    # 스타일 옵션
    theme: str = "modern"  # modern, classic, minimal
    color_scheme: str = "default"


class ReportBuilder(ABC):
    """보고서 빌더 추상 클래스"""
    
    def __init__(self, options: ReportOptions):
        """
        빌더 초기화
        
        Args:
            options: 보고서 옵션
        """
        self.options = options
    
    @abstractmethod
    def build(self, 
              quality_result: 'QualityCheckResult',
              additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        보고서 생성
        
        Args:
            quality_result: 품질 검사 결과
            additional_data: 추가 데이터
            
        Returns:
            str: 생성된 보고서 내용
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """파일 확장자 반환"""
        pass
    
    def prepare_data(self, quality_result: 'QualityCheckResult') -> Dict[str, Any]:
        """
        공통 데이터 준비
        
        Args:
            quality_result: 품질 검사 결과
            
        Returns:
            준비된 데이터
        """
        analysis = quality_result.analysis_result
        
        return {
            'file_info': {
                'filename': analysis.document.filename,
                'path': str(analysis.document.path),
                'size': analysis.document.file_size,
                'size_formatted': self._format_file_size(analysis.document.file_size),
                'pages': analysis.document.page_count,
                'pdf_version': analysis.document.pdf_version,
                'created_at': analysis.document.created_at.isoformat()
            },
            'profile': quality_result.profile_name,
            'quality_score': quality_result.quality_score,
            'issue_summary': {
                'total': len(quality_result.issues),
                'errors': quality_result.error_count,
                'warnings': quality_result.warning_count,
                'info': quality_result.info_count
            },
            'issues_by_category': self._group_issues_by_category(quality_result.issues),
            'issues_by_severity': self._group_issues_by_severity(quality_result.issues),
            'processing_time': {
                'analysis': analysis.analysis_duration,
                'check': quality_result.check_duration,
                'total': analysis.analysis_duration + quality_result.check_duration
            },
            'timestamp': quality_result.timestamp.isoformat()
        }
    
    def _group_issues_by_category(self, issues: List['QualityIssue']) -> Dict[str, List[Dict]]:
        """카테고리별로 이슈 그룹화"""
        grouped = {}
        
        for issue in issues:
            category = issue.category.value
            if category not in grouped:
                grouped[category] = []
            
            grouped[category].append({
                'title': issue.title,
                'description': issue.description,
                'severity': issue.severity.value,
                'severity_emoji': issue.severity.emoji,
                'pages': issue.pages,
                'count': issue.count,
                'details': issue.details,
                'suggestions': issue.suggestions,
                'is_fixable': issue.is_fixable,
                'rule_name': issue.rule_name
            })
        
        return grouped
    
    def _group_issues_by_severity(self, issues: List['QualityIssue']) -> Dict[str, List[Dict]]:
        """심각도별로 이슈 그룹화"""
        grouped = {}
        
        for issue in issues:
            severity = issue.severity.value
            if severity not in grouped:
                grouped[severity] = []
            
            grouped[severity].append({
                'title': issue.title,
                'description': issue.description,
                'category': issue.category.value,
                'pages': issue.pages,
                'count': issue.count
            })
        
        return grouped
    
    def _format_file_size(self, size: int) -> str:
        """파일 크기 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"