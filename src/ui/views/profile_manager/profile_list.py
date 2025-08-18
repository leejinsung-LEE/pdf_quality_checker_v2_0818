# src/ui/views/profile_manager/profile_list.py
"""
프로파일 관리 뷰 - 프로파일 목록 위젯
좌측 패널의 프로파일 목록과 관련 버튼들을 관리

AI 친화적 문서화:
- 프로파일 목록 표시 및 선택 기능
- CRUD 버튼 UI 제공
- 트리 구조로 내장/사용자 프로파일 구분
- 이벤트 콜백을 통한 느슨한 결합
"""

import tkinter as tk
from tkinter import ttk, filedialog
import customtkinter as ctk
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from ...controllers import ProfileController, ProfileInfo


class ProfileListWidget:
    """
    프로파일 목록 위젯 클래스
    
    역할:
    - 프로파일 목록을 트리뷰로 표시
    - 내장/사용자 프로파일 구분 표시
    - CRUD 버튼 UI 제공
    - 선택/더블클릭 이벤트 처리
    
    아키텍처:
    - 위젯 헬퍼 패턴
    - 콜백을 통한 이벤트 위임
    - 단일 책임 원칙 적용
    """
    
    def __init__(
        self,
        parent: ctk.CTkFrame,
        profile_controller: ProfileController,
        on_profile_select: Callable[[str], None],
        on_profile_double_click: Callable[[str], None]
    ):
        """
        프로파일 목록 위젯 초기화
        
        Args:
            parent: 부모 프레임
            profile_controller: 프로파일 컨트롤러
            on_profile_select: 프로파일 선택 시 콜백
            on_profile_double_click: 더블클릭 시 콜백
        """
        self.parent = parent
        self.profile_controller = profile_controller
        self.on_profile_select = on_profile_select
        self.on_profile_double_click = on_profile_double_click
        
        # UI 컴포넌트
        self.profile_tree: Optional[ttk.Treeview] = None
        
        # 생성
        self._create_ui()
    
    def _create_ui(self):
        """UI 생성"""
        # 헤더 프레임
        self._create_header()
        
        # 목록 프레임
        self._create_list()
        
        # 버튼 프레임
        self._create_buttons()
    
    def _create_header(self):
        """헤더 프레임 생성"""
        header_frame = ctk.CTkFrame(self.parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        list_label = ctk.CTkLabel(
            header_frame,
            text="프로파일 목록",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_label.pack(side='left')
        
        # 새로고침 버튼
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄",
            width=30,
            command=self.load_profiles
        )
        refresh_btn.pack(side='right')
    
    def _create_list(self):
        """프로파일 목록 생성"""
        list_frame = ctk.CTkFrame(self.parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 트리뷰
        self.profile_tree = ttk.Treeview(
            list_frame,
            columns=('type', 'status'),
            show='tree headings',
            yscrollcommand=scrollbar.set
        )
        self.profile_tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.profile_tree.yview)
        
        # 컬럼 설정
        self.profile_tree.heading('#0', text='이름')
        self.profile_tree.heading('type', text='종류')
        self.profile_tree.heading('status', text='상태')
        
        self.profile_tree.column('#0', width=150)
        self.profile_tree.column('type', width=80)
        self.profile_tree.column('status', width=80)
        
        # 스타일 설정
        self._setup_tree_style()
        
        # 이벤트 바인딩
        self.profile_tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        self.profile_tree.bind('<Double-Button-1>', self._on_tree_double_click)
    
    def _setup_tree_style(self):
        """트리뷰 스타일 설정"""
        style = ttk.Style()
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#667eea')])
    
    def _create_buttons(self):
        """버튼 프레임 생성"""
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # 상단 버튼들
        self._create_top_buttons(button_frame)
        
        # 하단 버튼들
        self._create_bottom_buttons(button_frame)
    
    def _create_top_buttons(self, parent: ctk.CTkFrame):
        """상단 버튼들 생성"""
        buttons_top = ctk.CTkFrame(parent)
        buttons_top.pack(fill='x', pady=(0, 5))
        
        # 새 프로파일 버튼
        add_btn = ctk.CTkButton(
            buttons_top,
            text="새 프로파일",
            command=self._on_create_profile,
            width=100
        )
        add_btn.pack(side='left', padx=(0, 5))
        
        # 복제 버튼
        duplicate_btn = ctk.CTkButton(
            buttons_top,
            text="복제",
            command=self._on_duplicate_profile,
            width=100
        )
        duplicate_btn.pack(side='left', padx=(0, 5))
        
        # 삭제 버튼
        delete_btn = ctk.CTkButton(
            buttons_top,
            text="삭제",
            command=self._on_delete_profile,
            width=100,
            fg_color="red"
        )
        delete_btn.pack(side='left')
    
    def _create_bottom_buttons(self, parent: ctk.CTkFrame):
        """하단 버튼들 생성"""
        buttons_bottom = ctk.CTkFrame(parent)
        buttons_bottom.pack(fill='x')
        
        # 가져오기 버튼
        import_btn = ctk.CTkButton(
            buttons_bottom,
            text="가져오기",
            command=self._on_import_profile,
            width=100
        )
        import_btn.pack(side='left', padx=(0, 5))
        
        # 내보내기 버튼
        export_btn = ctk.CTkButton(
            buttons_bottom,
            text="내보내기",
            command=self._on_export_profile,
            width=100
        )
        export_btn.pack(side='left', padx=(0, 5))
        
        # 기본 설정 버튼
        set_current_btn = ctk.CTkButton(
            buttons_bottom,
            text="기본 설정",
            command=self._on_set_current,
            width=100,
            fg_color="green"
        )
        set_current_btn.pack(side='left')
    
    def load_profiles(self):
        """프로파일 목록 로드"""
        if not self.profile_tree:
            return
        
        # 트리 초기화
        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)
        
        # 프로파일 목록 가져오기
        profiles = self.profile_controller.get_profile_list()
        
        # 내장 프로파일과 사용자 프로파일 분리
        builtin_profiles = [p for p in profiles if p.is_builtin]
        user_profiles = [p for p in profiles if not p.is_builtin]
        
        # 내장 프로파일 추가
        self._add_builtin_profiles(builtin_profiles)
        
        # 사용자 프로파일 추가
        self._add_user_profiles(user_profiles)
    
    def _add_builtin_profiles(self, profiles: List[ProfileInfo]):
        """내장 프로파일 추가"""
        if not profiles or not self.profile_tree:
            return
        
        builtin_parent = self.profile_tree.insert(
            '', 'end', text='내장 프로파일', open=True
        )
        
        for profile in profiles:
            status = '✓ 현재' if profile.is_current else ''
            self.profile_tree.insert(
                builtin_parent, 'end',
                text=profile.name,
                values=('내장', status),
                tags=('builtin',)
            )
    
    def _add_user_profiles(self, profiles: List[ProfileInfo]):
        """사용자 프로파일 추가"""
        if not profiles or not self.profile_tree:
            return
        
        user_parent = self.profile_tree.insert(
            '', 'end', text='사용자 프로파일', open=True
        )
        
        for profile in profiles:
            status = '✓ 현재' if profile.is_current else ''
            self.profile_tree.insert(
                user_parent, 'end',
                text=profile.name,
                values=('사용자', status),
                tags=('user',)
            )
    
    def _on_tree_select(self, event):
        """트리 선택 이벤트"""
        if not self.profile_tree:
            return
        
        selection = self.profile_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        parent = self.profile_tree.parent(item)
        
        # 카테고리 항목이면 무시
        if not parent:
            return
        
        # 프로파일 이름 가져오기
        profile_name = self.profile_tree.item(item)['text']
        self.on_profile_select(profile_name)
    
    def _on_tree_double_click(self, event):
        """트리 더블클릭 이벤트"""
        if not self.profile_tree:
            return
        
        selection = self.profile_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        parent = self.profile_tree.parent(item)
        
        # 카테고리 항목이면 무시
        if not parent:
            return
        
        # 프로파일 이름 가져오기
        profile_name = self.profile_tree.item(item)['text']
        self.on_profile_double_click(profile_name)
    
    def get_selected_profile(self) -> Optional[str]:
        """선택된 프로파일 이름 반환"""
        if not self.profile_tree:
            return None
        
        selection = self.profile_tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        parent = self.profile_tree.parent(item)
        
        # 카테고리 항목이면 None 반환
        if not parent:
            return None
        
        return self.profile_tree.item(item)['text']
    
    # 버튼 이벤트 핸들러들 - 콜백으로 처리
    def set_event_handlers(self, handlers: Dict[str, callable]):
        """
        이벤트 핸들러 설정
        
        Args:
            handlers: 이벤트 핸들러 딕셔너리
        """
        self.create_handler = handlers.get('create')
        self.duplicate_handler = handlers.get('duplicate')
        self.delete_handler = handlers.get('delete')
        self.import_handler = handlers.get('import')
        self.export_handler = handlers.get('export')
        self.set_current_handler = handlers.get('set_current')
    
    def _on_create_profile(self):
        """새 프로파일 생성 버튼"""
        if hasattr(self, 'create_handler') and self.create_handler:
            self.create_handler()
    
    def _on_duplicate_profile(self):
        """복제 버튼"""
        if hasattr(self, 'duplicate_handler') and self.duplicate_handler:
            self.duplicate_handler()
    
    def _on_delete_profile(self):
        """삭제 버튼"""
        if hasattr(self, 'delete_handler') and self.delete_handler:
            self.delete_handler()
    
    def _on_import_profile(self):
        """가져오기 버튼"""
        if hasattr(self, 'import_handler') and self.import_handler:
            self.import_handler()
    
    def _on_export_profile(self):
        """내보내기 버튼"""
        if hasattr(self, 'export_handler') and self.export_handler:
            self.export_handler()
    
    def _on_set_current(self):
        """기본 설정 버튼"""
        if hasattr(self, 'set_current_handler') and self.set_current_handler:
            self.set_current_handler()