"""
대시보드 뷰 모듈

PDF 처리 통계와 분석 정보를 시각적으로 표시하는 대시보드입니다.
실시간 통계, 차트, 주요 지표를 제공합니다.

최종 수정: 2025-01-12
"""

from .base import DashboardView
from .stats_manager import StatisticsManager

__all__ = ['DashboardView', 'StatisticsManager']