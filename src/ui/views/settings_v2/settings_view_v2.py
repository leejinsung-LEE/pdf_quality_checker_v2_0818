# src/ui/views/settings_v2/settings_view_v2.py
"""
환경설정 뷰 V2 - 메인 클래스

사이드바 네비게이션과 즉시 적용 모드를 지원하는 모던한 환경설정 뷰
"""

import customtkinter as ctk
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from pathlib import Path

from ...controllers import get_settings_controller
from ...events import EventBus, EventType, Event, get_event_bus
from .navigation import NavigationSidebar
from .categories import (
    GeneralCategory,
    ProcessingCategory, 
    NotificationCategory,
    AdvancedCategory
)
from .search_bar import SettingsSearchBar


@dataclass
class CategoryInfo:
    """카테고리 정보"""
    id: str
    name: str
    icon: str
    widget_class: type
    keywords: List[str]  # 검색용 키워드


class SettingsViewV2(ctk.CTkToplevel):
    """
    환경설정 뷰 V2
    
    주요 특징:
    - 사이드바 네비게이션
    - 4개 카테고리로 통합된 설정
    - 즉시 적용 모드 (실시간 반영)
    - 설정 검색 기능
    - 변경사항 하이라이트
    """
    
    # 카테고리 정의
    CATEGORIES = [
        CategoryInfo(
            id="general",
            name="일반 설정",
            icon="🔧",
            widget_class=GeneralCategory,
            keywords=["테마", "시작", "UI", "인터페이스", "사이드바"]
        ),
        CategoryInfo(
            id="processing",
            name="처리 설정",
            icon="⚙️",
            widget_class=ProcessingCategory,
            keywords=["프로파일", "자동", "보고서", "폴더", "경로"]
        ),
        CategoryInfo(
            id="notification",
            name="알림 설정",
            icon="🔔",
            widget_class=NotificationCategory,
            keywords=["알림", "소리", "조용한", "히스토리"]
        ),
        CategoryInfo(
            id="advanced",
            name="고급 설정",
            icon="🛠️",
            widget_class=AdvancedCategory,
            keywords=["성능", "로그", "도구", "타임아웃", "동시"]
        )
    ]
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 컨트롤러 및 이벤트 버스
        self.settings_controller = get_settings_controller()
        self.settings = self.settings_controller.get_settings()
        self.event_bus = get_event_bus()
        
        # 카테고리 위젯 저장 (먼저 초기화)
        self.category_widgets: Dict[str, ctk.CTkFrame] = {}
        self.current_category = "general"
        
        # 변경사항 추적
        self.original_settings = {}  # 나중에 설정됨
        self.modified_fields = set()
        
        # 콜백
        self.on_close: Optional[Callable] = None
        
        # 윈도우 설정
        self._setup_window()
        
        # UI 생성
        self._create_ui()
        
        # 초기 설정 로드
        self._load_settings()
        
        # UI 생성 후 원본 설정 저장
        self.original_settings = self._get_current_settings()
        
        # 이벤트 구독
        self._subscribe_events()
        
        # 포커스 설정
        self.focus()
    
    def _setup_window(self):
        """윈도우 설정"""
        self.title("환경설정")
        self.geometry("900x600")
        self.resizable(False, False)
        
        # 모달 윈도우로 설정
        self.transient(self.master)
        self.grab_set()
        
        # ESC 키로 닫기
        self.bind('<Escape>', lambda e: self.close())
        
        # 닫기 버튼 처리
        self.protocol("WM_DELETE_WINDOW", self.close)
    
    def _create_ui(self):
        """UI 생성"""
        # 메인 컨테이너
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill='both', expand=True)
        
        # 헤더 영역
        self._create_header(main_container)
        
        # 구분선
        separator = ctk.CTkFrame(main_container, height=1, fg_color=("gray70", "gray30"))
        separator.pack(fill='x', pady=(0, 10))
        
        # 콘텐츠 영역 (사이드바 + 설정 패널)
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill='both', expand=True, padx=20)
        
        # 사이드바 네비게이션
        self.navigation = NavigationSidebar(
            content_frame,
            categories=self.CATEGORIES,
            on_category_select=self._on_category_select
        )
        self.navigation.pack(side='left', fill='y', padx=(0, 20))
        
        # 설정 패널 컨테이너
        self.panel_container = ctk.CTkFrame(content_frame)
        self.panel_container.pack(side='left', fill='both', expand=True)
        
        # 카테고리별 패널 생성
        self._create_category_panels()
        
        # 하단 영역
        self._create_footer(main_container)
    
    def _create_header(self, parent):
        """헤더 영역 생성"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # 제목
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ 환경설정",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side='left')
        
        # 검색 바
        self.search_bar = SettingsSearchBar(
            header_frame,
            on_search=self._on_search,
            placeholder="설정 검색..."
        )
        self.search_bar.pack(side='right', padx=(20, 0))
    
    def _create_category_panels(self):
        """카테고리별 패널 생성"""
        for category in self.CATEGORIES:
            # 패널 생성
            panel = category.widget_class(
                self.panel_container,
                settings_controller=self.settings_controller,
                on_setting_change=self._on_setting_change
            )
            
            # 저장
            self.category_widgets[category.id] = panel
            
            # 기본적으로 숨김
            if category.id != self.current_category:
                panel.pack_forget()
            else:
                panel.pack(fill='both', expand=True)
    
    def _create_footer(self, parent):
        """하단 영역 생성"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        # 구분선
        separator = ctk.CTkFrame(footer_frame, height=1, fg_color=("gray70", "gray30"))
        separator.pack(fill='x', pady=(0, 10))
        
        # 버튼 영역
        button_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        button_frame.pack(fill='x')
        
        # 변경사항 표시
        self.changes_label = ctk.CTkLabel(
            button_frame,
            text="",
            text_color=("orange", "yellow")
        )
        self.changes_label.pack(side='left')
        
        # 닫기 버튼
        close_btn = ctk.CTkButton(
            button_frame,
            text="닫기",
            width=100,
            command=self.close
        )
        close_btn.pack(side='right')
        
        # 기본값 복원 버튼
        reset_btn = ctk.CTkButton(
            button_frame,
            text="기본값 복원",
            width=100,
            fg_color="gray",
            command=self._reset_to_defaults
        )
        reset_btn.pack(side='right', padx=(0, 10))
    
    def _on_category_select(self, category_id: str):
        """카테고리 선택 이벤트"""
        if category_id == self.current_category:
            return
        
        # 현재 패널 숨기기
        if self.current_category in self.category_widgets:
            self.category_widgets[self.current_category].pack_forget()
        
        # 새 패널 표시
        if category_id in self.category_widgets:
            self.category_widgets[category_id].pack(fill='both', expand=True)
        
        self.current_category = category_id
        
        # 이벤트 발행
        self.event_bus.emit(
            EventType.SETTINGS_CATEGORY_CHANGED,
            data={"category": category_id},
            source="settings_v2"
        )
    
    def _on_setting_change(self, setting_key: str, value: Any):
        """설정 변경 이벤트 (즉시 적용)"""
        # 변경사항 추적
        original_value = self.original_settings.get(setting_key)
        if value != original_value:
            self.modified_fields.add(setting_key)
        else:
            self.modified_fields.discard(setting_key)
        
        # 변경사항 표시 업데이트
        self._update_changes_label()
        
        # 즉시 적용
        self.settings_controller.set_setting(setting_key, value)
        
        # 이벤트 발행
        self.event_bus.emit(
            EventType.SETTING_CHANGED,
            data={
                "key": setting_key,
                "value": value,
                "source": "settings_v2"
            }
        )
    
    def _on_search(self, query: str):
        """설정 검색"""
        if not query:
            # 검색어가 없으면 모든 설정 표시
            for widget in self.category_widgets.values():
                widget.show_all_settings()
            return
        
        # 검색어와 매칭되는 설정 찾기
        query_lower = query.lower()
        matching_categories = []
        
        for category in self.CATEGORIES:
            # 카테고리 이름이나 키워드에서 검색
            if (query_lower in category.name.lower() or 
                any(query_lower in keyword.lower() for keyword in category.keywords)):
                matching_categories.append(category.id)
                
                # 해당 카테고리 위젯에서 검색
                if category.id in self.category_widgets:
                    self.category_widgets[category.id].search_settings(query)
        
        # 매칭되는 첫 번째 카테고리로 이동
        if matching_categories and matching_categories[0] != self.current_category:
            self._on_category_select(matching_categories[0])
            self.navigation.select_category(matching_categories[0])
    
    def _update_changes_label(self):
        """변경사항 표시 업데이트"""
        count = len(self.modified_fields)
        if count > 0:
            self.changes_label.configure(
                text=f"✏️ {count}개 항목이 변경되었습니다"
            )
        else:
            self.changes_label.configure(text="")
    
    def _reset_to_defaults(self):
        """기본값으로 초기화"""
        # 확인 다이얼로그
        from tkinter import messagebox
        if not messagebox.askyesno(
            "기본값 복원",
            "모든 설정을 기본값으로 복원하시겠습니까?\n이 작업은 되돌릴 수 없습니다."
        ):
            return
        
        # 기본값 복원
        self.settings_controller.reset_to_defaults()
        
        # UI 업데이트
        self._load_settings()
        
        # 변경사항 초기화
        self.modified_fields.clear()
        self._update_changes_label()
        
        # 이벤트 발행
        self.event_bus.emit(EventType.SETTINGS_RESET, source="settings_v2")
        
        messagebox.showinfo("완료", "설정이 기본값으로 복원되었습니다.")
    
    def _load_settings(self):
        """현재 설정 로드"""
        self.settings = self.settings_controller.get_settings()
        
        # 각 카테고리에 설정 로드
        for widget in self.category_widgets.values():
            widget.load_settings(self.settings)
        
        # 원본 설정 업데이트
        self.original_settings = self._get_current_settings()
    
    def _get_current_settings(self) -> Dict[str, Any]:
        """현재 설정 값 가져오기"""
        settings = {}
        if hasattr(self, 'category_widgets') and self.category_widgets:
            for widget in self.category_widgets.values():
                if hasattr(widget, 'get_settings'):
                    settings.update(widget.get_settings())
        return settings
    
    def _subscribe_events(self):
        """이벤트 구독"""
        # 테마 변경 이벤트
        self.event_bus.subscribe(
            EventType.THEME_CHANGED,
            self._on_theme_changed
        )
    
    def _on_theme_changed(self, event: Event):
        """테마 변경 이벤트 처리"""
        if event.data.get("source") != "settings_v2":
            # 외부에서 변경된 경우 UI 업데이트
            self._load_settings()
    
    def close(self):
        """설정창 닫기"""
        # 변경사항이 있으면 확인
        if self.modified_fields:
            # 즉시 적용 모드이므로 이미 저장됨
            pass
        
        # 콜백 호출
        if self.on_close:
            self.on_close()
        
        # 이벤트 발행
        self.event_bus.emit(EventType.SETTINGS_CLOSED, source="settings_v2")
        
        # 창 닫기
        self.destroy()