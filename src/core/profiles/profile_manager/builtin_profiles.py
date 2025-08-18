# src/core/profiles/profile_manager/builtin_profiles.py
"""
기본 제공 프로파일 정의
"""

import copy
from typing import Dict, Any

from .models import QualityProfile


class BuiltinProfileProvider:
    """기본 제공 프로파일 제공자"""
    
    @staticmethod
    def get_default_profile() -> Dict[str, Any]:
        """기본 프로파일 데이터 반환"""
        return {
            'description': '표준 인쇄용 기본 설정',
            'quality_standards': {
                'max_ink_coverage': 300,
                'warning_ink_coverage': 280,
                'min_image_dpi': 72,
                'warning_image_dpi': 150,
                'optimal_image_dpi': 300,
                'standard_bleed_size': 3.0,
                'min_text_size': 4.0
            },
            'check_options': {
                'check_rgb': True,
                'check_spot': True,
                'allow_rgb': False,
                'allow_spot': True,
                'spot_color_limit': 2,
                'ink_coverage': False  # 기본 OFF
            },
            'color_settings': {
                'rgb_severity': 'error',
                'spot_severity': 'warning'
            },
            'enabled_rules': None,  # None이면 모든 규칙 활성화
            'rule_severities': {}  # 기본값 사용
        }
    
    @staticmethod
    def get_strict_profile() -> Dict[str, Any]:
        """엄격 모드 프로파일 데이터 반환"""
        base = BuiltinProfileProvider.get_default_profile()
        strict_profile = copy.deepcopy(base)
        
        strict_profile.update({
            'description': '고품질 인쇄를 위한 엄격한 검사',
            'quality_standards': {
                **strict_profile['quality_standards'],
                'min_image_dpi': 150,
                'warning_image_dpi': 200,
                'standard_bleed_size': 5.0,
                'min_text_size': 5.0
            },
            'check_options': {
                **strict_profile['check_options'],
                'allow_rgb': False,
                'allow_spot': False,
                'spot_color_limit': 0,
                'ink_coverage': True  # 잉크량 검사 활성화
            },
            'rule_severities': {
                'font_embedding': 'error',
                'type3_font': 'error',
                'minimum_text_size': 'error',
                'rgb_color_usage': 'error',
                'spot_color_usage': 'error',
                'ink_coverage': 'error'
            }
        })
        
        return strict_profile
    
    @staticmethod
    def get_quick_profile() -> Dict[str, Any]:
        """빠른 검사 프로파일 데이터 반환"""
        base = BuiltinProfileProvider.get_default_profile()
        quick_profile = copy.deepcopy(base)
        
        quick_profile.update({
            'description': '필수 항목만 빠르게 검사',
            'enabled_rules': [
                'font_embedding',
                'rgb_color_usage'
            ],
            'check_options': {
                **quick_profile['check_options'],
                'check_spot': False,
                'ink_coverage': False
            }
        })
        
        return quick_profile
    
    @staticmethod
    def get_web_profile() -> Dict[str, Any]:
        """웹용/디지털용 프로파일 데이터 반환"""
        base = BuiltinProfileProvider.get_default_profile()
        web_profile = copy.deepcopy(base)
        
        web_profile.update({
            'description': '웹/디지털용 PDF 검사',
            'quality_standards': {
                **web_profile['quality_standards'],
                'min_image_dpi': 72,
                'warning_image_dpi': 96,
                'optimal_image_dpi': 150,
                'standard_bleed_size': 0
            },
            'check_options': {
                **web_profile['check_options'],
                'allow_rgb': True,
                'check_spot': False
            },
            'color_settings': {
                'rgb_severity': 'info',
                'spot_severity': 'info'
            },
            'enabled_rules': [
                'font_embedding',
                'minimum_text_size'
            ]
        })
        
        return web_profile
    
    @classmethod
    def create_all_builtin_profiles(cls) -> Dict[str, QualityProfile]:
        """모든 기본 제공 프로파일 생성"""
        profiles = {}
        
        # 기본 프로파일
        profiles['default'] = QualityProfile(
            'default', 
            cls.get_default_profile(), 
            is_builtin=True
        )
        
        # 엄격 모드
        profiles['strict'] = QualityProfile(
            'strict', 
            cls.get_strict_profile(), 
            is_builtin=True
        )
        
        # 빠른 검사
        profiles['quick'] = QualityProfile(
            'quick', 
            cls.get_quick_profile(), 
            is_builtin=True
        )
        
        # 웹용
        profiles['web'] = QualityProfile(
            'web', 
            cls.get_web_profile(), 
            is_builtin=True
        )
        
        return profiles
    
    @staticmethod
    def get_empty_profile_template() -> Dict[str, Any]:
        """빈 프로파일 템플릿 반환"""
        return {
            'description': '',
            'quality_standards': {
                'max_ink_coverage': 300,
                'warning_ink_coverage': 280,
                'min_image_dpi': 72,
                'warning_image_dpi': 150,
                'optimal_image_dpi': 300,
                'standard_bleed_size': 3.0,
                'min_text_size': 4.0
            },
            'check_options': {
                'check_rgb': True,
                'check_spot': True,
                'allow_rgb': False,
                'allow_spot': True,
                'spot_color_limit': 2,
                'ink_coverage': False
            },
            'color_settings': {
                'rgb_severity': 'warning',
                'spot_severity': 'warning'
            },
            'enabled_rules': None,
            'rule_severities': {}
        }