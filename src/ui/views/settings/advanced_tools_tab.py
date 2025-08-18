# src/ui/views/settings/advanced_tools_tab.py
"""
환경설정 뷰 - 고급 및 외부 도구 설정 탭

이 모듈은 고급 설정과 외부 도구 설정 탭들의 UI 생성과 관련 기능을 담당합니다.
- 고급 처리 설정 (동시 처리 파일 수, 타임아웃)
- 로그 설정 (레벨, 보관 기간)
- 외부 도구 경로 설정 및 테스트

AI 친화적 설계:
- 두 탭을 하나의 모듈에서 처리 (연관성이 높음)
- 외부 도구 자동 감지 기능 포함
- 설정 테스트 및 검증 기능
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Dict, Any, Callable
from pathlib import Path


class AdvancedTabHelper:
    """고급 설정 탭 헬퍼 클래스"""
    
    @staticmethod
    def create_tab(parent: ctk.CTkFrame, widgets: Dict[str, Any]) -> ctk.CTkLabel:
        """
        고급 탭 생성
        
        Args:
            parent: 부모 프레임 (탭 프레임)
            widgets: 위젯 딕셔너리 (참조로 전달)
            
        Returns:
            concurrent_label: 동시 처리 파일 수 표시 레이블
        """
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 처리 설정 섹션
        concurrent_label = AdvancedTabHelper._create_processing_section(scroll_frame, widgets)
        
        # 로그 설정 섹션
        AdvancedTabHelper._create_log_section(scroll_frame, widgets)
        
        return concurrent_label
    
    @staticmethod
    def _create_processing_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> ctk.CTkLabel:
        """처리 설정 섹션 생성"""
        # 제목
        processing_label = ctk.CTkLabel(
            parent,
            text="처리 설정",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        processing_label.pack(fill='x', pady=(0, 10))
        
        # 동시 처리 파일 수
        concurrent_frame = ctk.CTkFrame(parent, fg_color="transparent")
        concurrent_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(concurrent_frame, text="동시 처리 파일 수:", width=150, anchor='w').pack(side='left')
        widgets['max_concurrent_files'] = ctk.CTkSlider(
            concurrent_frame,
            from_=1,
            to=10,
            width=200
        )
        widgets['max_concurrent_files'].pack(side='left', padx=(0, 10))
        
        concurrent_label = ctk.CTkLabel(concurrent_frame, text="3")
        concurrent_label.pack(side='left')
        
        widgets['max_concurrent_files'].configure(
            command=lambda v: concurrent_label.configure(text=str(int(v)))
        )
        
        # 처리 타임아웃
        timeout_frame = ctk.CTkFrame(parent, fg_color="transparent")
        timeout_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(timeout_frame, text="처리 타임아웃(초):", width=150, anchor='w').pack(side='left')
        widgets['processing_timeout'] = ctk.CTkEntry(
            timeout_frame,
            width=100
        )
        widgets['processing_timeout'].pack(side='left')
        
        return concurrent_label
    
    @staticmethod
    def _create_log_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """로그 설정 섹션 생성"""
        # 제목
        log_label = ctk.CTkLabel(
            parent,
            text="로그 설정",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        log_label.pack(fill='x', pady=(20, 10))
        
        # 로그 레벨
        log_level_frame = ctk.CTkFrame(parent, fg_color="transparent")
        log_level_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(log_level_frame, text="로그 레벨:", width=150, anchor='w').pack(side='left')
        widgets['log_level'] = ctk.CTkComboBox(
            log_level_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=200
        )
        widgets['log_level'].pack(side='left')
        
        # 로그 보관 기간
        log_keep_frame = ctk.CTkFrame(parent, fg_color="transparent")
        log_keep_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(log_keep_frame, text="로그 보관 기간(일):", width=150, anchor='w').pack(side='left')
        widgets['keep_log_days'] = ctk.CTkEntry(
            log_keep_frame,
            width=100
        )
        widgets['keep_log_days'].pack(side='left')
    
    @staticmethod
    def load_settings(widgets: Dict[str, Any], settings, concurrent_label: ctk.CTkLabel) -> None:
        """고급 설정 로드"""
        # 동시 처리 파일 수
        if hasattr(settings, 'max_concurrent_files'):
            widgets['max_concurrent_files'].set(settings.max_concurrent_files)
            concurrent_label.configure(text=str(settings.max_concurrent_files))
        
        # 처리 타임아웃
        if hasattr(settings, 'processing_timeout'):
            widgets['processing_timeout'].insert(0, str(settings.processing_timeout))
        
        # 로그 설정
        if hasattr(settings, 'log_level'):
            widgets['log_level'].set(settings.log_level)
        
        if hasattr(settings, 'keep_log_days'):
            widgets['keep_log_days'].insert(0, str(settings.keep_log_days))
    
    @staticmethod
    def collect_settings(widgets: Dict[str, Any]) -> Dict[str, Any]:
        """고급 설정 수집"""
        settings = {}
        
        # 동시 처리 파일 수
        settings['max_concurrent_files'] = int(widgets['max_concurrent_files'].get())
        
        # 처리 타임아웃
        try:
            settings['processing_timeout'] = int(widgets['processing_timeout'].get())
        except:
            settings['processing_timeout'] = 300
        
        # 로그 설정
        settings['log_level'] = widgets['log_level'].get()
        
        try:
            settings['keep_log_days'] = int(widgets['keep_log_days'].get())
        except:
            settings['keep_log_days'] = 30
        
        return settings


class ToolsTabHelper:
    """외부 도구 설정 탭 헬퍼 클래스"""
    
    @staticmethod
    def create_tab(
        parent: ctk.CTkFrame, 
        widgets: Dict[str, Any], 
        settings_controller,
        browse_callback: Callable[[str], None],
        test_callback: Callable[[str], None],
        auto_detect_callback: Callable[[], None]
    ) -> None:
        """
        외부 도구 탭 생성
        
        Args:
            parent: 부모 프레임 (탭 프레임)
            widgets: 위젯 딕셔너리 (참조로 전달)
            settings_controller: 설정 컨트롤러
            browse_callback: 도구 찾기 콜백
            test_callback: 도구 테스트 콜백
            auto_detect_callback: 자동 감지 콜백
        """
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 설명
        info_label = ctk.CTkLabel(
            scroll_frame,
            text="PDF 처리에 필요한 외부 도구들의 경로를 설정합니다.",
            text_color="gray"
        )
        info_label.pack(fill='x', pady=(0, 20))
        
        # 도구별 설정 생성
        ToolsTabHelper._create_tool_sections(
            scroll_frame, widgets, settings_controller, 
            browse_callback, test_callback
        )
        
        # 자동 감지 버튼
        auto_detect_btn = ctk.CTkButton(
            scroll_frame,
            text="자동 감지",
            command=auto_detect_callback
        )
        auto_detect_btn.pack(pady=20)
    
    @staticmethod
    def _create_tool_sections(
        parent: ctk.CTkScrollableFrame, 
        widgets: Dict[str, Any], 
        settings_controller,
        browse_callback: Callable[[str], None],
        test_callback: Callable[[str], None]
    ) -> None:
        """도구별 설정 섹션 생성"""
        # 도구 상태 가져오기
        tools_status = settings_controller.get_external_tools_status()
        
        for tool_name, tool_info in tools_status.items():
            # 도구 프레임
            tool_frame = ctk.CTkFrame(parent)
            tool_frame.pack(fill='x', pady=(0, 15))
            
            # 도구 이름과 상태
            header_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
            header_frame.pack(fill='x', padx=10, pady=(10, 5))
            
            name_label = ctk.CTkLabel(
                header_frame,
                text=tool_name.capitalize(),
                font=ctk.CTkFont(size=14, weight="bold")
            )
            name_label.pack(side='left')
            
            # 상태 표시
            status_text = "✓ 사용 가능" if tool_info.available else "✗ 찾을 수 없음"
            status_color = "green" if tool_info.available else "red"
            
            status_label = ctk.CTkLabel(
                header_frame,
                text=status_text,
                text_color=status_color
            )
            status_label.pack(side='left', padx=(10, 0))
            
            if tool_info.version:
                version_label = ctk.CTkLabel(
                    header_frame,
                    text=f"(v{tool_info.version})",
                    text_color="gray"
                )
                version_label.pack(side='left', padx=(5, 0))
            
            # 경로 입력 및 버튼들
            ToolsTabHelper._create_tool_controls(
                tool_frame, widgets, tool_name, tool_info,
                browse_callback, test_callback
            )
    
    @staticmethod
    def _create_tool_controls(
        parent: ctk.CTkFrame,
        widgets: Dict[str, Any],
        tool_name: str,
        tool_info: Dict[str, Any],
        browse_callback: Callable[[str], None],
        test_callback: Callable[[str], None]
    ) -> None:
        """도구별 컨트롤 생성"""
        # 경로 입력 프레임
        path_frame = ctk.CTkFrame(parent, fg_color="transparent")
        path_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tool_entry_key = f'tool_{tool_name}'
        widgets[tool_entry_key] = ctk.CTkEntry(
            path_frame,
            placeholder_text="경로를 입력하거나 찾아보기..."
        )
        widgets[tool_entry_key].pack(side='left', fill='x', expand=True)
        
        if tool_info.path:
            widgets[tool_entry_key].insert(0, str(tool_info.path))
        
        # 찾아보기 버튼
        browse_btn = ctk.CTkButton(
            path_frame,
            text="찾아보기",
            width=100,
            command=lambda tn=tool_name: browse_callback(f'tool_{tn}')
        )
        browse_btn.pack(side='left', padx=(10, 0))
        
        # 테스트 버튼
        test_btn = ctk.CTkButton(
            path_frame,
            text="테스트",
            width=70,
            fg_color="gray",
            command=lambda tn=tool_name: test_callback(tn)
        )
        test_btn.pack(side='left', padx=(5, 0))
    
    @staticmethod
    def browse_tool(widget_key: str, widgets: Dict[str, Any]) -> None:
        """도구 실행 파일 찾아보기"""
        file = filedialog.askopenfilename(
            title="실행 파일 선택",
            filetypes=[("실행 파일", "*.exe"), ("모든 파일", "*.*")]
        )
        if file:
            widgets[widget_key].delete(0, 'end')
            widgets[widget_key].insert(0, file)
    
    @staticmethod
    def test_tool(tool_name: str, widgets: Dict[str, Any], settings_controller) -> None:
        """외부 도구 테스트"""
        widget_key = f'tool_{tool_name}'
        tool_path = widgets[widget_key].get()
        
        if not tool_path:
            messagebox.showwarning("경고", "도구 경로를 입력해주세요.")
            return
        
        # 도구 경로 설정 및 테스트
        if settings_controller.configure_external_tool(tool_name, Path(tool_path)):
            # 버전 확인
            version = settings_controller.tool_manager.get_tool_version(tool_name)
            if version:
                messagebox.showinfo("성공", f"{tool_name} 테스트 성공!\n버전: {version}")
            else:
                messagebox.showinfo("성공", f"{tool_name} 테스트 성공!")
        else:
            messagebox.showerror("실패", f"{tool_name} 테스트 실패!")
    
    @staticmethod
    def auto_detect_tools(widgets: Dict[str, Any], settings_controller) -> None:
        """외부 도구 자동 감지"""
        detected = 0
        
        for tool_name in ['ghostscript', 'pdffonts']:
            if settings_controller.tool_manager.find_tool(tool_name):
                path = settings_controller.tool_manager.get_tool_path(tool_name)
                if path:
                    widget_key = f'tool_{tool_name}'
                    widgets[widget_key].delete(0, 'end')
                    widgets[widget_key].insert(0, str(path))
                    detected += 1
        
        if detected > 0:
            messagebox.showinfo("자동 감지", f"{detected}개의 도구를 찾았습니다.")
        else:
            messagebox.showinfo("자동 감지", "도구를 찾을 수 없습니다.\n수동으로 경로를 설정해주세요.")
    
    @staticmethod
    def save_tool_settings(widgets: Dict[str, Any], settings_controller) -> None:
        """외부 도구 설정 저장"""
        for tool_name in ['ghostscript', 'pdffonts']:
            widget_key = f'tool_{tool_name}'
            if widget_key in widgets:
                tool_path = widgets[widget_key].get()
                if tool_path:
                    settings_controller.configure_external_tool(
                        tool_name,
                        Path(tool_path)
                    )