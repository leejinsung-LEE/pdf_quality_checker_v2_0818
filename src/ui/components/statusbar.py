# src/ui/components/statusbar.py
"""
상태바 컴포넌트

애플리케이션 하단의 상태 정보를 표시합니다.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
from datetime import datetime


class StatusBar(ctk.CTkFrame):
    """상태바 컴포넌트"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 색상 테마
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'info': '#17a2b8'
        }
        
        # 상태 정보
        self.current_status = "준비"
        self.processing_count = 0
        self.folder_watch_active = False
        
        # UI 생성
        self._create_ui()
    
    def _create_ui(self):
        """UI 구성"""
        self.configure(fg_color=self.colors['bg_secondary'], height=30)
        self.pack_propagate(False)
        
        # 내부 프레임
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill='both', expand=True, padx=10)
        
        # 왼쪽: 상태 메시지
        left_frame = ctk.CTkFrame(inner, fg_color="transparent")
        left_frame.pack(side='left', fill='y')
        
        self.status_label = ctk.CTkLabel(
            left_frame,
            text="준비",
            font=('Arial', 11),
            text_color=self.colors['text_primary']
        )
        self.status_label.pack(side='left', padx=(0, 20))
        
        # 처리 중 표시
        self.processing_label = ctk.CTkLabel(
            left_frame,
            text="",
            font=('Arial', 11),
            text_color=self.colors['info']
        )
        self.processing_label.pack(side='left', padx=(0, 20))
        
        # 오른쪽: 추가 정보
        right_frame = ctk.CTkFrame(inner, fg_color="transparent")
        right_frame.pack(side='right', fill='y')
        
        # 폴더 감시 상태
        self.watch_indicator = ctk.CTkLabel(
            right_frame,
            text="",
            font=('Arial', 11),
            text_color=self.colors['text_secondary']
        )
        self.watch_indicator.pack(side='right', padx=(20, 0))
        
        # 현재 프로파일
        self.profile_label = ctk.CTkLabel(
            right_frame,
            text="프로파일: default",
            font=('Arial', 11),
            text_color=self.colors['text_secondary']
        )
        self.profile_label.pack(side='right', padx=(20, 0))
        
        # 시간
        self.time_label = ctk.CTkLabel(
            right_frame,
            text="",
            font=('Arial', 11),
            text_color=self.colors['text_secondary']
        )
        self.time_label.pack(side='right')
        
        # 시간 업데이트 시작
        self._update_time()
    
    def _update_time(self):
        """시간 업데이트"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        
        # 1초마다 업데이트
        self.after(1000, self._update_time)
    
    # Public 메서드
    
    def set_status(self, message: str, status_type: str = "info"):
        """상태 메시지 설정"""
        self.current_status = message
        self.status_label.configure(text=message)
        
        # 상태별 색상
        color_map = {
            'info': self.colors['text_primary'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['error']
        }
        color = color_map.get(status_type, self.colors['text_primary'])
        self.status_label.configure(text_color=color)
    
    def set_processing_count(self, count: int):
        """처리 중인 파일 수 설정"""
        self.processing_count = count
        if count > 0:
            self.processing_label.configure(text=f"처리 중: {count}개")
        else:
            self.processing_label.configure(text="")
    
    def set_folder_watch_status(self, active: bool, folder_count: int = 0):
        """폴더 감시 상태 설정"""
        self.folder_watch_active = active
        if active:
            self.watch_indicator.configure(
                text=f"📁 감시 중 ({folder_count}개 폴더)",
                text_color=self.colors['success']
            )
        else:
            self.watch_indicator.configure(
                text="📁 감시 중지",
                text_color=self.colors['text_secondary']
            )
    
    def set_current_profile(self, profile_name: str):
        """현재 프로파일 표시"""
        self.profile_label.configure(text=f"프로파일: {profile_name}")
    
    def show_progress(self, current: int, total: int, message: str = ""):
        """진행률 표시"""
        if total > 0:
            percent = (current / total) * 100
            progress_text = f"{message} {current}/{total} ({percent:.1f}%)"
            self.set_status(progress_text, "info")
    
    def flash_message(self, message: str, status_type: str = "info", duration: int = 3000):
        """일시적 메시지 표시"""
        # 현재 상태 저장
        prev_status = self.current_status
        prev_color = self.status_label.cget("text_color")
        
        # 메시지 표시
        self.set_status(message, status_type)
        
        # 일정 시간 후 복원
        self.after(
            duration,
            lambda: self.status_label.configure(text=prev_status, text_color=prev_color)
        )