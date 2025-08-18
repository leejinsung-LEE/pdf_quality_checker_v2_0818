"""
파일 매니저 - 파일 작업 관리
"""

import json
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, List
from pathlib import Path

if TYPE_CHECKING:
    from .base import MainWindow


class FileManager:
    """파일 매니저"""
    
    def __init__(self, window: 'MainWindow'):
        self.window = window
    
    def open_files(self):
        """파일 열기"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            pdf_files = [Path(f) for f in files if f.endswith('.pdf')]
            if pdf_files:
                self.process_files(pdf_files)
            else:
                messagebox.showwarning("경고", "PDF 파일을 선택해주세요.")
    
    def open_folder(self):
        """폴더 열기"""
        folder = filedialog.askdirectory(title="PDF 파일이 있는 폴더 선택")
        
        if folder:
            folder_path = Path(folder)
            pdf_files = list(folder_path.glob("*.pdf"))
            
            if pdf_files:
                self.process_files(pdf_files)
            else:
                messagebox.showinfo("정보", "선택한 폴더에 PDF 파일이 없습니다.")
    
    def open_recent_files(self, files: List[Path]):
        """최근 파일 열기"""
        self.process_files(files)
    
    def process_files(self, files: List[Path]):
        """파일 처리"""
        if not files:
            return
        
        # 파일 컨트롤러로 처리
        for file_path in files:
            if file_path.exists() and file_path.suffix.lower() == '.pdf':
                self.window.file_controller.add_file(str(file_path))
                self.add_recent_file(str(file_path))
        
        # 통합 처리 뷰로 전환
        self.window.view_manager.switch_tab('unified_processing')
        
        # 처리 시작
        self.window.file_controller.start_processing()
    
    def load_recent_files(self):
        """최근 파일 목록 로드"""
        try:
            recent_file = Path("data/recent_files.json")
            if recent_file.exists():
                with open(recent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.window.recent_files = data.get('recent_files', [])
            else:
                self.window.recent_files = []
        except Exception as e:
            print(f"최근 파일 로드 실패: {e}")
            self.window.recent_files = []
    
    def save_recent_files(self):
        """최근 파일 목록 저장"""
        try:
            recent_file = Path("data/recent_files.json")
            recent_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(recent_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'recent_files': self.window.recent_files[:10]  # 최대 10개
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"최근 파일 저장 실패: {e}")
    
    def add_recent_file(self, file_path: str):
        """최근 파일 추가"""
        # 이미 있으면 제거
        if file_path in self.window.recent_files:
            self.window.recent_files.remove(file_path)
        
        # 맨 앞에 추가
        self.window.recent_files.insert(0, file_path)
        
        # 최대 10개 유지
        self.window.recent_files = self.window.recent_files[:10]
        
        # 메뉴 업데이트
        if hasattr(self.window, 'menubar'):
            self.window.menubar.update_recent_files(
                [Path(f) for f in self.window.recent_files if Path(f).exists()]
            )
        
        # 저장
        self.save_recent_files()
    
    def clear_recent_files(self):
        """최근 파일 목록 초기화"""
        self.window.recent_files = []
        self.save_recent_files()
        
        # 메뉴 업데이트
        if hasattr(self.window, 'menubar'):
            self.window.menubar.update_recent_files([])