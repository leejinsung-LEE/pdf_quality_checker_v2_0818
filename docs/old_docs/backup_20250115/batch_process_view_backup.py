# src/ui/views/batch_process_view.py
"""
일괄 처리 뷰

여러 PDF 파일을 일괄적으로 처리하는 UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
import queue
from datetime import datetime
import time

from ..controllers import get_file_controller, get_profile_controller, FileStatus
from ...processing import BatchProcessor


class BatchProcessView(ctk.CTkToplevel):
    """일괄 처리 창"""
    
    def __init__(self, parent):
        """
        일괄 처리 창 초기화
        
        Args:
            parent: 부모 윈도우
        """
        super().__init__(parent)
        
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
        
        # 창 설정
        self.title("일괄 처리")
        self.geometry("1000x700")
        self.resizable(True, True)
        
        # 모달 창 설정
        self.transient(parent)
        self.grab_set()
        
        # UI 생성
        self._create_ui()
        
        # 창 포커스
        self.focus()
        
        # 큐 모니터링 시작
        self._monitor_queue()
        
        # 닫기 이벤트
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_ui(self):
        """UI 생성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 상단: 파일 선택 영역
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # 제목
        title_label = ctk.CTkLabel(
            top_frame,
            text="일괄 처리",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # 파일 선택 버튼들
        button_frame = ctk.CTkFrame(top_frame)
        button_frame.pack()
        
        add_files_btn = ctk.CTkButton(
            button_frame,
            text="파일 추가",
            command=self._add_files,
            width=120
        )
        add_files_btn.pack(side='left', padx=5)
        
        add_folder_btn = ctk.CTkButton(
            button_frame,
            text="폴더 추가",
            command=self._add_folder,
            width=120
        )
        add_folder_btn.pack(side='left', padx=5)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="목록 초기화",
            command=self._clear_list,
            width=120,
            fg_color="gray"
        )
        clear_btn.pack(side='left', padx=5)
        
        # 중단: 파일 목록 및 설정
        middle_frame = ctk.CTkFrame(main_frame)
        middle_frame.pack(fill='both', expand=True, pady=10)
        
        # 좌측: 파일 목록
        left_frame = ctk.CTkFrame(middle_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        list_label = ctk.CTkLabel(
            left_frame,
            text="처리할 파일 목록",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_label.pack(pady=5)
        
        # 파일 수 레이블
        self.file_count_label = ctk.CTkLabel(
            left_frame,
            text="0개 파일",
            text_color="gray"
        )
        self.file_count_label.pack()
        
        # 파일 리스트 프레임
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 파일 트리뷰
        self.file_tree = ttk.Treeview(
            list_frame,
            columns=('size', 'pages', 'status'),
            show='tree headings',
            yscrollcommand=scrollbar.set
        )
        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.file_tree.yview)
        
        # 컬럼 설정
        self.file_tree.heading('#0', text='파일명')
        self.file_tree.heading('size', text='크기')
        self.file_tree.heading('pages', text='페이지')
        self.file_tree.heading('status', text='상태')
        
        self.file_tree.column('#0', width=400)
        self.file_tree.column('size', width=80)
        self.file_tree.column('pages', width=60)
        self.file_tree.column('status', width=100)
        
        # 트리 스타일
        style = ttk.Style()
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b")
        
        # 우측: 처리 설정
        right_frame = ctk.CTkFrame(middle_frame, width=350)
        right_frame.pack(side='right', fill='y', padx=(5, 0))
        right_frame.pack_propagate(False)
        
        settings_label = ctk.CTkLabel(
            right_frame,
            text="처리 설정",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_label.pack(pady=10)
        
        # 설정 스크롤 프레임
        settings_scroll = ctk.CTkScrollableFrame(right_frame)
        settings_scroll.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # 프로파일 선택
        profile_label = ctk.CTkLabel(settings_scroll, text="검사 프로파일:")
        profile_label.pack(anchor='w', pady=(10, 5))
        
        profiles = self.profile_controller.get_profile_list()
        profile_names = [p.name for p in profiles]
        
        self.profile_combo = ctk.CTkComboBox(
            settings_scroll,
            values=profile_names,
            width=300
        )
        self.profile_combo.pack(fill='x', pady=(0, 10))
        
        current_profile, _ = self.profile_controller.get_current_profile()
        self.profile_combo.set(current_profile)
        
        # 출력 설정
        output_label = ctk.CTkLabel(
            settings_scroll,
            text="출력 설정",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        output_label.pack(anchor='w', pady=(20, 5))
        
        # 출력 폴더
        output_folder_label = ctk.CTkLabel(settings_scroll, text="출력 폴더:")
        output_folder_label.pack(anchor='w', pady=(5, 2))
        
        output_frame = ctk.CTkFrame(settings_scroll)
        output_frame.pack(fill='x', pady=(0, 10))
        
        self.output_entry = ctk.CTkEntry(output_frame, width=220)
        self.output_entry.pack(side='left', padx=(0, 5))
        self.output_entry.insert(0, "output")
        
        browse_btn = ctk.CTkButton(
            output_frame,
            text="찾기",
            command=self._browse_output,
            width=60
        )
        browse_btn.pack(side='left')
        
        # 파일 구성
        self.keep_structure = ctk.CTkCheckBox(
            settings_scroll,
            text="원본 폴더 구조 유지"
        )
        self.keep_structure.pack(anchor='w', pady=5)
        
        self.create_subfolders = ctk.CTkCheckBox(
            settings_scroll,
            text="파일별 하위 폴더 생성"
        )
        self.create_subfolders.pack(anchor='w', pady=5)
        
        # 처리 옵션
        options_label = ctk.CTkLabel(
            settings_scroll,
            text="처리 옵션",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        options_label.pack(anchor='w', pady=(20, 5))
        
        self.auto_fix = ctk.CTkCheckBox(
            settings_scroll,
            text="문제 자동 수정"
        )
        self.auto_fix.pack(anchor='w', pady=5)
        self.auto_fix.select()
        
        self.generate_report = ctk.CTkCheckBox(
            settings_scroll,
            text="보고서 생성"
        )
        self.generate_report.pack(anchor='w', pady=5)
        self.generate_report.select()
        
        self.generate_thumbnail = ctk.CTkCheckBox(
            settings_scroll,
            text="썸네일 생성"
        )
        self.generate_thumbnail.pack(anchor='w', pady=5)
        
        # 보고서 형식
        report_format_label = ctk.CTkLabel(settings_scroll, text="보고서 형식:")
        report_format_label.pack(anchor='w', pady=(10, 5))
        
        format_frame = ctk.CTkFrame(settings_scroll)
        format_frame.pack(fill='x', pady=(0, 10))
        
        self.format_html = ctk.CTkCheckBox(format_frame, text="HTML")
        self.format_html.pack(side='left', padx=5)
        self.format_html.select()
        
        self.format_json = ctk.CTkCheckBox(format_frame, text="JSON")
        self.format_json.pack(side='left', padx=5)
        
        self.format_txt = ctk.CTkCheckBox(format_frame, text="TXT")
        self.format_txt.pack(side='left', padx=5)
        
        # 완료 후 동작
        completion_label = ctk.CTkLabel(
            settings_scroll,
            text="완료 후 동작",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        completion_label.pack(anchor='w', pady=(20, 5))
        
        self.open_output = ctk.CTkCheckBox(
            settings_scroll,
            text="출력 폴더 열기"
        )
        self.open_output.pack(anchor='w', pady=5)
        
        self.show_summary = ctk.CTkCheckBox(
            settings_scroll,
            text="요약 보고서 표시"
        )
        self.show_summary.pack(anchor='w', pady=5)
        self.show_summary.select()
        
        # 하단: 진행 상황 및 버튼
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        # 진행 상황
        progress_label = ctk.CTkLabel(
            bottom_frame,
            text="진행 상황",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        progress_label.pack(anchor='w', pady=(0, 5))
        
        # 진행률 바
        self.progress_bar = ctk.CTkProgressBar(bottom_frame, width=None)
        self.progress_bar.pack(fill='x', pady=5)
        self.progress_bar.set(0)
        
        # 상태 레이블
        self.status_label = ctk.CTkLabel(
            bottom_frame,
            text="대기 중...",
            text_color="gray"
        )
        self.status_label.pack(anchor='w', pady=5)
        
        # 상세 정보
        info_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        info_frame.pack(fill='x', pady=5)
        
        self.time_label = ctk.CTkLabel(
            info_frame,
            text="소요 시간: --:--",
            text_color="gray"
        )
        self.time_label.pack(side='left', padx=(0, 20))
        
        self.progress_label = ctk.CTkLabel(
            info_frame,
            text="0 / 0 파일",
            text_color="gray"
        )
        self.progress_label.pack(side='left', padx=(0, 20))
        
        self.speed_label = ctk.CTkLabel(
            info_frame,
            text="속도: -- 파일/분",
            text_color="gray"
        )
        self.speed_label.pack(side='left')
        
        # 버튼
        button_frame = ctk.CTkFrame(bottom_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="취소",
            command=self._cancel_process,
            width=100,
            state='disabled'
        )
        self.cancel_btn.pack(side='right', padx=(5, 0))
        
        self.start_btn = ctk.CTkButton(
            button_frame,
            text="처리 시작",
            command=self._start_process,
            width=100
        )
        self.start_btn.pack(side='right')
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="닫기",
            command=self._on_closing,
            width=100
        )
        close_btn.pack(side='left')
    
    def _add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        )
        
        if files:
            for file in files:
                path = Path(file)
                if path not in self.file_list:
                    self.file_list.append(path)
            
            self._update_file_list()
    
    def _add_folder(self):
        """폴더 추가"""
        folder = filedialog.askdirectory(title="폴더 선택")
        if not folder:
            return
        
        # 재귀적으로 PDF 파일 찾기
        path = Path(folder)
        pdf_files = list(path.glob("**/*.pdf"))
        
        if pdf_files:
            added_count = 0
            for pdf_file in pdf_files:
                if pdf_file not in self.file_list:
                    self.file_list.append(pdf_file)
                    added_count += 1
            
            self._update_file_list()
            messagebox.showinfo("추가 완료", f"{added_count}개의 PDF 파일을 추가했습니다.")
        else:
            messagebox.showinfo("알림", "PDF 파일을 찾을 수 없습니다.")
    
    def _clear_list(self):
        """파일 목록 초기화"""
        if self.file_list:
            if messagebox.askyesno("확인", "파일 목록을 모두 지우시겠습니까?"):
                self.file_list.clear()
                self._update_file_list()
    
    def _update_file_list(self):
        """파일 목록 업데이트"""
        # 트리 초기화
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 파일 추가
        for file_path in self.file_list:
            try:
                # 파일 정보 가져오기
                size = file_path.stat().st_size / (1024 * 1024)  # MB
                size_text = f"{size:.1f} MB"
                
                # 트리에 추가
                self.file_tree.insert(
                    '', 'end',
                    text=file_path.name,
                    values=(size_text, '-', '대기'),
                    tags=('pending',)
                )
            except:
                pass
        
        # 파일 수 업데이트
        self.file_count_label.configure(text=f"{len(self.file_list)}개 파일")
        self.total_count = len(self.file_list)
    
    def _browse_output(self):
        """출력 폴더 선택"""
        folder = filedialog.askdirectory(title="출력 폴더 선택")
        if folder:
            self.output_entry.delete(0, 'end')
            self.output_entry.insert(0, folder)
    
    def _start_process(self):
        """처리 시작"""
        if not self.file_list:
            messagebox.showwarning("경고", "처리할 파일이 없습니다.")
            return
        
        # UI 상태 변경
        self.is_processing = True
        self.start_btn.configure(state='disabled')
        self.cancel_btn.configure(state='normal')
        self.cancel_event.clear()
        
        # 진행 상황 초기화
        self.processed_count = 0
        self.progress_bar.set(0)
        self.status_label.configure(text="처리 준비 중...")
        
        # 시작 시간
        self.start_time = time.time()
        
        # 처리 스레드 시작
        self.process_thread = threading.Thread(target=self._process_files)
        self.process_thread.daemon = True
        self.process_thread.start()
    
    def _process_files(self):
        """파일 처리 (별도 스레드)"""
        try:
            # 설정 수집
            profile = self.profile_combo.get()
            output_folder = Path(self.output_entry.get())
            output_folder.mkdir(parents=True, exist_ok=True)
            
            auto_fix = self.auto_fix.get()
            generate_report = self.generate_report.get()
            generate_thumbnail = self.generate_thumbnail.get()
            
            # 보고서 형식
            report_formats = []
            if self.format_html.get():
                report_formats.append('html')
            if self.format_json.get():
                report_formats.append('json')
            if self.format_txt.get():
                report_formats.append('txt')
            
            # 각 파일 처리
            for i, file_path in enumerate(self.file_list):
                if self.cancel_event.is_set():
                    break
                
                # 상태 업데이트
                self.message_queue.put({
                    'type': 'status',
                    'index': i,
                    'text': f"처리 중: {file_path.name}",
                    'tree_status': '처리 중...'
                })
                
                try:
                    # 파일 처리
                    file_id = self.file_controller.add_file(
                        file_path,
                        profile=profile,
                        auto_fix=auto_fix
                    )
                    
                    # 처리 대기
                    while True:
                        if self.cancel_event.is_set():
                            break
                        
                        status = self.file_controller.get_file_status(file_id)
                        if status in [FileStatus.COMPLETED, FileStatus.ERROR]:
                            break
                        
                        time.sleep(0.1)
                    
                    # 결과 확인
                    if status == FileStatus.COMPLETED:
                        tree_status = '✓ 완료'
                        
                        # 보고서 생성
                        if generate_report:
                            for format_type in report_formats:
                                report_path = output_folder / f"{file_path.stem}_report.{format_type}"
                                # 보고서 생성 로직
                        
                        # 썸네일 생성
                        if generate_thumbnail:
                            # 썸네일 생성 로직
                            pass
                    else:
                        tree_status = '✗ 오류'
                    
                except Exception as e:
                    tree_status = f'✗ {str(e)}'
                
                # 진행 상황 업데이트
                self.processed_count += 1
                progress = self.processed_count / self.total_count
                
                self.message_queue.put({
                    'type': 'progress',
                    'index': i,
                    'progress': progress,
                    'tree_status': tree_status
                })
            
            # 완료
            if not self.cancel_event.is_set():
                self.message_queue.put({'type': 'complete'})
            else:
                self.message_queue.put({'type': 'cancelled'})
                
        except Exception as e:
            self.message_queue.put({
                'type': 'error',
                'message': str(e)
            })
    
    def _cancel_process(self):
        """처리 취소"""
        if messagebox.askyesno("확인", "처리를 취소하시겠습니까?"):
            self.cancel_event.set()
            self.status_label.configure(text="취소 중...")
    
    def _monitor_queue(self):
        """메시지 큐 모니터링"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                if message['type'] == 'status':
                    # 상태 업데이트
                    self.status_label.configure(text=message['text'])
                    
                    # 트리 아이템 업데이트
                    items = self.file_tree.get_children()
                    if message['index'] < len(items):
                        item = items[message['index']]
                        values = list(self.file_tree.item(item)['values'])
                        values[2] = message['tree_status']
                        self.file_tree.item(item, values=values)
                
                elif message['type'] == 'progress':
                    # 진행률 업데이트
                    self.progress_bar.set(message['progress'])
                    self.progress_label.configure(
                        text=f"{self.processed_count} / {self.total_count} 파일"
                    )
                    
                    # 트리 아이템 업데이트
                    items = self.file_tree.get_children()
                    if message['index'] < len(items):
                        item = items[message['index']]
                        values = list(self.file_tree.item(item)['values'])
                        values[2] = message['tree_status']
                        self.file_tree.item(item, values=values)
                    
                    # 시간 및 속도 계산
                    elapsed = time.time() - self.start_time
                    elapsed_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"
                    self.time_label.configure(text=f"소요 시간: {elapsed_str}")
                    
                    if elapsed > 0:
                        speed = (self.processed_count / elapsed) * 60
                        self.speed_label.configure(text=f"속도: {speed:.1f} 파일/분")
                
                elif message['type'] == 'complete':
                    self._on_process_complete()
                
                elif message['type'] == 'cancelled':
                    self._on_process_cancelled()
                
                elif message['type'] == 'error':
                    messagebox.showerror("오류", f"처리 중 오류 발생:\n{message['message']}")
                    self._reset_ui()
                    
        except queue.Empty:
            pass
        
        # 100ms 후 다시 체크
        if self.winfo_exists():
            self.after(100, self._monitor_queue)
    
    def _on_process_complete(self):
        """처리 완료"""
        self.status_label.configure(text="처리 완료!")
        self.progress_bar.set(1.0)
        
        # 요약 보고서
        if self.show_summary.get():
            elapsed = time.time() - self.start_time
            elapsed_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"
            
            summary = f"""일괄 처리 완료
            
처리된 파일: {self.processed_count}개
소요 시간: {elapsed_str}
평균 속도: {(self.processed_count / elapsed * 60):.1f} 파일/분

출력 폴더: {self.output_entry.get()}"""
            
            messagebox.showinfo("처리 완료", summary)
        
        # 출력 폴더 열기
        if self.open_output.get():
            import os
            import platform
            
            output_path = Path(self.output_entry.get())
            if output_path.exists():
                if platform.system() == 'Windows':
                    os.startfile(output_path)
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{output_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{output_path}"')
        
        self._reset_ui()
    
    def _on_process_cancelled(self):
        """처리 취소됨"""
        self.status_label.configure(text="처리가 취소되었습니다.")
        messagebox.showinfo("취소", f"처리가 취소되었습니다.\n완료: {self.processed_count}/{self.total_count} 파일")
        self._reset_ui()
    
    def _reset_ui(self):
        """UI 초기화"""
        self.is_processing = False
        self.start_btn.configure(state='normal')
        self.cancel_btn.configure(state='disabled')
    
    def _on_closing(self):
        """창 닫기"""
        if self.is_processing:
            if not messagebox.askyesno("확인", "처리가 진행 중입니다.\n창을 닫으시겠습니까?"):
                return
            
            self.cancel_event.set()
            if self.process_thread:
                self.process_thread.join(timeout=2)
        
        self.destroy()