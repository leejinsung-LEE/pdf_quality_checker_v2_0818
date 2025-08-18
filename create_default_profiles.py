#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기본 프로파일 생성 스크립트

PDF Quality Checker v2.0의 기본 프로파일을 생성합니다.
"""

import json
from pathlib import Path
from datetime import datetime


def create_default_profile():
    """기본 프로파일 데이터 생성"""
    return {
        "name": "default",
        "description": "표준 인쇄 품질 검사 프로파일",
        "created_at": datetime.now().isoformat(),
        "modified_at": datetime.now().isoformat(),
        "is_builtin": True,
        
        "quality_standards": {
            "min_image_dpi": 300,
            "min_line_art_dpi": 600,
            "max_ink_coverage": 320,
            "min_bleed_mm": 3.0,
            "min_font_size": 6.0
        },
        
        "check_options": {
            "check_fonts": True,
            "check_colors": True,
            "check_images": True,
            "check_layout": True,
            "check_print_settings": True,
            "require_font_embedding": True,
            "allow_rgb": False,
            "check_transparency": True,
            "check_overprint": True
        },
        
        "color_settings": {
            "preferred_color_space": "CMYK",
            "allow_spot_colors": True,
            "max_spot_colors": 4
        },
        
        "enabled_rules": [
            "font_not_embedded",
            "rgb_color_used",
            "low_resolution_image",
            "high_ink_coverage",
            "missing_bleed"
        ],
        
        "rule_severities": {
            "font_not_embedded": "error",
            "rgb_color_used": "error",
            "low_resolution_image": "warning",
            "high_ink_coverage": "warning",
            "missing_bleed": "warning"
        }
    }


def create_quick_profile():
    """빠른 검사 프로파일 데이터 생성"""
    return {
        "name": "quick",
        "description": "빠른 기본 검사 프로파일",
        "created_at": datetime.now().isoformat(),
        "modified_at": datetime.now().isoformat(),
        "is_builtin": True,
        "parent_profile": "default",
        
        "quality_standards": {
            "min_image_dpi": 150,
            "min_line_art_dpi": 300,
            "max_ink_coverage": 400,
            "min_bleed_mm": 2.0,
            "min_font_size": 4.0
        },
        
        "check_options": {
            "check_fonts": True,
            "check_colors": True,
            "check_images": False,
            "check_layout": False,
            "check_print_settings": False,
            "require_font_embedding": True,
            "allow_rgb": True,
            "check_transparency": False,
            "check_overprint": False
        },
        
        "color_settings": {
            "preferred_color_space": "CMYK",
            "allow_spot_colors": True,
            "max_spot_colors": 10
        },
        
        "enabled_rules": [
            "font_not_embedded",
            "rgb_color_used"
        ],
        
        "rule_severities": {
            "font_not_embedded": "warning",
            "rgb_color_used": "info"
        }
    }


def create_strict_profile():
    """엄격한 검사 프로파일 데이터 생성"""
    return {
        "name": "strict",
        "description": "엄격한 인쇄 품질 검사 프로파일",
        "created_at": datetime.now().isoformat(),
        "modified_at": datetime.now().isoformat(),
        "is_builtin": True,
        "parent_profile": "default",
        
        "quality_standards": {
            "min_image_dpi": 350,
            "min_line_art_dpi": 1200,
            "max_ink_coverage": 300,
            "min_bleed_mm": 5.0,
            "min_font_size": 8.0
        },
        
        "check_options": {
            "check_fonts": True,
            "check_colors": True,
            "check_images": True,
            "check_layout": True,
            "check_print_settings": True,
            "require_font_embedding": True,
            "allow_rgb": False,
            "check_transparency": True,
            "check_overprint": True
        },
        
        "color_settings": {
            "preferred_color_space": "CMYK",
            "allow_spot_colors": True,
            "max_spot_colors": 2
        },
        
        "enabled_rules": [
            "font_not_embedded",
            "rgb_color_used",
            "low_resolution_image",
            "high_ink_coverage",
            "missing_bleed",
            "small_font_size",
            "transparency_used",
            "overprint_used"
        ],
        
        "rule_severities": {
            "font_not_embedded": "error",
            "rgb_color_used": "error",
            "low_resolution_image": "error",
            "high_ink_coverage": "error",
            "missing_bleed": "error",
            "small_font_size": "warning",
            "transparency_used": "warning",
            "overprint_used": "info"
        }
    }


def main():
    """메인 함수"""
    # 프로파일 디렉토리 생성
    profiles_dir = Path("data/profiles")
    profiles_dir.mkdir(parents=True, exist_ok=True)
    
    # 프로파일 생성
    profiles = [
        create_default_profile(),
        create_quick_profile(),
        create_strict_profile()
    ]
    
    # 프로파일 저장
    for profile_data in profiles:
        profile_name = profile_data['name']
        profile_path = profiles_dir / f"{profile_name}.json"
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        print(f"[Created] Profile saved: {profile_path}")
    
    print(f"\n[Success] {len(profiles)} profiles created in {profiles_dir}")


if __name__ == "__main__":
    main()