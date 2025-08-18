# -*- coding: utf-8 -*-
"""
통계 대시보드 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 statistics_dashboard/ 디렉토리에 모듈화되어 있습니다.

최종 수정: 2025-01-12
Phase 3-D 모듈화 완료
"""

from .statistics_dashboard import StatisticsDashboardView

# 호환성을 위한 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # 원본에 있던 private 메서드들 매핑
    method_mappings = {
        # UIBuilder 메서드
        '_setup_ui': lambda self: self.ui_builder.create_ui,
        '_create_toolbar': lambda self: self.ui_builder._create_toolbar,
        '_create_content_area': lambda self: self.ui_builder._create_content_area,
        '_create_summary_cards': lambda self: self.ui_builder._create_summary_cards,
        '_create_card': lambda self: self.ui_builder._create_card,
        '_create_charts': lambda self: self.ui_builder._create_chart_area,
        '_create_recent_list': lambda self: self.ui_builder._create_recent_list,
        '_update_summary_cards': lambda self: self.ui_builder.update_summary_cards,
        '_update_recent_list': lambda self: self.ui_builder.update_recent_list,
        
        # ChartManager 메서드
        '_update_chart': lambda self: self.chart_manager.update_chart,
        
        # DataProcessor 메서드
        '_get_date_range_text': lambda self: self.data_processor.get_date_range_text,
        
        # EventHandler 메서드
        '_on_period_change': lambda self: self.on_period_change,
        '_export_statistics': lambda self: self.export_statistics,
        '_show_more_history': lambda self: self.show_more_history,
    }
    
    # 메서드 매핑 적용
    for method_name, method_func in method_mappings.items():
        if not hasattr(StatisticsDashboardView, method_name):
            setattr(StatisticsDashboardView, method_name,
                   lambda self, *args, method_func=method_func, **kwargs:
                   method_func(self)(*args, **kwargs))

# 호환성 메서드 추가 실행
_add_compat_methods()

# 모든 공개 심볼 export
__all__ = ['StatisticsDashboardView']