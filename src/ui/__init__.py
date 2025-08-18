# src/ui/__init__.py
"""
사용자 인터페이스 패키지

PDF Quality Checker v2의 GUI 구성요소들을 포함합니다.
MVC 패턴을 따라 controllers, views, components로 구성됩니다.
"""

# 컨트롤러
from .controllers import (
    FileController,
    SettingsController,
    ProfileController,
    get_file_controller,
    get_settings_controller,
    get_profile_controller
)

# 뷰
from .views import (
    ProcessingView,
    DashboardView
)

# 향후 추가될 메인 윈도우
try:
    from .windows import MainWindow, PDFQualityCheckerApp
    HAS_MAIN_WINDOW = True
except ImportError:
    HAS_MAIN_WINDOW = False

# 향후 추가될 컴포넌트
try:
    from .components import Sidebar, Menubar, Statusbar
    HAS_COMPONENTS = True
except ImportError:
    HAS_COMPONENTS = False

__all__ = [
    # Controllers
    'FileController',
    'SettingsController',
    'ProfileController',
    'get_file_controller',
    'get_settings_controller',
    'get_profile_controller',
    
    # Views
    'ProcessingView',
    'DashboardView',
]

# 조건부 추가
if HAS_MAIN_WINDOW:
    __all__.extend(['MainWindow', 'PDFQualityCheckerApp'])

if HAS_COMPONENTS:
    __all__.extend(['Sidebar', 'Menubar', 'Statusbar'])