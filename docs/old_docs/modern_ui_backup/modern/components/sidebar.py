# src/ui/modern/components/sidebar.py
"""
Modern 사이드바 컴포넌트

Classic UI의 사이드바와 동일한 기능을 제공하는 Modern 버전
"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import ModernApp


class ModernSidebar(ft.Container):
    """Modern 사이드바"""
    
    def __init__(self, app: 'ModernApp'):
        self.app = app
        self.selected_index = 0
        
        # 네비게이션 아이템 정의 (Classic과 동일한 구성)
        self.nav_items = [
            {"icon": "dashboard", "label": "대시보드", "view": "dashboard"},
            {"icon": "folder_open", "label": "파일 처리", "view": "processing"},
            {"icon": "history", "label": "히스토리", "view": "history"},
            {"icon": "folder_special", "label": "폴더 관리", "view": "folders"},
            {"icon": "settings", "label": "설정", "view": "settings"},
        ]
        
        super().__init__(
            width=250,
            bgcolor="#2B2930",
            padding=ft.padding.all(20),
            content=self._build_content()
        )
    
    def _build_content(self):
        """사이드바 컨텐츠 생성"""
        # 로고/타이틀
        logo_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(name="picture_as_pdf", color="#F44336", size=32),
                    ft.Text(
                        "PDF Quality Checker",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF"
                    ),
                ]),
                ft.Text(
                    "v2.0 Modern UI",
                    size=12,
                    color="#888888"
                ),
            ]),
            padding=ft.padding.only(bottom=20),
        )
        
        # 프로파일 선택 (Classic과 동일)
        profile_section = self._create_profile_section()
        
        # 네비게이션 메뉴
        nav_menu = ft.Column(
            controls=[self._create_nav_item(i, item) for i, item in enumerate(self.nav_items)],
            spacing=5,
        )
        
        # 빠른 액션 버튼
        quick_actions = self._create_quick_actions()
        
        return ft.Column([
            logo_section,
            ft.Divider(height=1, color="#444444"),
            profile_section,
            ft.Divider(height=1, color="#444444"),
            nav_menu,
            ft.Container(expand=True),  # 공간 채우기
            ft.Divider(height=1, color="#444444"),
            quick_actions,
        ], spacing=10)
    
    def _create_profile_section(self):
        """프로파일 선택 섹션"""
        # ProfileController의 실제 메서드 사용
        if self.app.profile_controller:
            profile_list = self.app.profile_controller.get_profile_list()
            profiles = [p.name for p in profile_list]
            # 현재 프로파일 가져오기
            current_name, _ = self.app.profile_controller.get_current_profile()
        else:
            profiles = ["Default"]
            current_name = "Default"
        
        return ft.Container(
            content=ft.Column([
                ft.Text("프로파일", size=12, color="#888888"),
                ft.Dropdown(
                    value=current_name,
                    options=[ft.dropdown.Option(p) for p in profiles],
                    width=200,
                    on_change=self._on_profile_change,
                ),
            ]),
            padding=ft.padding.symmetric(vertical=10),
        )
    
    def _create_nav_item(self, index: int, item: dict):
        """네비게이션 아이템 생성"""
        is_selected = index == self.selected_index
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    name=item["icon"],
                    color="#FFFFFF" if is_selected else "#888888",
                    size=20,
                ),
                ft.Text(
                    item["label"],
                    color="#FFFFFF" if is_selected else "#888888",
                    size=14,
                    weight=ft.FontWeight.W_500 if is_selected else None,
                ),
            ]),
            padding=ft.padding.all(12),
            border_radius=10,
            bgcolor="#6750A4" if is_selected else None,
            on_click=lambda e, idx=index, view=item["view"]: self._on_nav_click(idx, view),
            ink=True,
        )
    
    def _create_quick_actions(self):
        """빠른 액션 버튼"""
        return ft.Column([
            ft.Text("빠른 액션", size=12, color="#888888"),
            ft.Row([
                ft.IconButton(
                    icon="add_circle",
                    icon_color="#6750A4",
                    tooltip="파일 추가",
                    on_click=self._on_add_file,
                ),
                ft.IconButton(
                    icon="play_arrow",
                    icon_color="#4CAF50",
                    tooltip="배치 처리",
                    on_click=self._on_batch_process,
                ),
                ft.IconButton(
                    icon="refresh",
                    icon_color="#FF9800",
                    tooltip="새로고침",
                    on_click=self._on_refresh,
                ),
            ]),
        ])
    
    def _on_nav_click(self, index: int, view: str):
        """네비게이션 클릭 이벤트"""
        self.selected_index = index
        self.app.switch_view(view)
        self.update_selection()
    
    def update_selection(self):
        """선택 상태 업데이트"""
        # 모든 네비게이션 아이템 재생성
        nav_menu = ft.Column(
            controls=[self._create_nav_item(i, item) for i, item in enumerate(self.nav_items)],
            spacing=5,
        )
        
        # 컨텐츠 업데이트
        if self.content and hasattr(self.content, 'controls'):
            # nav_menu가 있는 인덱스 찾기 (보통 4번째)
            for i, control in enumerate(self.content.controls):
                if isinstance(control, ft.Column) and len(control.controls) > 2:
                    self.content.controls[i] = nav_menu
                    break
        
        self.update()
    
    def _on_profile_change(self, e):
        """프로파일 변경 이벤트"""
        if self.app.profile_controller:
            self.app.profile_controller.set_current_profile(e.control.value)
            self.app.show_message("프로파일 변경", f"프로파일이 '{e.control.value}'로 변경되었습니다.", "info")
    
    def _on_add_file(self, e):
        """파일 추가"""
        self.app.switch_view("processing")
        # 파일 선택 다이얼로그는 ProcessingView에서 처리
    
    def _on_batch_process(self, e):
        """배치 처리"""
        self.app.show_message("배치 처리", "배치 처리 기능은 준비 중입니다.", "info")
    
    def _on_refresh(self, e):
        """새로고침"""
        # 현재 뷰 새로고침
        current_view = self.app.current_view
        self.app.views.pop(current_view, None)
        self.app.switch_view(current_view)
        self.app.show_message("새로고침", "화면이 새로고침되었습니다.", "success")