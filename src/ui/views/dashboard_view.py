"""
대시보드 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 dashboard/ 디렉토리에 모듈화되어 있습니다.

마이그레이션:
기존: from src.ui.views.dashboard_view import DashboardView, StatisticsManager
새로운: from src.ui.views.dashboard import DashboardView, StatisticsManager

최종 수정: 2025-01-12
"""

from .dashboard import DashboardView, StatisticsManager

# 호환성을 위한 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # generate_report 메서드 래핑 (base.py에서 quick_actions_builder로 이동)
    def generate_report(self):
        """통계 보고서 생성 (호환성)"""
        self.quick_actions_builder.generate_report()
    
    # 메서드 추가 (필요한 경우)
    if not hasattr(DashboardView, 'generate_report'):
        DashboardView.generate_report = generate_report

# 호환성 메서드 추가 실행
_add_compat_methods()

__all__ = ['DashboardView', 'StatisticsManager']