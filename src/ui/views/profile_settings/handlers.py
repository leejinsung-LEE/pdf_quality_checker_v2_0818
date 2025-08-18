"""
프로파일 설정 이벤트 핸들러
기능: 설정 변경, 저장, 로드 등 이벤트 처리
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import ProfileSettingsView


class EventHandler:
    """이벤트 처리 헬퍼 클래스"""
    
    def __init__(self, view: 'ProfileSettingsView'):
        self.view = view
        
    def on_profile_select(self, event):
        """프로파일 선택 이벤트"""
        if 'profile_listbox' not in self.view.widgets:
            return
            
        selection = self.view.widgets['profile_listbox'].curselection()
        if not selection:
            return
            
        # 수정사항 확인
        if self.view.modified:
            if not messagebox.askyesno("확인", "저장하지 않은 변경사항이 있습니다. 계속하시겠습니까?"):
                return
                
        # 선택된 프로파일 이름 추출
        profile_text = self.view.widgets['profile_listbox'].get(selection[0])
        profile_name = profile_text.split(" ")[0]
        
        self.load_profile_settings(profile_name)
        
    def load_profile_settings(self, profile_name: str):
        """프로파일 설정 로드"""
        self.view.current_profile_name = profile_name
        profile = self.view.profile_manager.get_profile(profile_name)
        
        if not profile:
            return
            
        # 기본 정보
        if 'settings_title' in self.view.widgets:
            self.view.widgets['settings_title'].configure(text=f"프로파일 설정: {profile_name}")
            
        if 'name_entry' in self.view.widgets:
            self.view.widgets['name_entry'].delete(0, tk.END)
            self.view.widgets['name_entry'].insert(0, profile_name)
        
        # 설명
        if 'desc_text' in self.view.widgets:
            self.view.widgets['desc_text'].delete("1.0", tk.END)
            self.view.widgets['desc_text'].insert("1.0", profile.get_description())
        
        # 부모 프로파일
        if 'parent_menu' in self.view.widgets:
            parent = profile.parent_profile or "없음"
            self.view.widgets['parent_menu'].set(parent)
        
        # 품질 기준
        standards = profile.data.get('quality_standards', {})
        if 'min_dpi_var' in self.view.vars:
            self.view.vars['min_dpi_var'].set(standards.get('minimum_dpi', 300))
        if 'bleed_var' in self.view.vars:
            self.view.vars['bleed_var'].set(standards.get('standard_bleed_size', 3.0))
        if 'min_text_var' in self.view.vars:
            self.view.vars['min_text_var'].set(standards.get('minimum_text_size', 6.0))
        if 'max_ink_var' in self.view.vars:
            self.view.vars['max_ink_var'].set(standards.get('max_ink_coverage', 320))
        
        # 검사 옵션
        options = profile.data.get('check_options', {})
        if 'check_vars' in self.view.vars:
            for key, var in self.view.vars['check_vars'].items():
                var.set(options.get(key, True))
                
        # 색상 설정
        if 'allow_rgb_var' in self.view.vars:
            self.view.vars['allow_rgb_var'].set(options.get('allow_rgb', False))
        if 'check_spot_var' in self.view.vars:
            self.view.vars['check_spot_var'].set(options.get('check_spot', True))
        
        # 폰트 설정
        if 'require_embed_var' in self.view.vars:
            self.view.vars['require_embed_var'].set(options.get('require_font_embedding', True))
        if 'allow_type3_var' in self.view.vars:
            self.view.vars['allow_type3_var'].set(options.get('allow_type3_fonts', False))
        if 'allow_subset_var' in self.view.vars:
            self.view.vars['allow_subset_var'].set(options.get('allow_subset_fonts', True))
        
        # 이미지 설정
        if 'jpeg_quality_var' in self.view.vars:
            self.view.vars['jpeg_quality_var'].set(standards.get('jpeg_quality', 85))
        if 'allow_resample_var' in self.view.vars:
            self.view.vars['allow_resample_var'].set(options.get('allow_image_resampling', False))
        
        # 고급 설정
        if 'check_metadata_var' in self.view.vars:
            self.view.vars['check_metadata_var'].set(options.get('check_metadata', True))
        
        # 자동 수정 옵션
        autofix = profile.data.get('autofix_options', {})
        if 'autofix_vars' in self.view.vars:
            for key, var in self.view.vars['autofix_vars'].items():
                var.set(autofix.get(key, False))
                
        # 슬라이더 레이블 업데이트
        self.update_slider_labels()
        
        # 편집 가능 여부
        is_builtin = profile.is_builtin
        state = "disabled" if is_builtin else "normal"
        
        if 'name_entry' in self.view.widgets:
            self.view.widgets['name_entry'].configure(state=state)
        if 'save_btn' in self.view.widgets:
            self.view.widgets['save_btn'].configure(state="disabled")
        if 'revert_btn' in self.view.widgets:
            self.view.widgets['revert_btn'].configure(state="disabled")
        
        self.view.modified = False
        
    def update_slider_labels(self):
        """슬라이더 레이블 업데이트"""
        if 'min_dpi_label' in self.view.widgets and 'min_dpi_var' in self.view.vars:
            self.view.widgets['min_dpi_label'].configure(text=str(self.view.vars['min_dpi_var'].get()))
            
        if 'bleed_label' in self.view.widgets and 'bleed_var' in self.view.vars:
            self.view.widgets['bleed_label'].configure(text=f"{self.view.vars['bleed_var'].get():.1f}")
            
        if 'min_text_label' in self.view.widgets and 'min_text_var' in self.view.vars:
            self.view.widgets['min_text_label'].configure(text=f"{self.view.vars['min_text_var'].get():.1f}")
            
        if 'max_ink_label' in self.view.widgets and 'max_ink_var' in self.view.vars:
            self.view.widgets['max_ink_label'].configure(text=str(self.view.vars['max_ink_var'].get()))
            
        if 'jpeg_quality_label' in self.view.widgets and 'jpeg_quality_var' in self.view.vars:
            self.view.widgets['jpeg_quality_label'].configure(text=str(self.view.vars['jpeg_quality_var'].get()))
        
    def on_slider_change(self, value):
        """슬라이더 변경 이벤트"""
        self.update_slider_labels()
        self.on_setting_change()
        
    def on_parent_change(self, value):
        """부모 프로파일 변경"""
        self.on_setting_change()
        
    def on_setting_change(self, event=None):
        """설정 변경 이벤트"""
        if self.view.current_profile_name:
            profile = self.view.profile_manager.get_profile(self.view.current_profile_name)
            if profile and not profile.is_builtin:
                self.view.modified = True
                if 'save_btn' in self.view.widgets:
                    self.view.widgets['save_btn'].configure(state="normal")
                if 'revert_btn' in self.view.widgets:
                    self.view.widgets['revert_btn'].configure(state="normal")
                    
    def save_settings(self):
        """설정 저장"""
        if not self.view.current_profile_name:
            return
            
        # 설정 수집
        settings = {}
        
        # 설명
        if 'desc_text' in self.view.widgets:
            settings['description'] = self.view.widgets['desc_text'].get("1.0", tk.END).strip()
            
        # 부모 프로파일
        if 'parent_menu' in self.view.widgets:
            parent = self.view.widgets['parent_menu'].get()
            settings['parent_profile'] = None if parent == "없음" else parent
            
        # 품질 기준
        settings['quality_standards'] = {}
        if 'min_dpi_var' in self.view.vars:
            settings['quality_standards']['minimum_dpi'] = self.view.vars['min_dpi_var'].get()
        if 'bleed_var' in self.view.vars:
            settings['quality_standards']['standard_bleed_size'] = self.view.vars['bleed_var'].get()
        if 'min_text_var' in self.view.vars:
            settings['quality_standards']['minimum_text_size'] = self.view.vars['min_text_var'].get()
        if 'max_ink_var' in self.view.vars:
            settings['quality_standards']['max_ink_coverage'] = self.view.vars['max_ink_var'].get()
        if 'jpeg_quality_var' in self.view.vars:
            settings['quality_standards']['jpeg_quality'] = self.view.vars['jpeg_quality_var'].get()
        
        # 검사 옵션
        settings['check_options'] = {}
        if 'check_vars' in self.view.vars:
            for key, var in self.view.vars['check_vars'].items():
                settings['check_options'][key] = var.get()
                
        if 'allow_rgb_var' in self.view.vars:
            settings['check_options']['allow_rgb'] = self.view.vars['allow_rgb_var'].get()
        if 'check_spot_var' in self.view.vars:
            settings['check_options']['check_spot'] = self.view.vars['check_spot_var'].get()
        if 'require_embed_var' in self.view.vars:
            settings['check_options']['require_font_embedding'] = self.view.vars['require_embed_var'].get()
        if 'allow_type3_var' in self.view.vars:
            settings['check_options']['allow_type3_fonts'] = self.view.vars['allow_type3_var'].get()
        if 'allow_subset_var' in self.view.vars:
            settings['check_options']['allow_subset_fonts'] = self.view.vars['allow_subset_var'].get()
        if 'allow_resample_var' in self.view.vars:
            settings['check_options']['allow_image_resampling'] = self.view.vars['allow_resample_var'].get()
        if 'check_metadata_var' in self.view.vars:
            settings['check_options']['check_metadata'] = self.view.vars['check_metadata_var'].get()
        
        # 자동 수정 옵션
        settings['autofix_options'] = {}
        if 'autofix_vars' in self.view.vars:
            for key, var in self.view.vars['autofix_vars'].items():
                settings['autofix_options'][key] = var.get()
        
        # 프로파일 업데이트
        success = self.view.profile_manager.update_profile(self.view.current_profile_name, settings)
        
        if success:
            self.view.profile_manager.save_profiles()
            self.view.modified = False
            if 'save_btn' in self.view.widgets:
                self.view.widgets['save_btn'].configure(state="disabled")
            if 'revert_btn' in self.view.widgets:
                self.view.widgets['revert_btn'].configure(state="disabled")
            messagebox.showinfo("성공", "프로파일이 저장되었습니다.")
        else:
            messagebox.showerror("오류", "프로파일 저장에 실패했습니다.")
            
    def revert_settings(self):
        """설정 되돌리기"""
        if self.view.current_profile_name:
            self.load_profile_settings(self.view.current_profile_name)