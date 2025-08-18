# src/ui/views/settings_v2/base_category.py
"""
설정 카테고리 기본 클래스

모든 설정 카테고리가 상속받는 기본 클래스
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional, List
from abc import ABC, abstractmethod


class BaseCategory(ctk.CTkScrollableFrame, ABC):
    """
    설정 카테고리 기본 클래스
    
    모든 설정 카테고리가 공통으로 가지는 기능을 제공
    """
    
    def __init__(self, parent, settings_controller, on_setting_change: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.settings_controller = settings_controller
        self.on_setting_change = on_setting_change
        
        # 위젯 저장
        self.widgets: Dict[str, Any] = {}
        
        # 섹션별 프레임 저장
        self.sections: Dict[str, ctk.CTkFrame] = {}
        
        # 변경 추적을 위한 원본 값
        self.original_values: Dict[str, Any] = {}
        
        # UI 생성
        self._create_ui()
    
    @abstractmethod
    def _create_ui(self):
        """UI 생성 - 서브클래스에서 구현"""
        pass
    
    @abstractmethod
    def load_settings(self, settings):
        """설정 로드 - 서브클래스에서 구현"""
        pass
    
    @abstractmethod
    def get_settings(self) -> Dict[str, Any]:
        """현재 설정 값 반환 - 서브클래스에서 구현"""
        pass
    
    def create_section(self, title: str, icon: str = "") -> ctk.CTkFrame:
        """섹션 생성"""
        # 섹션 컨테이너
        section_frame = ctk.CTkFrame(self, corner_radius=10)
        section_frame.pack(fill='x', pady=(0, 15))
        
        # 섹션 헤더
        header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        # 섹션 제목
        title_text = f"{icon} {title}" if icon else title
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(side='left')
        
        # 콘텐츠 영역
        content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # 섹션 저장
        section_id = title.lower().replace(" ", "_")
        self.sections[section_id] = content_frame
        
        return content_frame
    
    def create_option_row(self, parent: ctk.CTkFrame, label: str, 
                         widget_type: str, widget_id: str, **widget_kwargs) -> Any:
        """옵션 행 생성"""
        # 행 컨테이너
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill='x', pady=5)
        
        # 레이블
        label_widget = ctk.CTkLabel(
            row_frame,
            text=label,
            width=200,
            anchor='w'
        )
        label_widget.pack(side='left', padx=(0, 20))
        
        # 위젯 생성
        widget = None
        if widget_type == "switch":
            widget = self._create_switch(row_frame, widget_id, **widget_kwargs)
        elif widget_type == "combobox":
            widget = self._create_combobox(row_frame, widget_id, **widget_kwargs)
        elif widget_type == "entry":
            widget = self._create_entry(row_frame, widget_id, **widget_kwargs)
        elif widget_type == "slider":
            widget = self._create_slider(row_frame, widget_id, **widget_kwargs)
        elif widget_type == "button":
            widget = self._create_button(row_frame, widget_id, **widget_kwargs)
        
        if widget:
            widget.pack(side='left')
            self.widgets[widget_id] = widget
        
        return widget
    
    def _create_switch(self, parent: ctk.CTkFrame, widget_id: str, **kwargs) -> ctk.CTkSwitch:
        """스위치 생성"""
        switch = ctk.CTkSwitch(
            parent,
            text="",
            width=50,
            command=lambda: self._on_widget_change(widget_id, self.widgets[widget_id].get()),
            **kwargs
        )
        return switch
    
    def _create_combobox(self, parent: ctk.CTkFrame, widget_id: str, 
                        values: List[str], **kwargs) -> ctk.CTkComboBox:
        """콤보박스 생성"""
        combobox = ctk.CTkComboBox(
            parent,
            values=values,
            width=200,
            command=lambda value: self._on_widget_change(widget_id, value),
            **kwargs
        )
        return combobox
    
    def _create_entry(self, parent: ctk.CTkFrame, widget_id: str, **kwargs) -> ctk.CTkEntry:
        """입력 필드 생성"""
        entry = ctk.CTkEntry(
            parent,
            width=200,
            height=32,
            **kwargs
        )
        # 엔터 키나 포커스 벗어날 때 변경 감지
        entry.bind('<Return>', lambda e: self._on_widget_change(widget_id, entry.get()))
        entry.bind('<FocusOut>', lambda e: self._on_widget_change(widget_id, entry.get()))
        return entry
    
    def _create_slider(self, parent: ctk.CTkFrame, widget_id: str, 
                      from_: float, to: float, **kwargs) -> ctk.CTkSlider:
        """슬라이더 생성"""
        # 슬라이더와 값 표시를 위한 프레임
        slider_frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        slider = ctk.CTkSlider(
            slider_frame,
            from_=from_,
            to=to,
            width=150,
            command=lambda value: self._on_slider_change(widget_id, value),
            **kwargs
        )
        slider.pack(side='left')
        
        # 값 표시 레이블
        value_label = ctk.CTkLabel(
            slider_frame,
            text=str(int(slider.get())),
            width=40
        )
        value_label.pack(side='left', padx=(10, 0))
        
        # 슬라이더 변경 시 레이블 업데이트
        def update_label(value):
            value_label.configure(text=str(int(value)))
            self._on_widget_change(widget_id, int(value))
        
        slider.configure(command=update_label)
        
        # 프레임 반환 (슬라이더가 포함된)
        return slider_frame
    
    def _create_button(self, parent: ctk.CTkFrame, widget_id: str, 
                      text: str, command: Callable = None, **kwargs) -> ctk.CTkButton:
        """버튼 생성"""
        button = ctk.CTkButton(
            parent,
            text=text,
            width=100,
            height=32,
            command=command,
            **kwargs
        )
        return button
    
    def _on_widget_change(self, widget_id: str, value: Any):
        """위젯 값 변경 이벤트"""
        # 원본 값과 비교
        if widget_id not in self.original_values:
            self.original_values[widget_id] = value
        
        # 변경 콜백 호출
        if self.on_setting_change:
            self.on_setting_change(widget_id, value)
    
    def _on_slider_change(self, widget_id: str, value: float):
        """슬라이더 변경 이벤트"""
        self._on_widget_change(widget_id, int(value))
    
    def search_settings(self, query: str):
        """설정 검색"""
        query_lower = query.lower()
        
        # 모든 섹션을 순회하며 매칭되는 설정 표시/숨김
        for section_name, section_frame in self.sections.items():
            has_match = False
            
            # 섹션 내 위젯들 확인
            for widget_id, widget in self.widgets.items():
                # 위젯 ID나 관련 텍스트에서 검색
                if query_lower in widget_id.lower():
                    has_match = True
                    # 위젯 하이라이트 (선택사항)
                    self._highlight_widget(widget)
            
            # 섹션 표시/숨김
            if has_match or not query:
                section_frame.master.pack(fill='x', pady=(0, 15))
            else:
                section_frame.master.pack_forget()
    
    def show_all_settings(self):
        """모든 설정 표시"""
        for section_frame in self.sections.values():
            section_frame.master.pack(fill='x', pady=(0, 15))
    
    def _highlight_widget(self, widget):
        """위젯 하이라이트"""
        # 임시 하이라이트 효과 (구현 선택사항)
        pass