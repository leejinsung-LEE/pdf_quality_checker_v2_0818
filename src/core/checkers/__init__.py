# src/core/checkers/__init__.py
"""
PDF 품질 검사기 모듈

규칙 기반으로 PDF 품질 문제를 검출하는 검사기들을 제공합니다.
"""

from .base_checker import BaseChecker, CheckRule, CheckerContext, CompositeChecker
from .font_checker import FontChecker, FontEmbeddingRule, Type3FontRule, MinimumTextSizeRule
from .color_checker import ColorChecker, RGBColorRule, SpotColorRule, InkCoverageRule
from .image_checker import ImageChecker, ImageResolutionRule, ImageCompressionRule, ImageColorModeRule
from .layout_checker import LayoutChecker, BleedCheckRule, NonUniformBleedRule, LargeFormatBleedRule
from .print_checker import PrintChecker, OverprintRule, WhiteOverprintRule
from .advanced_checker import AdvancedChecker

__all__ = [
    # Base classes
    'BaseChecker',
    'CheckRule',
    'CheckerContext',
    'CompositeChecker',
    
    # Font checker
    'FontChecker',
    'FontEmbeddingRule',
    'Type3FontRule',
    'MinimumTextSizeRule',
    
    # Color checker
    'ColorChecker',
    'RGBColorRule',
    'SpotColorRule',
    'InkCoverageRule',
    
    # Image checker
    'ImageChecker',
    'ImageResolutionRule',
    'ImageCompressionRule',
    'ImageColorModeRule',
    
    # Layout checker
    'LayoutChecker',
    'BleedCheckRule',
    'NonUniformBleedRule',
    'LargeFormatBleedRule',
    
    # Print checker
    'PrintChecker',
    'OverprintRule',
    'WhiteOverprintRule',
    
    # Advanced checker
    'AdvancedChecker',
]


def create_default_checker() -> CompositeChecker:
    """기본 품질 검사기 생성"""
    checker = CompositeChecker()
    checker.add_checker(FontChecker())
    checker.add_checker(ColorChecker())
    checker.add_checker(ImageChecker())
    checker.add_checker(LayoutChecker())
    checker.add_checker(PrintChecker())
    checker.add_checker(AdvancedChecker())
    return checker


def create_quick_checker() -> CompositeChecker:
    """빠른 검사용 검사기 생성 (필수 항목만)"""
    checker = CompositeChecker()
    checker.add_checker(FontChecker())
    checker.add_checker(ColorChecker())
    return checker


def create_print_ready_checker() -> CompositeChecker:
    """인쇄 준비 검사기 생성 (모든 항목 엄격히)"""
    checker = CompositeChecker()
    checker.add_checker(FontChecker())
    checker.add_checker(ColorChecker())
    checker.add_checker(ImageChecker())
    checker.add_checker(LayoutChecker())
    checker.add_checker(PrintChecker())
    checker.add_checker(AdvancedChecker())
    return checker