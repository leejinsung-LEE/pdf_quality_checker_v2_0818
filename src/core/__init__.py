# src/core/__init__.py
"""PDF Quality Checker v2.0 - 핵심 모듈"""

# Models
from .models import (
    PDFDocument,
    AnalysisResult,
    QualityIssue,
    IssueSeverity,
    IssueCategory
)

# Analyzers
from .analyzers import PDFAnalyzer

# Quality Checker
from .quality_checker import (
    PDFQualityChecker,
    QualityCheckResult,
    check_pdf,
    quick_check_pdf,
    strict_check_pdf
)

# Profiles
from .profiles import (
    ProfileManager,
    QualityProfile,
    get_profile_manager
)

# Checkers
from .checkers import (
    BaseChecker,
    CompositeChecker,
    CheckerContext,
    FontChecker,
    ColorChecker,
    ImageChecker,
    LayoutChecker,
    PrintChecker
)

__all__ = [
    # Models
    'PDFDocument',
    'AnalysisResult',
    'QualityIssue',
    'IssueSeverity',
    'IssueCategory',
    
    # Analyzers
    'PDFAnalyzer',
    
    # Quality Checker
    'PDFQualityChecker',
    'QualityCheckResult',
    'check_pdf',
    'quick_check_pdf',
    'strict_check_pdf',
    
    # Profiles
    'ProfileManager',
    'QualityProfile',
    'get_profile_manager',
    
    # Checkers
    'BaseChecker',
    'CompositeChecker',
    'CheckerContext',
    'FontChecker',
    'ColorChecker',
    'ImageChecker',
    'LayoutChecker',
    'PrintChecker'
]