# src/core/fixers/__init__.py
"""
PDF 자동 수정 모듈

PDF 파일의 품질 문제를 자동으로 수정하는 기능을 제공합니다.
"""

from .base_fixer import BaseFixer, FixResult, FixContext
from .color_fixer import ColorFixer
from .font_fixer import FontFixer
from .image_fixer import ImageFixer
from .auto_fixer import AutoFixer

__all__ = [
    'BaseFixer',
    'FixResult', 
    'FixContext',
    'ColorFixer',
    'FontFixer',
    'ImageFixer',
    'AutoFixer'
]