# src/__init__.py
"""
PDF Quality Checker v2.0

PDF 파일의 인쇄 품질을 자동으로 검사하고 문제점을 수정하는 애플리케이션입니다.
향후 판짜기(Imposition) 기능 확장을 고려한 모듈형 설계를 적용했습니다.
"""

__version__ = "2.0.0"
__author__ = "PDF Quality Checker Team"

# 핵심 모듈
from .core import (
    # Models
    PDFDocument,
    AnalysisResult,
    QualityIssue,
    IssueSeverity,
    IssueCategory,
    
    # Analyzers
    PDFAnalyzer,
    
    # Quality Checker
    PDFQualityChecker,
    QualityCheckResult,
    check_pdf,
    quick_check_pdf,
    strict_check_pdf,
    
    # Profiles
    ProfileManager,
    QualityProfile,
    get_profile_manager
)

# 처리 시스템
from .processing import (
    PDFProcessor,
    BatchProcessor,
    FolderWatcher,
    QueueManager,
    get_processor,
    get_queue_manager,
    ProcessingResult,
    ProcessingStatus
)

# 보고서 시스템
from .reporting import (
    ReportGenerator,
    ReportOptions,
    generate_report
)

# UI (옵션)
try:
    from .ui import (
        FileController,
        SettingsController,
        ProfileController,
        ProcessingView,
        DashboardView
    )
    HAS_UI = True
except ImportError:
    HAS_UI = False

# 외부 도구
from .external import (
    ToolManager,
    get_tool_manager
)

# 설정
from .config import Config

__all__ = [
    # Version
    '__version__',
    
    # Core - Models
    'PDFDocument',
    'AnalysisResult', 
    'QualityIssue',
    'IssueSeverity',
    'IssueCategory',
    
    # Core - Analysis
    'PDFAnalyzer',
    
    # Core - Quality Check
    'PDFQualityChecker',
    'QualityCheckResult',
    'check_pdf',
    'quick_check_pdf',
    'strict_check_pdf',
    
    # Core - Profiles
    'ProfileManager',
    'QualityProfile',
    'get_profile_manager',
    
    # Processing
    'PDFProcessor',
    'BatchProcessor',
    'FolderWatcher',
    'QueueManager',
    'get_processor',
    'get_queue_manager',
    'ProcessingResult',
    'ProcessingStatus',
    
    # Reporting
    'ReportGenerator',
    'ReportOptions',
    'generate_report',
    
    # External Tools
    'ToolManager',
    'get_tool_manager',
    
    # Config
    'Config',
]

# UI는 조건부 추가
if HAS_UI:
    __all__.extend([
        'FileController',
        'SettingsController',
        'ProfileController',
        'ProcessingView',
        'DashboardView'
    ])