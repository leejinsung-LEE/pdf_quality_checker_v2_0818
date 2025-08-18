# src/ui/selector.py
"""
UI 모드 선택 다이얼로그

프로그램 시작 시 Classic/Modern UI를 선택할 수 있는 다이얼로그
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Literal
from pathlib import Path
import sys

UIMode = Literal["classic", "modern"]

class UIModeSelector:
    """UI 모드 선택 다이얼로그"""
    
    def __init__(self):
        self.selected_mode: Optional[UIMode] = None
        self.remember_choice = False
        
    def show(self) -> Optional[UIMode]:
        """선택 다이얼로그 표시"""
        # 루트 윈도우 생성
        root = tk.Tk()
        root.title("PDF Quality Checker - UI 모드 선택")
        root.geometry("600x400")
        root.resizable(False, False)
        
        # 중앙 정렬
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (600 // 2)
        y = (root.winfo_screenheight() // 2) - (400 // 2)
        root.geometry(f"600x400+{x}+{y}")
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        
        # 배경색 설정
        root.configure(bg='#1e1e1e')
        
        # 타이틀
        title_label = tk.Label(
            root,
            text="UI 모드를 선택하세요",
            font=('Segoe UI', 18, 'bold'),
            bg='#1e1e1e',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # 설명
        desc_label = tk.Label(
            root,
            text="원하시는 인터페이스 스타일을 선택해주세요",
            font=('Segoe UI', 10),
            bg='#1e1e1e',
            fg='#cccccc'
        )
        desc_label.pack(pady=(0, 30))
        
        # 선택 프레임
        selection_frame = tk.Frame(root, bg='#1e1e1e')
        selection_frame.pack(expand=True, fill='both', padx=40)
        
        # Classic UI 버튼
        classic_frame = tk.Frame(selection_frame, bg='#2b2b2b', highlightbackground='#444', highlightthickness=1)
        classic_frame.pack(side='left', expand=True, fill='both', padx=(0, 10))
        
        tk.Label(
            classic_frame,
            text="🎯 Classic UI",
            font=('Segoe UI', 14, 'bold'),
            bg='#2b2b2b',
            fg='#4a9eff'
        ).pack(pady=20)
        
        tk.Label(
            classic_frame,
            text="안정적이고 검증된\n기존 인터페이스",
            font=('Segoe UI', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            justify='center'
        ).pack(pady=10)
        
        tk.Label(
            classic_frame,
            text="✓ 모든 기능 완벽 지원\n✓ 안정적인 성능\n✓ 기존 사용자 친화적",
            font=('Segoe UI', 9),
            bg='#2b2b2b',
            fg='#888888',
            justify='left'
        ).pack(pady=10, padx=20)
        
        classic_btn = tk.Button(
            classic_frame,
            text="Classic 선택",
            font=('Segoe UI', 11, 'bold'),
            bg='#4a9eff',
            fg='white',
            relief='flat',
            padx=30,
            pady=10,
            cursor='hand2',
            command=lambda: self._select_mode(root, 'classic')
        )
        classic_btn.pack(pady=20)
        
        # Modern UI 버튼
        modern_frame = tk.Frame(selection_frame, bg='#2b2b2b', highlightbackground='#444', highlightthickness=1)
        modern_frame.pack(side='right', expand=True, fill='both', padx=(10, 0))
        
        tk.Label(
            modern_frame,
            text="✨ Modern UI",
            font=('Segoe UI', 14, 'bold'),
            bg='#2b2b2b',
            fg='#6750A4'
        ).pack(pady=20)
        
        tk.Label(
            modern_frame,
            text="현대적이고 세련된\n새로운 인터페이스",
            font=('Segoe UI', 10),
            bg='#2b2b2b',
            fg='#cccccc',
            justify='center'
        ).pack(pady=10)
        
        tk.Label(
            modern_frame,
            text="✓ Material Design 3\n✓ 부드러운 애니메이션\n✓ 향상된 사용자 경험",
            font=('Segoe UI', 9),
            bg='#2b2b2b',
            fg='#888888',
            justify='left'
        ).pack(pady=10, padx=20)
        
        # Modern UI 사용 가능 여부 확인
        try:
            import flet
            modern_available = True
            button_text = "Modern 선택"
            button_bg = '#6750A4'
        except ImportError:
            modern_available = False
            button_text = "설치 필요"
            button_bg = '#666666'
        
        modern_btn = tk.Button(
            modern_frame,
            text=button_text,
            font=('Segoe UI', 11, 'bold'),
            bg=button_bg,
            fg='white',
            relief='flat',
            padx=30,
            pady=10,
            cursor='hand2' if modern_available else 'arrow',
            state='normal' if modern_available else 'disabled',
            command=lambda: self._select_mode(root, 'modern') if modern_available else None
        )
        modern_btn.pack(pady=20)
        
        if not modern_available:
            tk.Label(
                modern_frame,
                text="pip install flet",
                font=('Consolas', 9),
                bg='#2b2b2b',
                fg='#ff6b6b'
            ).pack()
        
        # 하단 옵션
        bottom_frame = tk.Frame(root, bg='#1e1e1e')
        bottom_frame.pack(fill='x', padx=40, pady=20)
        
        # 기억하기 체크박스
        self.remember_var = tk.BooleanVar(value=False)
        remember_check = tk.Checkbutton(
            bottom_frame,
            text="이 선택을 기억하기",
            variable=self.remember_var,
            font=('Segoe UI', 9),
            bg='#1e1e1e',
            fg='#888888',
            selectcolor='#1e1e1e',
            activebackground='#1e1e1e',
            activeforeground='#888888',
            command=self._on_remember_change
        )
        remember_check.pack(side='left')
        
        # 종료 버튼
        exit_btn = tk.Button(
            bottom_frame,
            text="종료",
            font=('Segoe UI', 9),
            bg='#444444',
            fg='white',
            relief='flat',
            padx=20,
            pady=5,
            cursor='hand2',
            command=root.destroy
        )
        exit_btn.pack(side='right')
        
        # ESC 키로 종료
        root.bind('<Escape>', lambda e: root.destroy())
        
        # 윈도우 실행
        root.mainloop()
        
        return self.selected_mode
    
    def _select_mode(self, root: tk.Tk, mode: UIMode):
        """UI 모드 선택"""
        self.selected_mode = mode
        self.remember_choice = self.remember_var.get()
        root.destroy()
    
    def _on_remember_change(self):
        """기억하기 체크박스 변경"""
        self.remember_choice = self.remember_var.get()


def show_ui_selector() -> Optional[UIMode]:
    """UI 선택 다이얼로그 표시 헬퍼 함수"""
    selector = UIModeSelector()
    mode = selector.show()
    
    # 선택 기억하기 옵션 처리
    if mode and selector.remember_choice:
        from src.config.ui_config import get_ui_config_manager
        ui_config = get_ui_config_manager()
        ui_config.set_ui_mode(mode)
        ui_config.config.show_selector_on_start = False
        ui_config.save_config()
    
    return mode


if __name__ == "__main__":
    # 테스트용
    selected = show_ui_selector()
    print(f"선택된 UI 모드: {selected}")