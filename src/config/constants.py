# -*- coding: utf-8 -*-
"""프로그램 설정 상수"""

class Config:
    """프로그램 설정 상수 - Phase 1 기본값"""
    
    # 기본 경로 설정
    INPUT_FOLDER = "input"
    OUTPUT_FOLDER = "output"
    REPORTS_FOLDER = "reports"
    COMPLETED_FOLDER = "completed"
    
    # 품질 기준 설정
    MIN_IMAGE_DPI = 300
    WARNING_IMAGE_DPI = 200
    MAX_INK_COVERAGE = 320  # 320%
    WARNING_INK_COVERAGE = 300  # 300%
    STANDARD_BLEED_SIZE = 3.0  # 3mm
    MIN_TEXT_SIZE = 6.0  # 6pt
    
    # 검사 옵션 (Phase 2에서 구현)
    CHECK_OPTIONS = {
        'transparency': True,
        'overprint': True,
        'spot_colors': True,
        'bleed': True,
        'image_compression': True,
        'minimum_text': True,
        'ink_coverage': False,
    }
