# -*- coding: utf-8 -*-
"""
프로파일 상세 설정 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 profile_settings/ 디렉토리에 모듈화되어 있습니다.

최종 수정: 2025-01-12
"""

from .profile_settings import ProfileSettingsView

# 호환성을 위한 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # 원본에 있던 속성들을 직접 접근 가능하도록 매핑
    original_attrs = [
        'profile_listbox', 'settings_frame', 'settings_title', 'tabview',
        'name_entry', 'desc_text', 'parent_menu', 'save_btn', 'revert_btn',
        'min_dpi_var', 'min_dpi_slider', 'min_dpi_label',
        'bleed_var', 'bleed_slider', 'bleed_label',
        'min_text_var', 'min_text_slider', 'min_text_label',
        'check_vars', 'max_ink_var', 'max_ink_slider', 'max_ink_label',
        'allow_rgb_var', 'check_spot_var', 'color_profile_menu',
        'require_embed_var', 'allow_type3_var', 'allow_subset_var',
        'jpeg_quality_var', 'jpeg_quality_slider', 'jpeg_quality_label',
        'allow_resample_var', 'pdf_version_menu', 'check_metadata_var',
        'autofix_vars'
    ]
    
    # 속성 접근자 생성
    def make_property(attr_name):
        def getter(self):
            # widgets 딕셔너리에서 먼저 찾기
            if hasattr(self, 'widgets') and attr_name in self.widgets:
                return self.widgets[attr_name]
            # vars 딕셔너리에서 찾기
            if hasattr(self, 'vars') and attr_name in self.vars:
                return self.vars[attr_name]
            # 직접 속성에서 찾기
            if hasattr(self, f'_{attr_name}'):
                return getattr(self, f'_{attr_name}')
            return None
            
        def setter(self, value):
            if hasattr(self, 'widgets') and attr_name in ['profile_listbox', 'settings_frame', 
                                                          'settings_title', 'tabview', 'name_entry',
                                                          'desc_text', 'parent_menu', 'save_btn', 
                                                          'revert_btn', 'color_profile_menu',
                                                          'pdf_version_menu']:
                self.widgets[attr_name] = value
            elif hasattr(self, 'vars'):
                self.vars[attr_name] = value
            else:
                setattr(self, f'_{attr_name}', value)
                
        return property(getter, setter)
    
    # 모든 속성에 대해 property 생성
    for attr in original_attrs:
        if not hasattr(ProfileSettingsView, attr):
            setattr(ProfileSettingsView, attr, make_property(attr))

_add_compat_methods()

__all__ = ['ProfileSettingsView']