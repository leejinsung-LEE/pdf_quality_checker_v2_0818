"""
프로파일 설정 탭 빌더
기능: 각 설정 탭의 UI 생성
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import ProfileSettingsView


class TabBuilder:
    """탭 UI 생성 헬퍼 클래스"""
    
    def __init__(self, view: 'ProfileSettingsView'):
        self.view = view
        
    def create_all_tabs(self):
        """모든 탭 내용 생성"""
        self._create_basic_tab()
        self._create_quality_tab()
        self._create_color_tab()
        self._create_font_tab()
        self._create_image_tab()
        self._create_advanced_tab()
        
    def _create_basic_tab(self):
        """기본 설정 탭"""
        if 'tabview' not in self.view.widgets:
            return
            
        tab = self.view.widgets['tabview'].tab("기본 설정")
        
        # 프로파일 이름
        name_frame = ctk.CTkFrame(tab, fg_color="transparent")
        name_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(name_frame, text="프로파일 이름:", width=120).pack(side="left")
        name_entry = ctk.CTkEntry(name_frame, width=200)
        name_entry.pack(side="left", padx=10)
        name_entry.bind("<KeyRelease>", self.view.on_setting_change)
        self.view.widgets['name_entry'] = name_entry
        
        # 설명
        desc_frame = ctk.CTkFrame(tab, fg_color="transparent")
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(desc_frame, text="설명:", width=120).pack(side="left", anchor="n")
        desc_text = ctk.CTkTextbox(desc_frame, width=300, height=100)
        desc_text.pack(side="left", padx=10)
        desc_text.bind("<KeyRelease>", self.view.on_setting_change)
        self.view.widgets['desc_text'] = desc_text
        
        # 부모 프로파일 (상속)
        parent_frame = ctk.CTkFrame(tab, fg_color="transparent")
        parent_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(parent_frame, text="부모 프로파일:", width=120).pack(side="left")
        parent_menu = ctk.CTkOptionMenu(
            parent_frame,
            values=["없음"],
            command=self.view.on_parent_change,
            width=200
        )
        parent_menu.pack(side="left", padx=10)
        self.view.widgets['parent_menu'] = parent_menu
        
    def _create_quality_tab(self):
        """품질 기준 탭"""
        if 'tabview' not in self.view.widgets:
            return
            
        tab = self.view.widgets['tabview'].tab("품질 기준")
        
        # DPI 설정
        dpi_frame = ctk.CTkFrame(tab, fg_color="transparent")
        dpi_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(dpi_frame, text="최소 이미지 DPI:", width=150).pack(side="left")
        min_dpi_var = tk.IntVar(value=300)
        self.view.vars['min_dpi_var'] = min_dpi_var
        
        min_dpi_slider = ctk.CTkSlider(
            dpi_frame,
            from_=72,
            to=600,
            variable=min_dpi_var,
            command=self.view.on_slider_change
        )
        min_dpi_slider.pack(side="left", padx=10, fill="x", expand=True)
        self.view.widgets['min_dpi_slider'] = min_dpi_slider
        
        min_dpi_label = ctk.CTkLabel(dpi_frame, text="300")
        min_dpi_label.pack(side="left", padx=5)
        self.view.widgets['min_dpi_label'] = min_dpi_label
        
        # 재단선 크기
        bleed_frame = ctk.CTkFrame(tab, fg_color="transparent")
        bleed_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(bleed_frame, text="표준 재단선 (mm):", width=150).pack(side="left")
        bleed_var = tk.DoubleVar(value=3.0)
        self.view.vars['bleed_var'] = bleed_var
        
        bleed_slider = ctk.CTkSlider(
            bleed_frame,
            from_=0,
            to=10,
            variable=bleed_var,
            command=self.view.on_slider_change
        )
        bleed_slider.pack(side="left", padx=10, fill="x", expand=True)
        self.view.widgets['bleed_slider'] = bleed_slider
        
        bleed_label = ctk.CTkLabel(bleed_frame, text="3.0")
        bleed_label.pack(side="left", padx=5)
        self.view.widgets['bleed_label'] = bleed_label
        
        # 최소 텍스트 크기
        text_frame = ctk.CTkFrame(tab, fg_color="transparent")
        text_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(text_frame, text="최소 텍스트 크기 (pt):", width=150).pack(side="left")
        min_text_var = tk.DoubleVar(value=6.0)
        self.view.vars['min_text_var'] = min_text_var
        
        min_text_slider = ctk.CTkSlider(
            text_frame,
            from_=4,
            to=12,
            variable=min_text_var,
            command=self.view.on_slider_change
        )
        min_text_slider.pack(side="left", padx=10, fill="x", expand=True)
        self.view.widgets['min_text_slider'] = min_text_slider
        
        min_text_label = ctk.CTkLabel(text_frame, text="6.0")
        min_text_label.pack(side="left", padx=5)
        self.view.widgets['min_text_label'] = min_text_label
        
        # 체크 옵션들
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkLabel(options_frame, text="검사 옵션", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.view.vars['check_vars'] = {}
        check_options = [
            ("check_fonts", "폰트 검사"),
            ("check_images", "이미지 검사"),
            ("check_colors", "색상 검사"),
            ("check_bleed", "재단선 검사"),
            ("check_transparency", "투명도 검사"),
            ("check_overprint", "오버프린트 검사")
        ]
        
        for key, label in check_options:
            var = tk.BooleanVar(value=True)
            self.view.vars['check_vars'][key] = var
            checkbox = ctk.CTkCheckBox(
                options_frame,
                text=label,
                variable=var,
                command=self.view.on_setting_change
            )
            checkbox.pack(anchor="w", padx=20, pady=2)
            
    def _create_color_tab(self):
        """색상 설정 탭"""
        if 'tabview' not in self.view.widgets:
            return
            
        tab = self.view.widgets['tabview'].tab("색상 설정")
        
        # 잉크 커버리지
        ink_frame = ctk.CTkFrame(tab, fg_color="transparent")
        ink_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ink_frame, text="최대 잉크 커버리지 (%):", width=150).pack(side="left")
        max_ink_var = tk.IntVar(value=320)
        self.view.vars['max_ink_var'] = max_ink_var
        
        max_ink_slider = ctk.CTkSlider(
            ink_frame,
            from_=200,
            to=400,
            variable=max_ink_var,
            command=self.view.on_slider_change
        )
        max_ink_slider.pack(side="left", padx=10, fill="x", expand=True)
        self.view.widgets['max_ink_slider'] = max_ink_slider
        
        max_ink_label = ctk.CTkLabel(ink_frame, text="320")
        max_ink_label.pack(side="left", padx=5)
        self.view.widgets['max_ink_label'] = max_ink_label
        
        # RGB 허용
        rgb_frame = ctk.CTkFrame(tab, fg_color="transparent")
        rgb_frame.pack(fill="x", padx=10, pady=5)
        
        allow_rgb_var = tk.BooleanVar(value=False)
        self.view.vars['allow_rgb_var'] = allow_rgb_var
        ctk.CTkCheckBox(
            rgb_frame,
            text="RGB 색상 허용",
            variable=allow_rgb_var,
            command=self.view.on_setting_change
        ).pack(side="left", padx=10)
        
        # 별색 검사
        spot_frame = ctk.CTkFrame(tab, fg_color="transparent")
        spot_frame.pack(fill="x", padx=10, pady=5)
        
        check_spot_var = tk.BooleanVar(value=True)
        self.view.vars['check_spot_var'] = check_spot_var
        ctk.CTkCheckBox(
            spot_frame,
            text="별색(Spot Color) 검사",
            variable=check_spot_var,
            command=self.view.on_setting_change
        ).pack(side="left", padx=10)
        
        # 색상 프로파일
        profile_frame = ctk.CTkFrame(tab, fg_color="transparent")
        profile_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(profile_frame, text="권장 색상 프로파일:", width=150).pack(side="left")
        color_profile_menu = ctk.CTkOptionMenu(
            profile_frame,
            values=["Fogra39", "US Web Coated (SWOP) v2", "Japan Color 2001 Coated", "사용자 정의"],
            command=self.view.on_setting_change,
            width=200
        )
        color_profile_menu.pack(side="left", padx=10)
        self.view.widgets['color_profile_menu'] = color_profile_menu
        
    def _create_font_tab(self):
        """폰트 설정 탭"""
        if 'tabview' not in self.view.widgets:
            return
            
        tab = self.view.widgets['tabview'].tab("폰트 설정")
        
        # 폰트 임베딩
        embed_frame = ctk.CTkFrame(tab, fg_color="transparent")
        embed_frame.pack(fill="x", padx=10, pady=5)
        
        require_embed_var = tk.BooleanVar(value=True)
        self.view.vars['require_embed_var'] = require_embed_var
        ctk.CTkCheckBox(
            embed_frame,
            text="폰트 임베딩 필수",
            variable=require_embed_var,
            command=self.view.on_setting_change
        ).pack(side="left", padx=10)
        
        # Type3 폰트
        type3_frame = ctk.CTkFrame(tab, fg_color="transparent")
        type3_frame.pack(fill="x", padx=10, pady=5)
        
        allow_type3_var = tk.BooleanVar(value=False)
        self.view.vars['allow_type3_var'] = allow_type3_var
        ctk.CTkCheckBox(
            type3_frame,
            text="Type3 폰트 허용",
            variable=allow_type3_var,
            command=self.view.on_setting_change
        ).pack(side="left", padx=10)
        
        # 서브셋 폰트
        subset_frame = ctk.CTkFrame(tab, fg_color="transparent")
        subset_frame.pack(fill="x", padx=10, pady=5)
        
        allow_subset_var = tk.BooleanVar(value=True)
        self.view.vars['allow_subset_var'] = allow_subset_var
        ctk.CTkCheckBox(
            subset_frame,
            text="서브셋 폰트 허용",
            variable=allow_subset_var,
            command=self.view.on_setting_change
        ).pack(side="left", padx=10)
        
    def _create_image_tab(self):
        """이미지 설정 탭"""
        if 'tabview' not in self.view.widgets:
            return
            
        tab = self.view.widgets['tabview'].tab("이미지 설정")
        
        # 압축 품질
        quality_frame = ctk.CTkFrame(tab, fg_color="transparent")
        quality_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(quality_frame, text="JPEG 압축 품질:", width=150).pack(side="left")
        jpeg_quality_var = tk.IntVar(value=85)
        self.view.vars['jpeg_quality_var'] = jpeg_quality_var
        
        jpeg_quality_slider = ctk.CTkSlider(
            quality_frame,
            from_=50,
            to=100,
            variable=jpeg_quality_var,
            command=self.view.on_slider_change
        )
        jpeg_quality_slider.pack(side="left", padx=10, fill="x", expand=True)
        self.view.widgets['jpeg_quality_slider'] = jpeg_quality_slider
        
        jpeg_quality_label = ctk.CTkLabel(quality_frame, text="85")
        jpeg_quality_label.pack(side="left", padx=5)
        self.view.widgets['jpeg_quality_label'] = jpeg_quality_label
        
        # 이미지 리샘플링
        resample_frame = ctk.CTkFrame(tab, fg_color="transparent")
        resample_frame.pack(fill="x", padx=10, pady=5)
        
        allow_resample_var = tk.BooleanVar(value=False)
        self.view.vars['allow_resample_var'] = allow_resample_var
        ctk.CTkCheckBox(
            resample_frame,
            text="이미지 리샘플링 허용",
            variable=allow_resample_var,
            command=self.view.on_setting_change
        ).pack(side="left", padx=10)
        
    def _create_advanced_tab(self):
        """고급 설정 탭"""
        if 'tabview' not in self.view.widgets:
            return
            
        tab = self.view.widgets['tabview'].tab("고급 설정")
        
        # PDF 버전
        version_frame = ctk.CTkFrame(tab, fg_color="transparent")
        version_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(version_frame, text="권장 PDF 버전:", width=150).pack(side="left")
        pdf_version_menu = ctk.CTkOptionMenu(
            version_frame,
            values=["PDF 1.4", "PDF 1.5", "PDF 1.6", "PDF 1.7", "PDF/X-1a", "PDF/X-4"],
            command=self.view.on_setting_change,
            width=200
        )
        pdf_version_menu.pack(side="left", padx=10)
        self.view.widgets['pdf_version_menu'] = pdf_version_menu
        
        # 메타데이터 검사
        meta_frame = ctk.CTkFrame(tab, fg_color="transparent")
        meta_frame.pack(fill="x", padx=10, pady=5)
        
        check_metadata_var = tk.BooleanVar(value=True)
        self.view.vars['check_metadata_var'] = check_metadata_var
        ctk.CTkCheckBox(
            meta_frame,
            text="메타데이터 검사",
            variable=check_metadata_var,
            command=self.view.on_setting_change
        ).pack(side="left", padx=10)
        
        # 자동 수정 옵션
        autofix_frame = ctk.CTkFrame(tab)
        autofix_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkLabel(autofix_frame, text="자동 수정 옵션", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.view.vars['autofix_vars'] = {}
        autofix_options = [
            ("autofix_rgb", "RGB → CMYK 자동 변환"),
            ("autofix_fonts", "폰트 자동 임베딩"),
            ("autofix_images", "이미지 자동 최적화"),
            ("autofix_bleed", "재단선 자동 추가")
        ]
        
        for key, label in autofix_options:
            var = tk.BooleanVar(value=False)
            self.view.vars['autofix_vars'][key] = var
            checkbox = ctk.CTkCheckBox(
                autofix_frame,
                text=label,
                variable=var,
                command=self.view.on_setting_change
            )
            checkbox.pack(anchor="w", padx=20, pady=2)