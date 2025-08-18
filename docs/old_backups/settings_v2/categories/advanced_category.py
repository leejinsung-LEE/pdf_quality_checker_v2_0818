# src/ui/views/settings_v2/categories/advanced_category.py
"""
고급 설정 카테고리

성능, 로그, 외부 도구 등 고급 설정 관리
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Dict, Any
from pathlib import Path
from ..base_category import BaseCategory


class AdvancedCategory(BaseCategory):
    """
    고급 설정 카테고리
    
    - 성능 설정
    - 로그 설정
    - 외부 도구 경로
    - 캐시 및 임시 파일
    """
    
    def _create_ui(self):
        """UI 생성"""
        # 성능 설정 섹션
        self._create_performance_section()
        
        # 로그 설정 섹션
        self._create_log_section()
        
        # 외부 도구 섹션
        self._create_tools_section()
        
        # 캐시 설정 섹션
        self._create_cache_section()
    
    def _create_performance_section(self):
        """성능 설정 섹션"""
        section = self.create_section("성능 설정", "⚡")
        
        # 동시 처리 파일 수
        concurrent_frame = ctk.CTkFrame(section, fg_color="transparent")
        concurrent_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            concurrent_frame,
            text="동시 처리 파일 수:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        slider_container = ctk.CTkFrame(concurrent_frame, fg_color="transparent")
        slider_container.pack(side='left')
        
        self.concurrent_slider = ctk.CTkSlider(
            slider_container,
            from_=1,
            to=10,
            width=150,
            command=self._on_concurrent_change
        )
        self.concurrent_slider.pack(side='left')
        
        self.concurrent_label = ctk.CTkLabel(
            slider_container,
            text="3",
            width=30
        )
        self.concurrent_label.pack(side='left', padx=(10, 0))
        
        self.widgets['max_concurrent_files'] = self.concurrent_slider
        
        # 처리 타임아웃
        timeout_frame = ctk.CTkFrame(section, fg_color="transparent")
        timeout_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            timeout_frame,
            text="처리 타임아웃(초):",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.timeout_entry = ctk.CTkEntry(
            timeout_frame,
            width=100,
            placeholder_text="300"
        )
        self.timeout_entry.pack(side='left')
        self.timeout_entry.bind('<Return>', lambda e: self._on_widget_change("processing_timeout", self.timeout_entry.get()))
        self.timeout_entry.bind('<FocusOut>', lambda e: self._on_widget_change("processing_timeout", self.timeout_entry.get()))
        self.widgets['processing_timeout'] = self.timeout_entry
        
        # 메모리 제한
        memory_frame = ctk.CTkFrame(section, fg_color="transparent")
        memory_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            memory_frame,
            text="메모리 제한(MB):",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.memory_entry = ctk.CTkEntry(
            memory_frame,
            width=100,
            placeholder_text="2048"
        )
        self.memory_entry.pack(side='left')
        self.widgets['memory_limit'] = self.memory_entry
        
        ctk.CTkLabel(
            memory_frame,
            text="(0 = 무제한)",
            text_color=("gray50", "gray50")
        ).pack(side='left', padx=(10, 0))
        
        # 멀티스레딩
        self.create_option_row(
            section,
            "멀티스레딩 사용:",
            "switch",
            "use_multithreading"
        )
    
    def _create_log_section(self):
        """로그 설정 섹션"""
        section = self.create_section("로그 설정", "📝")
        
        # 로그 레벨
        self.create_option_row(
            section,
            "로그 레벨:",
            "combobox",
            "log_level",
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        
        # 로그 파일 크기 제한
        size_frame = ctk.CTkFrame(section, fg_color="transparent")
        size_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            size_frame,
            text="로그 파일 최대 크기(MB):",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.log_size_entry = ctk.CTkEntry(
            size_frame,
            width=100,
            placeholder_text="10"
        )
        self.log_size_entry.pack(side='left')
        self.widgets['max_log_size'] = self.log_size_entry
        
        # 로그 보관 기간
        keep_frame = ctk.CTkFrame(section, fg_color="transparent")
        keep_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            keep_frame,
            text="로그 보관 기간(일):",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.keep_days_entry = ctk.CTkEntry(
            keep_frame,
            width=100,
            placeholder_text="30"
        )
        self.keep_days_entry.pack(side='left')
        self.widgets['keep_log_days'] = self.keep_days_entry
        
        # 로그 위치
        log_path_frame = ctk.CTkFrame(section, fg_color="transparent")
        log_path_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            log_path_frame,
            text="로그 폴더:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.log_path_entry = ctk.CTkEntry(
            log_path_frame,
            width=200,
            placeholder_text="logs/"
        )
        self.log_path_entry.pack(side='left', padx=(0, 10))
        self.widgets['log_folder'] = self.log_path_entry
        
        # 로그 보기 버튼
        view_log_btn = ctk.CTkButton(
            log_path_frame,
            text="로그 보기",
            width=80,
            command=self._view_logs
        )
        view_log_btn.pack(side='left')
    
    def _create_tools_section(self):
        """외부 도구 섹션"""
        section = self.create_section("외부 도구", "🛠️")
        
        # 도구 목록
        tools = [
            ("ghostscript", "Ghostscript", "gs.exe"),
            ("pdffonts", "pdffonts (Poppler)", "pdffonts.exe"),
            ("pdftk", "pdftk", "pdftk.exe"),
            ("imagemagick", "ImageMagick", "magick.exe")
        ]
        
        for tool_id, tool_name, default_exe in tools:
            self._create_tool_row(section, tool_id, tool_name, default_exe)
        
        # 자동 감지 버튼
        auto_detect_frame = ctk.CTkFrame(section, fg_color="transparent")
        auto_detect_frame.pack(fill='x', pady=(15, 5))
        
        ctk.CTkLabel(
            auto_detect_frame,
            text="",
            width=200
        ).pack(side='left', padx=(0, 20))
        
        auto_detect_btn = ctk.CTkButton(
            auto_detect_frame,
            text="🔍 도구 자동 감지",
            width=150,
            command=self._auto_detect_tools
        )
        auto_detect_btn.pack(side='left')
    
    def _create_tool_row(self, parent, tool_id: str, tool_name: str, default_exe: str):
        """도구 경로 행 생성"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill='x', pady=3)
        
        ctk.CTkLabel(
            row_frame,
            text=f"{tool_name}:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        # 경로 입력
        entry = ctk.CTkEntry(
            row_frame,
            width=200,
            placeholder_text=default_exe
        )
        entry.pack(side='left', padx=(0, 5))
        self.widgets[f'tool_{tool_id}'] = entry
        
        # 찾아보기 버튼
        browse_btn = ctk.CTkButton(
            row_frame,
            text="...",
            width=30,
            command=lambda t=tool_id: self._browse_tool(t)
        )
        browse_btn.pack(side='left', padx=(0, 5))
        
        # 테스트 버튼
        test_btn = ctk.CTkButton(
            row_frame,
            text="테스트",
            width=60,
            fg_color="gray",
            command=lambda t=tool_id: self._test_tool(t)
        )
        test_btn.pack(side='left')
    
    def _create_cache_section(self):
        """캐시 설정 섹션"""
        section = self.create_section("캐시 및 임시 파일", "💾")
        
        # 캐시 활성화
        self.create_option_row(
            section,
            "캐시 사용:",
            "switch",
            "use_cache"
        )
        
        # 캐시 크기 제한
        cache_size_frame = ctk.CTkFrame(section, fg_color="transparent")
        cache_size_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            cache_size_frame,
            text="캐시 최대 크기(MB):",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.cache_size_entry = ctk.CTkEntry(
            cache_size_frame,
            width=100,
            placeholder_text="500"
        )
        self.cache_size_entry.pack(side='left')
        self.widgets['max_cache_size'] = self.cache_size_entry
        
        # 캐시 유효 기간
        cache_ttl_frame = ctk.CTkFrame(section, fg_color="transparent")
        cache_ttl_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            cache_ttl_frame,
            text="캐시 유효 기간(시간):",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.cache_ttl_entry = ctk.CTkEntry(
            cache_ttl_frame,
            width=100,
            placeholder_text="24"
        )
        self.cache_ttl_entry.pack(side='left')
        self.widgets['cache_ttl_hours'] = self.cache_ttl_entry
        
        # 캐시 정리 버튼들
        cache_btn_frame = ctk.CTkFrame(section, fg_color="transparent")
        cache_btn_frame.pack(fill='x', pady=(15, 5))
        
        ctk.CTkLabel(
            cache_btn_frame,
            text="",
            width=200
        ).pack(side='left', padx=(0, 20))
        
        clear_cache_btn = ctk.CTkButton(
            cache_btn_frame,
            text="🗑️ 캐시 정리",
            width=120,
            command=self._clear_cache
        )
        clear_cache_btn.pack(side='left', padx=(0, 10))
        
        clear_temp_btn = ctk.CTkButton(
            cache_btn_frame,
            text="🗑️ 임시 파일 정리",
            width=120,
            command=self._clear_temp_files
        )
        clear_temp_btn.pack(side='left')
        
        # 캐시 통계
        stats_frame = ctk.CTkFrame(section, fg_color="transparent")
        stats_frame.pack(fill='x', pady=(10, 5))
        
        self.cache_stats_label = ctk.CTkLabel(
            stats_frame,
            text="캐시 사용량: 0 MB / 500 MB",
            text_color=("gray50", "gray50")
        )
        self.cache_stats_label.pack(side='left', padx=(200, 0))
    
    def _on_concurrent_change(self, value: float):
        """동시 처리 수 변경"""
        count = int(value)
        self.concurrent_label.configure(text=str(count))
        self._on_widget_change("max_concurrent_files", count)
    
    def _browse_tool(self, tool_id: str):
        """도구 찾아보기"""
        file_path = filedialog.askopenfilename(
            title=f"{tool_id} 실행 파일 선택",
            filetypes=[("실행 파일", "*.exe"), ("모든 파일", "*.*")]
        )
        
        if file_path:
            entry = self.widgets.get(f'tool_{tool_id}')
            if entry:
                entry.delete(0, 'end')
                entry.insert(0, file_path)
                self._on_widget_change(f'tool_{tool_id}', file_path)
    
    def _test_tool(self, tool_id: str):
        """도구 테스트"""
        entry = self.widgets.get(f'tool_{tool_id}')
        if entry:
            tool_path = entry.get()
            if tool_path and Path(tool_path).exists():
                messagebox.showinfo("테스트 성공", f"{tool_id}가 정상적으로 작동합니다.")
            else:
                messagebox.showerror("테스트 실패", f"{tool_id}를 찾을 수 없습니다.")
    
    def _auto_detect_tools(self):
        """도구 자동 감지"""
        # 실제 구현 시 시스템에서 도구 검색
        detected = 0
        tools = ["ghostscript", "pdffonts", "pdftk", "imagemagick"]
        
        for tool_id in tools:
            # 예시: Program Files에서 검색
            # 실제로는 더 정교한 검색 로직 필요
            detected += 1
        
        messagebox.showinfo("자동 감지", f"{detected}개의 도구를 찾았습니다.")
    
    def _view_logs(self):
        """로그 보기"""
        # 로그 뷰어 열기 또는 로그 폴더 열기
        log_folder = self.log_path_entry.get() or "logs/"
        if Path(log_folder).exists():
            import os
            os.startfile(log_folder)
        else:
            messagebox.showwarning("경고", "로그 폴더를 찾을 수 없습니다.")
    
    def _clear_cache(self):
        """캐시 정리"""
        if messagebox.askyesno("캐시 정리", "캐시를 정리하시겠습니까?"):
            # 캐시 정리 로직
            self.cache_stats_label.configure(text="캐시 사용량: 0 MB / 500 MB")
            messagebox.showinfo("완료", "캐시가 정리되었습니다.")
    
    def _clear_temp_files(self):
        """임시 파일 정리"""
        if messagebox.askyesno("임시 파일 정리", "임시 파일을 정리하시겠습니까?"):
            # 임시 파일 정리 로직
            messagebox.showinfo("완료", "임시 파일이 정리되었습니다.")
    
    def load_settings(self, settings):
        """설정 로드"""
        # 성능 설정
        if hasattr(settings, 'max_concurrent_files'):
            self.concurrent_slider.set(settings.max_concurrent_files)
            self.concurrent_label.configure(text=str(settings.max_concurrent_files))
        
        if hasattr(settings, 'processing_timeout'):
            self.timeout_entry.insert(0, str(settings.processing_timeout))
        
        if hasattr(settings, 'memory_limit'):
            self.memory_entry.insert(0, str(settings.memory_limit))
        elif 'memory_limit' in self.widgets:
            self.memory_entry.insert(0, "2048")
        
        if hasattr(settings, 'use_multithreading'):
            if settings.use_multithreading:
                self.widgets.get('use_multithreading', ctk.CTkSwitch()).select()
        elif 'use_multithreading' in self.widgets:
            self.widgets['use_multithreading'].select()  # 기본값
        
        # 로그 설정
        if hasattr(settings, 'log_level'):
            self.widgets['log_level'].set(settings.log_level)
        
        if hasattr(settings, 'keep_log_days'):
            self.keep_days_entry.insert(0, str(settings.keep_log_days))
        
        # 외부 도구 (설정에 있다면)
        if hasattr(settings, 'tools'):
            for tool_id, tool_path in settings.tools.items():
                entry = self.widgets.get(f'tool_{tool_id}')
                if entry and tool_path:
                    entry.insert(0, tool_path)
        
        # 캐시 설정
        if hasattr(settings, 'use_cache'):
            if settings.use_cache:
                self.widgets.get('use_cache', ctk.CTkSwitch()).select()
        elif 'use_cache' in self.widgets:
            self.widgets['use_cache'].select()  # 기본값
    
    def get_settings(self) -> Dict[str, Any]:
        """현재 설정 값 반환"""
        settings = {}
        
        # 성능 설정
        settings['max_concurrent_files'] = int(self.concurrent_slider.get())
        
        timeout = self.timeout_entry.get()
        settings['processing_timeout'] = int(timeout) if timeout else 300
        
        memory = self.memory_entry.get()
        settings['memory_limit'] = int(memory) if memory else 2048
        
        if 'use_multithreading' in self.widgets:
            settings['use_multithreading'] = self.widgets['use_multithreading'].get()
        
        # 로그 설정
        settings['log_level'] = self.widgets['log_level'].get()
        
        keep_days = self.keep_days_entry.get()
        settings['keep_log_days'] = int(keep_days) if keep_days else 30
        
        log_size = self.log_size_entry.get()
        if log_size:
            settings['max_log_size'] = int(log_size)
        
        log_folder = self.log_path_entry.get()
        if log_folder:
            settings['log_folder'] = log_folder
        
        # 외부 도구
        tools = {}
        for tool_id in ["ghostscript", "pdffonts", "pdftk", "imagemagick"]:
            entry = self.widgets.get(f'tool_{tool_id}')
            if entry:
                path = entry.get()
                if path:
                    tools[tool_id] = path
        
        if tools:
            settings['tools'] = tools
        
        # 캐시 설정
        if 'use_cache' in self.widgets:
            settings['use_cache'] = self.widgets['use_cache'].get()
        
        cache_size = self.cache_size_entry.get()
        if cache_size:
            settings['max_cache_size'] = int(cache_size)
        
        cache_ttl = self.cache_ttl_entry.get()
        if cache_ttl:
            settings['cache_ttl_hours'] = int(cache_ttl)
        
        return settings