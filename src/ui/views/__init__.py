# src/ui/views/__init__.py
"""
UI 뷰 모듈

애플리케이션의 다양한 뷰 컴포넌트들을 제공합니다.
"""

from .dashboard_view import DashboardView
from .processing_view import ProcessingView
from .history_view import HistoryView
from .process_monitor_view import ProcessMonitorView
from .unified_processing_view import UnifiedProcessingView
from .settings_view import SettingsView
from .profile_manager_view import ProfileManagerView
from .batch_process_view import BatchProcessView
from .statistics_dashboard_view import StatisticsDashboardView
from .profile_settings_view import ProfileSettingsView

__all__ = [
    'DashboardView',
    'ProcessingView',
    'HistoryView',
    'ProcessMonitorView',
    'UnifiedProcessingView',
    'SettingsView',
    'ProfileManagerView',
    'BatchProcessView',
    'StatisticsDashboardView',
    'ProfileSettingsView'
]