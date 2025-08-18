# src/reporting/report_generator/data_processor.py
"""
보고서용 데이터 처리 및 준비
"""

from typing import Dict, Any, List, Optional
import logging

from .base import ReportOptions

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.quality_checker import QualityCheckResult
    from ...core.models import QualityIssue
    from ...core.models.quality_issue import IssueCategory


class DataProcessor:
    """보고서 데이터 처리기"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 썸네일 생성기 (지연 로딩)
        self._thumbnail_generator = None
    
    def prepare_additional_data(self, 
                               quality_result: 'QualityCheckResult',
                               options: ReportOptions) -> Dict[str, Any]:
        """
        추가 데이터 준비
        
        Args:
            quality_result: 품질 검사 결과
            options: 보고서 옵션
            
        Returns:
            추가 데이터 딕셔너리
        """
        data = {}
        
        # 썸네일 생성
        if options.include_thumbnails:
            thumbnails = self._generate_thumbnails(
                quality_result,
                options.max_thumbnails
            )
            if thumbnails:
                data['thumbnails'] = thumbnails
        
        # 수정 제안
        if options.include_fix_suggestions:
            suggestions = self._generate_fix_suggestions(quality_result)
            if suggestions:
                data['fix_suggestions'] = suggestions
        
        # 차트 데이터
        if options.include_charts:
            data['chart_data'] = self._prepare_chart_data(quality_result)
        
        # 메타데이터
        if options.include_metadata:
            data['metadata'] = self._prepare_metadata(quality_result)
        
        return data
    
    def _generate_thumbnails(self, 
                           quality_result: 'QualityCheckResult',
                           max_count: int) -> Optional[Dict[str, Any]]:
        """
        썸네일 생성
        
        Args:
            quality_result: 품질 검사 결과
            max_count: 최대 썸네일 개수
            
        Returns:
            썸네일 데이터
        """
        if not self._thumbnail_generator:
            try:
                from ..thumbnail_generator import ThumbnailGenerator
                self._thumbnail_generator = ThumbnailGenerator()
            except ImportError:
                self.logger.warning("썸네일 생성기를 찾을 수 없습니다")
                return None
        
        try:
            pdf_path = quality_result.analysis_result.document.path
            
            # 문제가 있는 페이지 찾기
            problem_pages = set()
            for issue in quality_result.issues:
                if issue.pages:
                    problem_pages.update(issue.pages)
            
            # 썸네일 생성
            thumbnails = self._thumbnail_generator.generate_for_report(
                pdf_path,
                list(problem_pages)[:max_count],
                quality_result.analysis_result.document.page_count
            )
            
            return thumbnails
            
        except Exception as e:
            self.logger.error(f"썸네일 생성 실패: {e}")
            return None
    
    def _generate_fix_suggestions(self, quality_result: 'QualityCheckResult') -> List[Dict[str, Any]]:
        """
        수정 제안 생성
        
        Args:
            quality_result: 품질 검사 결과
            
        Returns:
            수정 제안 목록
        """
        suggestions = []
        
        # 수정 가능한 이슈 찾기
        fixable_issues = [issue for issue in quality_result.issues if issue.is_fixable]
        
        # 카테고리별로 그룹화
        by_category = {}
        for issue in fixable_issues:
            category = issue.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(issue)
        
        # 카테고리별 제안 생성
        for category, issues in by_category.items():
            suggestion = {
                'category': category,
                'issue_count': len(issues),
                'actions': self._get_fix_actions(category, issues)
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def _get_fix_actions(self, category: str, issues: List['QualityIssue']) -> List[Dict[str, Any]]:
        """
        카테고리별 수정 액션 생성
        
        Args:
            category: 이슈 카테고리
            issues: 이슈 목록
            
        Returns:
            수정 액션 목록
        """
        actions = []
        
        # 카테고리별 수정 액션 매핑
        action_map = {
            'color_space': {
                'type': 'convert_colors',
                'description': 'RGB 색상을 CMYK로 변환',
                'auto_fixable': True
            },
            'font_embedding': {
                'type': 'embed_fonts',
                'description': '누락된 폰트 임베딩',
                'auto_fixable': True
            },
            'image_quality': {
                'type': 'optimize_images',
                'description': '이미지 해상도 최적화',
                'auto_fixable': True
            },
            'ink_coverage': {
                'type': 'reduce_ink',
                'description': '잉크 사용량 감소',
                'auto_fixable': False
            },
            'transparency': {
                'type': 'flatten_transparency',
                'description': '투명도 평탄화',
                'auto_fixable': True
            }
        }
        
        if category in action_map:
            actions.append(action_map[category])
        
        # 이슈별 구체적인 액션 추가
        for issue in issues[:3]:  # 최대 3개까지만
            if issue.suggestions:
                for suggestion in issue.suggestions[:2]:  # 제안당 최대 2개
                    actions.append({
                        'type': 'manual',
                        'description': suggestion,
                        'auto_fixable': False
                    })
        
        return actions
    
    def _prepare_chart_data(self, quality_result: 'QualityCheckResult') -> Dict[str, Any]:
        """
        차트 데이터 준비
        
        Args:
            quality_result: 품질 검사 결과
            
        Returns:
            차트 데이터
        """
        # 심각도별 카운트
        severity_data = {
            'labels': ['오류', '경고', '정보'],
            'values': [
                quality_result.error_count,
                quality_result.warning_count,
                quality_result.info_count
            ],
            'colors': ['#dc3545', '#ffc107', '#17a2b8']
        }
        
        # 카테고리별 카운트
        category_counts = {}
        for issue in quality_result.issues:
            category = issue.category.get_display_name()
            category_counts[category] = category_counts.get(category, 0) + 1
        
        category_data = {
            'labels': list(category_counts.keys()),
            'values': list(category_counts.values())
        }
        
        # 페이지별 이슈 분포
        page_issues = {}
        for issue in quality_result.issues:
            if issue.pages:
                for page in issue.pages:
                    page_issues[page] = page_issues.get(page, 0) + 1
        
        page_data = {
            'pages': list(page_issues.keys()),
            'counts': list(page_issues.values())
        }
        
        return {
            'severity': severity_data,
            'category': category_data,
            'pages': page_data,
            'quality_score': {
                'value': quality_result.quality_score,
                'color': self._get_score_color(quality_result.quality_score)
            }
        }
    
    def _get_score_color(self, score: float) -> str:
        """점수에 따른 색상 반환"""
        if score >= 90:
            return '#28a745'
        elif score >= 70:
            return '#ffc107'
        elif score >= 50:
            return '#fd7e14'
        else:
            return '#dc3545'
    
    def _prepare_metadata(self, quality_result: 'QualityCheckResult') -> Dict[str, Any]:
        """
        메타데이터 준비
        
        Args:
            quality_result: 품질 검사 결과
            
        Returns:
            메타데이터
        """
        analysis = quality_result.analysis_result
        
        return {
            'document': {
                'producer': analysis.document.producer,
                'creator': analysis.document.creator,
                'creation_date': analysis.document.created_at.isoformat() if analysis.document.created_at else None,
                'modification_date': analysis.document.modified_at.isoformat() if analysis.document.modified_at else None,
                'is_encrypted': analysis.document.is_encrypted,
                'is_tagged': analysis.document.is_tagged
            },
            'fonts': {
                'total': len(analysis.fonts),
                'embedded': sum(1 for f in analysis.fonts.values() if f.is_embedded),
                'subset': sum(1 for f in analysis.fonts.values() if f.is_subset),
                'type3': sum(1 for f in analysis.fonts.values() if f.font_type == 'Type3')
            },
            'images': {
                'total': len(analysis.images),
                'formats': list(set(img.format for img in analysis.images))
            },
            'colors': {
                'color_spaces': list(analysis.colors.color_spaces),
                'spot_colors': len(analysis.colors.spot_colors),
                'has_transparency': analysis.colors.has_transparency
            }
        }