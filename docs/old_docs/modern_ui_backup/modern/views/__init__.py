# src/ui/modern/views/__init__.py
"""
Modern UI 뷰들
"""

from .dashboard_view import ModernDashboardView
from .processing_view import ModernProcessingView
from .history_view import ModernHistoryView
from .folder_view import ModernFolderView
from .settings_view import ModernSettingsView

__all__ = [
    'ModernDashboardView',
    'ModernProcessingView', 
    'ModernHistoryView',
    'ModernFolderView',
    'ModernSettingsView'
]