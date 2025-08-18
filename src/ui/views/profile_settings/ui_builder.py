"""
프로파일 설정 UI 빌더
기능: 프로파일 설정 UI 구성 요소 생성
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import ProfileSettingsView


class UIBuilder:
    """UI 생성 헬퍼 클래스"""
    
    def __init__(self, view: 'ProfileSettingsView'):
        self.view = view
        
    def create_ui(self):
        """전체 UI 구성"""
        # 좌측: 프로파일 목록
        self._create_profile_list()
        
        # 우측: 상세 설정
        self._create_settings_panel()
        
    def _create_profile_list(self):
        """프로파일 목록 패널"""
        list_frame = ctk.CTkFrame(self.view)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.view.widgets['list_frame'] = list_frame
        
        # 제목
        title = ctk.CTkLabel(
            list_frame,
            text="프로파일 목록",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=10)
        
        # 버튼 프레임
        btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        # 새 프로파일 버튼
        new_btn = ctk.CTkButton(
            btn_frame,
            text="➕ 새 프로파일",
            command=self.view.create_new_profile,
            width=100
        )
        new_btn.pack(side="left", padx=2)
        self.view.widgets['new_btn'] = new_btn
        
        # 복제 버튼
        clone_btn = ctk.CTkButton(
            btn_frame,
            text="📋 복제",
            command=self.view.clone_profile,
            width=80
        )
        clone_btn.pack(side="left", padx=2)
        self.view.widgets['clone_btn'] = clone_btn
        
        # 삭제 버튼
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ 삭제",
            command=self.view.delete_profile,
            width=80,
            fg_color="red"
        )
        delete_btn.pack(side="left", padx=2)
        self.view.widgets['delete_btn'] = delete_btn
        
        # 프로파일 리스트박스
        profile_listbox = tk.Listbox(
            list_frame,
            width=30,
            height=20,
            bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "white",
            fg="white" if ctk.get_appearance_mode() == "Dark" else "black",
            selectbackground="#1f6aa5",
            font=("Arial", 10)
        )
        profile_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        profile_listbox.bind('<<ListboxSelect>>', self.view.on_profile_select)
        self.view.widgets['profile_listbox'] = profile_listbox
        
        # 가져오기/내보내기 버튼
        io_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        io_frame.pack(fill="x", padx=10, pady=10)
        
        import_btn = ctk.CTkButton(
            io_frame,
            text="📥 가져오기",
            command=self.view.import_profile,
            width=100
        )
        import_btn.pack(side="left", padx=2)
        self.view.widgets['import_btn'] = import_btn
        
        export_btn = ctk.CTkButton(
            io_frame,
            text="📤 내보내기",
            command=self.view.export_profile,
            width=100
        )
        export_btn.pack(side="left", padx=2)
        self.view.widgets['export_btn'] = export_btn
        
    def _create_settings_panel(self):
        """설정 패널"""
        settings_frame = ctk.CTkScrollableFrame(self.view)
        settings_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.view.widgets['settings_frame'] = settings_frame
        
        # 제목
        settings_title = ctk.CTkLabel(
            settings_frame,
            text="프로파일 설정",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        settings_title.pack(pady=10)
        self.view.widgets['settings_title'] = settings_title
        
        # 탭뷰
        tabview = ctk.CTkTabview(settings_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.view.widgets['tabview'] = tabview
        
        # 탭 추가
        tabview.add("기본 설정")
        tabview.add("품질 기준")
        tabview.add("색상 설정")
        tabview.add("폰트 설정")
        tabview.add("이미지 설정")
        tabview.add("고급 설정")
        
        # 각 탭 내용은 TabBuilder가 생성
        if hasattr(self.view, 'tab_builder'):
            self.view.tab_builder.create_all_tabs()
        
        # 저장 버튼
        save_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        save_frame.pack(fill="x", pady=10)
        
        save_btn = ctk.CTkButton(
            save_frame,
            text="💾 저장",
            command=self.view.save_settings,
            width=120,
            state="disabled"
        )
        save_btn.pack(side="right", padx=10)
        self.view.widgets['save_btn'] = save_btn
        
        revert_btn = ctk.CTkButton(
            save_frame,
            text="↩️ 되돌리기",
            command=self.view.revert_settings,
            width=120,
            state="disabled"
        )
        revert_btn.pack(side="right", padx=5)
        self.view.widgets['revert_btn'] = revert_btn