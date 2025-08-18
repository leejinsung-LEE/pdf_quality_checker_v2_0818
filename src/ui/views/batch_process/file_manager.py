"""
일괄 처리 파일 관리자
기능: 파일 추가, 제거, 목록 관리
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import TYPE_CHECKING, List
import os

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import BatchProcessView


class FileManager:
    """파일 관리 헬퍼 클래스"""
    
    def __init__(self, view: 'BatchProcessView'):
        self.view = view
        
    def add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        )
        
        if files:
            for file_path in files:
                path = Path(file_path)
                if path not in self.view.file_list:
                    self.view.file_list.append(path)
            
            self.update_file_list()
    
    def add_folder(self):
        """폴더 추가"""
        folder = filedialog.askdirectory(title="폴더 선택")
        
        if folder:
            folder_path = Path(folder)
            pdf_files = list(folder_path.glob("**/*.pdf"))
            
            for file_path in pdf_files:
                if file_path not in self.view.file_list:
                    self.view.file_list.append(file_path)
            
            self.update_file_list()
            
            if pdf_files:
                tk.messagebox.showinfo(
                    "파일 추가",
                    f"{len(pdf_files)}개의 PDF 파일이 추가되었습니다."
                )
    
    def clear_list(self):
        """파일 목록 초기화"""
        self.view.file_list.clear()
        self.update_file_list()
    
    def update_file_list(self):
        """파일 목록 UI 업데이트"""
        if 'file_tree' not in self.view.widgets:
            return
            
        tree = self.view.widgets['file_tree']
        
        # 기존 항목 제거
        for item in tree.get_children():
            tree.delete(item)
        
        # 새 항목 추가
        for file_path in self.view.file_list:
            file_size = self._format_size(file_path.stat().st_size)
            
            # PDF 페이지 수 가져오기 (간단한 표시)
            pages = "?"  # 실제로는 PDF 라이브러리로 읽어야 함
            
            tree.insert(
                '',
                'end',
                text=file_path.name,
                values=(file_size, pages, "대기")
            )
        
        # 파일 수 업데이트
        if 'file_count_label' in self.view.widgets:
            count = len(self.view.file_list)
            text = f"{count}개 파일"
            if count > 0:
                total_size = sum(f.stat().st_size for f in self.view.file_list)
                text += f" ({self._format_size(total_size)})"
            self.view.widgets['file_count_label'].configure(text=text)
    
    def browse_output(self):
        """출력 폴더 선택"""
        folder = filedialog.askdirectory(title="출력 폴더 선택")
        
        if folder and 'output_entry' in self.view.widgets:
            self.view.widgets['output_entry'].delete(0, tk.END)
            self.view.widgets['output_entry'].insert(0, folder)
    
    def _format_size(self, size: int) -> str:
        """파일 크기 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_selected_files(self) -> List[Path]:
        """선택된 파일 목록 반환"""
        return self.view.file_list.copy()
    
    def update_file_status(self, file_path: Path, status: str):
        """파일 상태 업데이트"""
        if 'file_tree' not in self.view.widgets:
            return
            
        tree = self.view.widgets['file_tree']
        
        for item in tree.get_children():
            if tree.item(item, 'text') == file_path.name:
                values = list(tree.item(item, 'values'))
                values[2] = status
                tree.item(item, values=values)
                
                # 상태별 색상 설정
                if status == "완료":
                    tree.item(item, tags=('completed',))
                elif status == "오류":
                    tree.item(item, tags=('error',))
                elif status == "처리 중":
                    tree.item(item, tags=('processing',))
                break