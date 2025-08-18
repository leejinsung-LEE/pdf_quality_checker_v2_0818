"""
PDF Quality Checker v2.0 - 메인 애플리케이션 모듈
CustomTkinter 기반 GUI 구현
주요 기능: 애플리케이션 초기화, 백그라운드 처리, 이벤트 관리
최종 수정: 2025-01-11
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from pathlib import Path
import sys
import os
import threading
import queue
from datetime import datetime
from typing import Optional, Dict, Any, List

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# CustomTkinter 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# v2 핵심 모듈 임포트
from src.core.quality_checker import PDFQualityChecker, QualityCheckResult
from src.core.profiles import get_profile_manager
from src.external import get_tool_manager

# GUI 모듈 임포트
from .windows.main_window import MainWindow


class PDFQualityCheckerApp:
    """
    PDF Quality Checker v2.0 메인 애플리케이션 클래스
    
    주요 기능:
    - GUI 초기화 및 관리
    - 백그라운드 PDF 처리 스레드 관리
    - 파일 큐 및 결과 큐 관리
    - 주기적 UI 업데이트
    """
    
    def __init__(self):
        """애플리케이션 초기화"""
        # 메인 윈도우 생성
        self.root = ctk.CTk()
        self.root.title("PDF Quality Checker v2.0")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # 아이콘 설정 (있는 경우)
        try:
            icon_path = Path("assets/icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            # 아이콘 설정 실패는 무시
            pass
        
        # v2 핵심 시스템 초기화
        self.quality_checker = PDFQualityChecker()
        self.profile_manager = get_profile_manager()
        self.tool_manager = get_tool_manager()
        
        # 큐 시스템 (스레드 간 통신)
        self.file_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
        # 메인 윈도우는 별도로 생성 (tkinterdnd2.Tk를 상속받음)
        # self.main_window = MainWindow()
        # 임시로 컨트롤러 사용
        from .controllers import get_file_controller
        self.file_controller = get_file_controller()
        
        # 처리 스레드 시작
        self._start_processing_thread()
        
        # 주기적 업데이트
        self._schedule_updates()
        
        # 종료 이벤트
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _start_processing_thread(self):
        """백그라운드 처리 스레드 시작"""
        def process_files():
            while True:
                try:
                    # 파일 큐에서 작업 가져오기
                    file_info = self.file_queue.get(timeout=1)
                    if file_info is None:  # 종료 신호
                        break
                    
                    # PDF 품질 검사 수행
                    file_path = file_info['path']
                    profile_name = file_info.get('profile', 'default')
                    
                    result = self.quality_checker.check(file_path, profile_name)
                    
                    # 결과를 결과 큐에 추가
                    self.result_queue.put({
                        'file_path': file_path,
                        'result': result,
                        'timestamp': datetime.now()
                    })
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.result_queue.put({
                        'error': str(e),
                        'file_path': file_info.get('path', 'Unknown')
                    })
        
        self.processing_thread = threading.Thread(target=process_files, daemon=True)
        self.processing_thread.start()
    
    def _schedule_updates(self):
        """주기적 UI 업데이트"""
        # 결과 큐 확인
        try:
            while True:
                result = self.result_queue.get_nowait()
                if 'error' in result:
                    # 오류 처리 (main_window 대신 직접 처리)
                    print(f"Processing error: {result['error']}")
                else:
                    # 완료 처리
                    print(f"Processing complete: {result['file_path']}")
        except queue.Empty:
            pass
        
        # 100ms 후 다시 호출
        self.root.after(100, self._schedule_updates)
    
    def process_file(self, file_path: Path, profile_name: str = None):
        """파일 처리 요청"""
        self.file_queue.put({
            'path': file_path,
            'profile': profile_name or self.profile_manager.current_profile_name
        })
    
    def on_closing(self):
        """프로그램 종료"""
        if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
            # 처리 스레드 종료
            self.file_queue.put(None)
            self.root.destroy()
    
    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop()


# 실행 진입점
if __name__ == "__main__":
    app = PDFQualityCheckerApp()
    app.run()