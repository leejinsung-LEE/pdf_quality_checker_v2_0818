"""
일괄 처리 뷰 - 메인 클래스
기능: 여러 PDF 파일을 일괄 처리
의존성: customtkinter, tkinter, BatchProcessor
최종 수정: 2025-01-12

AI 친화적 문서화:
- 역할: PDF 일괄 처리 UI 제공
- 입력: PDF 파일 목록, 처리 설정
- 출력: 처리된 파일, 보고서
- 상태: 처리 진행 상황, 파일 목록
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
import queue
from datetime import datetime

# 컨트롤러 및 프로세서
from ...controllers import get_file_controller, get_profile_controller, FileStatus
from ....processing import BatchProcessor

# 헬퍼 클래스 import
from .ui_builder import UIBuilder
from .file_manager import FileManager
from .process_handler import ProcessHandler
from .monitor import ProgressMonitor


class BatchProcessView(ctk.CTkToplevel):
    """일괄 처리 창"""
    
    def __init__(self, parent):
        """
        일괄 처리 창 초기화
        
        Args:
            parent: 부모 윈도우
        """
        super().__init__(parent)
        
        # 컨트롤러 및 프로세서
        self.file_controller = get_file_controller()
        self.profile_controller = get_profile_controller()
        self.batch_processor = BatchProcessor()
        
        # 처리 상태
        self.is_processing = False
        self.process_thread = None
        self.cancel_event = threading.Event()
        self.message_queue = queue.Queue()
        
        # 파일 목록
        self.file_list = []
        self.processed_count = 0
        self.total_count = 0
        
        # UI 위젯 참조
        self.widgets = {}
        
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
            'info': '#17a2b8',
            'border': '#404040'
        }
        
        # 창 설정
        self.title("일괄 처리")
        self.geometry("1000x700")
        self.resizable(True, True)
        
        # 모달 창 설정
        self.transient(parent)
        self.grab_set()
        
        # 헬퍼 초기화
        self.ui_builder = UIBuilder(self)
        self.file_manager = FileManager(self)
        self.process_handler = ProcessHandler(self)
        self.progress_monitor = ProgressMonitor(self)
        
        # UI 생성
        self._create_ui()
        
        # 창 포커스
        self.focus()
        
        # 큐 모니터링 시작
        self.progress_monitor.start_monitoring()
        
        # 닫기 이벤트
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_ui(self):
        """UI 구성"""
        self.ui_builder.create_ui()
    
    def add_files(self):
        """파일 추가"""
        self.file_manager.add_files()
    
    def add_folder(self):
        """폴더 추가"""
        self.file_manager.add_folder()
    
    def clear_list(self):
        """파일 목록 초기화"""
        self.file_manager.clear_list()
    
    def start_process(self):
        """처리 시작"""
        self.process_handler.start_process()
    
    def cancel_process(self):
        """처리 취소"""
        self.process_handler.cancel_process()
    
    def _on_closing(self):
        """창 닫기 이벤트"""
        if self.is_processing:
            if tk.messagebox.askyesno("확인", "처리가 진행 중입니다. 정말 닫으시겠습니까?"):
                self.cancel_event.set()
                if self.process_thread and self.process_thread.is_alive():
                    self.process_thread.join(timeout=2.0)
        self.destroy()