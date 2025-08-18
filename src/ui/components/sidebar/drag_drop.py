# src/ui/components/sidebar/drag_drop.py
"""
드래그앤드롭 처리

파일 드래그앤드롭 이벤트 처리 및 파일 선택 기능을 담당합니다.
"""

import tkinterdnd2 as tkdnd
from tkinter import filedialog
from typing import List, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from .base import SidebarBase


class DragDropHandler:
    """드래그앤드롭 처리 클래스"""
    
    def __init__(self, parent: 'SidebarBase'):
        self.parent = parent
    
    def setup_drag_drop(self, drop_zone_widget):
        """드래그앤드롭 설정"""
        # 드래그앤드롭 이벤트 바인딩
        drop_zone_widget.drop_target_register(tkdnd.DND_FILES)
        drop_zone_widget.dnd_bind('<<Drop>>', self._on_drop)
        drop_zone_widget.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        drop_zone_widget.dnd_bind('<<DragLeave>>', self._on_drag_leave)
    
    def _on_drop(self, event):
        """파일 드롭 이벤트 처리"""
        try:
            # 드롭된 파일 목록 파싱
            file_paths = self._parse_drop_data(event.data)
            
            # PDF 파일만 필터링
            pdf_files = [path for path in file_paths 
                        if path.suffix.lower() == '.pdf' and path.exists()]
            
            if pdf_files:
                # 드롭 존 스타일 복원
                self._restore_drop_zone_style()
                
                # 콜백 호출
                if self.parent.on_files_dropped:
                    self.parent.on_files_dropped(pdf_files)
            else:
                # PDF 파일이 없을 경우 사용자에게 알림
                self._show_invalid_files_message()
                
        except Exception as e:
            print(f"드롭 처리 오류: {e}")
            self._restore_drop_zone_style()
    
    def _on_drag_enter(self, event):
        """드래그 진입 이벤트 처리"""
        # 드롭 존 스타일 변경 (시각적 피드백)
        drop_zone = self.parent.widgets.get('drop_zone')
        if drop_zone:
            drop_zone.configure(fg_color=self.parent.colors['accent'])
            
        drop_text = self.parent.widgets.get('drop_text')
        if drop_text:
            drop_text.configure(text="파일을 놓아주세요!", text_color=self.parent.colors['text_primary'])
    
    def _on_drag_leave(self, event):
        """드래그 벗어남 이벤트 처리"""
        self._restore_drop_zone_style()
    
    def _restore_drop_zone_style(self):
        """드롭 존 스타일 복원"""
        drop_zone = self.parent.widgets.get('drop_zone')
        if drop_zone:
            drop_zone.configure(fg_color=self.parent.colors['bg_card'])
            
        drop_text = self.parent.widgets.get('drop_text')
        if drop_text:
            drop_text.configure(text="PDF 파일을 여기에 드롭", text_color=self.parent.colors['text_secondary'])
    
    def _parse_drop_data(self, data: str) -> List[Path]:
        """드롭 데이터 파싱"""
        file_paths = []
        
        # Windows 스타일 경로 처리
        if data.startswith('{') and data.endswith('}'):
            # 중괄호로 감싸진 경우
            data = data[1:-1]
        
        # 공백으로 분리된 여러 파일 처리
        raw_paths = data.split()
        
        for raw_path in raw_paths:
            try:
                # 경로 정리
                clean_path = raw_path.strip('"').strip("'")
                path = Path(clean_path)
                
                if path.exists():
                    file_paths.append(path)
            except Exception:
                continue
        
        return file_paths
    
    def _show_invalid_files_message(self):
        """유효하지 않은 파일 메시지 표시"""
        drop_text = self.parent.widgets.get('drop_text')
        if drop_text:
            drop_text.configure(
                text="PDF 파일만 지원됩니다",
                text_color="#ff6b6b"  # 빨간색
            )
            
            # 2초 후 원래 텍스트로 복원
            drop_text.after(2000, lambda: drop_text.configure(
                text="PDF 파일을 여기에 드롭",
                text_color=self.parent.colors['text_secondary']
            ))
    
    def handle_file_select(self):
        """파일 선택 대화상자 처리"""
        try:
            # 파일 선택 대화상자
            file_paths = filedialog.askopenfilenames(
                title="PDF 파일 선택",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ],
                multiple=True
            )
            
            if file_paths:
                # Path 객체로 변환
                pdf_files = [Path(path) for path in file_paths]
                
                # 콜백 호출
                if self.parent.on_files_dropped:
                    self.parent.on_files_dropped(pdf_files)
                    
        except Exception as e:
            print(f"파일 선택 오류: {e}")
    
    def update_drop_zone_stats(self, file_count: int = 0):
        """드롭 존에 처리 통계 업데이트"""
        if file_count > 0:
            drop_text = self.parent.widgets.get('drop_text')
            if drop_text:
                drop_text.configure(text=f"📄 {file_count}개 파일 처리 중...")
                
                # 3초 후 원래 텍스트로 복원
                drop_text.after(3000, lambda: drop_text.configure(
                    text="PDF 파일을 여기에 드롭"
                ))
    
    def set_drop_zone_enabled(self, enabled: bool):
        """드롭 존 활성화/비활성화"""
        drop_zone = self.parent.widgets.get('drop_zone')
        drop_text = self.parent.widgets.get('drop_text')
        
        if enabled:
            if drop_zone:
                drop_zone.configure(fg_color=self.parent.colors['bg_card'])
            if drop_text:
                drop_text.configure(
                    text="PDF 파일을 여기에 드롭",
                    text_color=self.parent.colors['text_secondary']
                )
        else:
            if drop_zone:
                drop_zone.configure(fg_color=self.parent.colors['border'])
            if drop_text:
                drop_text.configure(
                    text="처리 중... 잠시 기다려주세요",
                    text_color=self.parent.colors['text_secondary']
                )