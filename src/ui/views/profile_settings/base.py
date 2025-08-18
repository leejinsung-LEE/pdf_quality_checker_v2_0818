"""
프로파일 설정 뷰 - 메인 클래스
기능: 품질 검사 프로파일의 상세 설정 관리
의존성: customtkinter, tkinter
최종 수정: 2025-01-12

AI 친화적 문서화:
- 역할: 프로파일 설정 편집 및 관리 UI 제공
- 입력: 프로파일 이름, 설정값
- 출력: 저장된 프로파일 설정
- 상태: 현재 편집 중인 프로파일, 수정 여부
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Dict, Any, Optional
from pathlib import Path

# 프로파일 매니저
from ....core.profiles import get_profile_manager

# 헬퍼 클래스 import
from .ui_builder import UIBuilder
from .tab_builders import TabBuilder
from .handlers import EventHandler
from .profile_manager import ProfileManagerHelper


class ProfileSettingsView(ctk.CTkFrame):
    """프로파일 상세 설정 뷰"""
    
    def __init__(self, parent, **kwargs):
        """
        초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent, **kwargs)
        
        # 프로파일 매니저
        self.profile_manager = get_profile_manager()
        
        # 현재 편집 중인 프로파일
        self.current_profile_name = None
        self.modified = False
        self.temp_settings = {}
        
        # UI 상태 변수 및 위젯 참조
        self.widgets = {}  # 위젯 참조 저장
        self.vars = {}     # tkinter 변수 저장
        
        # 색상 테마
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'bg_card': '#2a2a2a',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#667eea',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'border': '#404040'
        }
        
        # 헬퍼 초기화
        self.ui_builder = UIBuilder(self)
        self.tab_builder = TabBuilder(self)
        self.event_handler = EventHandler(self)
        self.profile_helper = ProfileManagerHelper(self)
        
        # UI 생성
        self._create_ui()
        
        # 초기 프로파일 로드
        self.load_profile_list()
        
    def _create_ui(self):
        """UI 구성"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # UI 빌더를 통해 생성
        self.ui_builder.create_ui()
        
    def load_profile_list(self):
        """프로파일 목록 로드"""
        self.profile_helper.load_profile_list()
        
    def on_profile_select(self, event):
        """프로파일 선택 이벤트"""
        self.event_handler.on_profile_select(event)
        
    def load_profile_settings(self, profile_name: str):
        """프로파일 설정 로드"""
        self.event_handler.load_profile_settings(profile_name)
        
    def update_slider_labels(self):
        """슬라이더 레이블 업데이트"""
        self.event_handler.update_slider_labels()
        
    def on_slider_change(self, value):
        """슬라이더 변경 이벤트"""
        self.event_handler.on_slider_change(value)
        
    def on_parent_change(self, value):
        """부모 프로파일 변경"""
        self.event_handler.on_parent_change(value)
        
    def on_setting_change(self, event=None):
        """설정 변경 이벤트"""
        self.event_handler.on_setting_change(event)
        
    def save_settings(self):
        """설정 저장"""
        self.event_handler.save_settings()
        
    def revert_settings(self):
        """설정 되돌리기"""
        self.event_handler.revert_settings()
        
    def create_new_profile(self):
        """새 프로파일 생성"""
        self.profile_helper.create_new_profile()
        
    def clone_profile(self):
        """프로파일 복제"""
        self.profile_helper.clone_profile()
        
    def delete_profile(self):
        """프로파일 삭제"""
        self.profile_helper.delete_profile()
        
    def import_profile(self):
        """프로파일 가져오기"""
        self.profile_helper.import_profile()
        
    def export_profile(self):
        """프로파일 내보내기"""
        self.profile_helper.export_profile()