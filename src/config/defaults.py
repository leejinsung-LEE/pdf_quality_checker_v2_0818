# -*- coding: utf-8 -*-
"""기본 프로파일 정의"""

DEFAULT_PROFILE = {
    "name": "default",
    "description": "기본 인쇄 품질 검사 프로파일",
    "version": "1.0",
    "checks": {
        "transparency": True,
        "overprint": True,
        "spot_colors": True,
        "bleed": True,
        "fonts": True,
        "images": True,
    },
    "thresholds": {
        "min_image_dpi": 300,
        "warning_image_dpi": 200,
        "max_ink_coverage": 320,
        "standard_bleed": 3.0,
        "min_text_size": 6.0,
    }
}
