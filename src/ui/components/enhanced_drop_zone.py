# -*- coding: utf-8 -*-
"""
향상된 드래그앤드롭 존 컴포넌트

시각적 피드백과 애니메이션이 강화된 드래그앤드롭 영역
"""

import customtkinter as ctk
import tkinterdnd2
from pathlib import Path
from typing import List, Callable, Optional
import threading
from PIL import Image, ImageDraw


class EnhancedDropZone(ctk.CTkFrame):
    """향상된 드래그앤드롭 존"""
    
    def __init__(self, 
                 parent,
                 on_files_dropped: Optional[Callable[[List[Path]], None]] = None,
                 **kwargs):
        """
        초기화
        
        Args:
            parent: 부모 위젯
            on_files_dropped: 파일 드롭 콜백
            **kwargs: CTkFrame 추가 인자
        """
        super().__init__(parent, **kwargs)
        
        self.on_files_dropped = on_files_dropped
        self.is_dragging = False
        self.animation_running = False
        
        # 색상 설정
        self.colors = {
            'normal': '#2b2b2b',
            'hover': '#3d3d3d',
            'active': '#4a4a4a',
            'accent': '#1e88e5',
            'success': '#4caf50',
            'error': '#f44336',
            'text': '#ffffff',
            'text_secondary': '#888888'
        }
        
        self._setup_ui()
        self._setup_drag_drop()
        
    def _setup_ui(self):
        """UI 구성"""
        # 메인 프레임 설정
        self.configure(
            fg_color=self.colors['normal'],
            corner_radius=10,
            border_width=2,
            border_color=self.colors['text_secondary']
        )
        
        # 중앙 컨텐츠 프레임
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 아이콘 (PDF 아이콘 또는 드롭 아이콘)
        self.icon_label = ctk.CTkLabel(
            self.content_frame,
            text="📄",
            font=('Arial', 48)
        )
        self.icon_label.pack(pady=(0, 10))
        
        # 메인 텍스트
        self.main_text = ctk.CTkLabel(
            self.content_frame,
            text="PDF 파일을 여기에 드래그하세요",
            font=('Arial', 14, 'bold'),
            text_color=self.colors['text']
        )
        self.main_text.pack(pady=(0, 5))
        
        # 보조 텍스트
        self.sub_text = ctk.CTkLabel(
            self.content_frame,
            text="또는 클릭하여 파일 선택",
            font=('Arial', 11),
            text_color=self.colors['text_secondary']
        )
        self.sub_text.pack()
        
        # 진행률 표시 (초기에는 숨김)
        self.progress_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=4
        )
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=200,
            height=4,
            progress_color=self.colors['accent']
        )
        
        # 상태 표시 라벨
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=('Arial', 10),
            text_color=self.colors['text_secondary']
        )
        
        # 클릭 이벤트 바인딩
        self.bind("<Button-1>", self._on_click)
        self.content_frame.bind("<Button-1>", self._on_click)
        
    def _setup_drag_drop(self):
        """드래그앤드롭 설정"""
        # tkinterdnd2 DND 등록
        self.drop_target_register(tkinterdnd2.DND_FILES)
        
        # 이벤트 바인딩
        self.dnd_bind('<<Drop>>', self._on_drop)
        self.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.dnd_bind('<<DragLeave>>', self._on_drag_leave)
        
    def _on_click(self, event):
        """클릭 이벤트 처리"""
        from tkinter import filedialog
        
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        )
        
        if files:
            pdf_files = [Path(f) for f in files if f.lower().endswith('.pdf')]
            if pdf_files:
                self._process_files(pdf_files)
                
    def _on_drag_enter(self, event):
        """드래그 진입 시"""
        if not self.is_dragging:
            self.is_dragging = True
            self._animate_drag_enter()
            
    def _on_drag_leave(self, event):
        """드래그 이탈 시"""
        if self.is_dragging:
            self.is_dragging = False
            self._animate_drag_leave()
            
    def _on_drop(self, event):
        """파일 드롭 시"""
        self.is_dragging = False
        
        # 파일 경로 파싱
        try:
            files = self.tk.splitlist(event.data)
            pdf_files = []
            
            for file_path in files:
                path = Path(file_path)
                if path.exists() and path.suffix.lower() == '.pdf':
                    pdf_files.append(path)
                    
            if pdf_files:
                self._process_files(pdf_files)
            else:
                self._show_error("PDF 파일이 없습니다")
                
        except Exception as e:
            self._show_error(f"파일 처리 오류: {e}")
            
        # UI 복원
        self._animate_drag_leave()
        
    def _process_files(self, files: List[Path]):
        """파일 처리"""
        # 성공 애니메이션
        self._animate_success()
        
        # 진행률 표시
        self._show_progress(len(files))
        
        # 콜백 호출
        if self.on_files_dropped:
            # 비동기로 처리
            threading.Thread(
                target=lambda: self._process_files_async(files),
                daemon=True
            ).start()
            
    def _process_files_async(self, files: List[Path]):
        """비동기 파일 처리"""
        try:
            # 파일별로 진행률 업데이트
            for i, file in enumerate(files):
                self._update_progress(i + 1, len(files), file.name)
                
            # 콜백 호출
            self.on_files_dropped(files)
            
            # 완료 표시
            self.after(100, lambda: self._show_complete(len(files)))
            
        except Exception as e:
            self.after(100, lambda: self._show_error(f"처리 오류: {e}"))
            
    def _animate_drag_enter(self):
        """드래그 진입 애니메이션"""
        self.configure(
            fg_color=self.colors['hover'],
            border_color=self.colors['accent'],
            border_width=3
        )
        
        # 아이콘 변경
        self.icon_label.configure(text="⬇️")
        
        # 텍스트 변경
        self.main_text.configure(
            text="놓아서 업로드",
            text_color=self.colors['accent']
        )
        
        # 펄스 애니메이션
        self._pulse_animation()
        
    def _animate_drag_leave(self):
        """드래그 이탈 애니메이션"""
        self.configure(
            fg_color=self.colors['normal'],
            border_color=self.colors['text_secondary'],
            border_width=2
        )
        
        # 아이콘 복원
        self.icon_label.configure(text="📄")
        
        # 텍스트 복원
        self.main_text.configure(
            text="PDF 파일을 여기에 드래그하세요",
            text_color=self.colors['text']
        )
        
        self.animation_running = False
        
    def _animate_success(self):
        """성공 애니메이션"""
        self.configure(
            border_color=self.colors['success'],
            border_width=3
        )
        
        # 아이콘 변경
        self.icon_label.configure(text="✅")
        
        # 1초 후 복원
        self.after(1000, self._animate_drag_leave)
        
    def _pulse_animation(self):
        """펄스 애니메이션"""
        if not self.is_dragging:
            return
            
        self.animation_running = True
        
        def pulse():
            if not self.animation_running:
                return
                
            # 테두리 두께 변화
            current_width = self.cget("border_width")
            new_width = 4 if current_width == 3 else 3
            self.configure(border_width=new_width)
            
            # 반복
            if self.animation_running:
                self.after(500, pulse)
                
        pulse()
        
    def _show_progress(self, total_files: int):
        """진행률 표시 시작"""
        self.progress_frame.pack(fill='x', padx=20, pady=(10, 0))
        self.progress_bar.pack(fill='x')
        self.progress_bar.set(0)
        
        self.status_label.pack(pady=(5, 10))
        self.status_label.configure(
            text=f"0/{total_files} 파일 처리 중..."
        )
        
    def _update_progress(self, current: int, total: int, filename: str):
        """진행률 업데이트"""
        progress = current / total
        
        self.after(0, lambda: [
            self.progress_bar.set(progress),
            self.status_label.configure(
                text=f"{current}/{total} - {filename[:30]}..."
            )
        ])
        
    def _show_complete(self, total_files: int):
        """완료 표시"""
        self.progress_bar.set(1.0)
        self.status_label.configure(
            text=f"✅ {total_files}개 파일 처리 완료",
            text_color=self.colors['success']
        )
        
        # 3초 후 숨기기
        self.after(3000, self._hide_progress)
        
    def _show_error(self, message: str):
        """에러 표시"""
        self.configure(
            border_color=self.colors['error'],
            border_width=3
        )
        
        self.icon_label.configure(text="❌")
        self.main_text.configure(
            text=message,
            text_color=self.colors['error']
        )
        
        # 3초 후 복원
        self.after(3000, self._animate_drag_leave)
        
    def _hide_progress(self):
        """진행률 숨기기"""
        self.progress_frame.pack_forget()
        self.status_label.pack_forget()
        self.status_label.configure(text="")
        
    def set_enabled(self, enabled: bool):
        """활성화/비활성화"""
        if enabled:
            self.configure(state="normal")
            self._setup_drag_drop()
        else:
            self.configure(state="disabled")
            self.unbind_all('<<Drop>>')
            self.unbind_all('<<DragEnter>>')
            self.unbind_all('<<DragLeave>>')