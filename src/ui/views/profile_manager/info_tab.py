# src/ui/views/profile_manager/info_tab.py
"""
프로파일 관리 뷰 - 기본 정보 탭
프로파일의 기본 정보(이름, 설명, 생성일 등)를 표시하고 편집

AI 친화적 문서화:
- 프로파일 메타데이터 관리
- 읽기 전용/편집 가능 상태 전환
- 타입 힌트를 통한 명확한 인터페이스
- 단일 책임 원칙 적용
"""

import customtkinter as ctk
from typing import Dict, Optional, Any
from ...controllers import ProfileInfo


class InfoTabHelper:
    """
    기본 정보 탭 헬퍼 클래스
    
    역할:
    - 프로파일 기본 정보 UI 구성
    - 메타데이터 표시 (이름, 설명, 생성일 등)
    - 편집 가능 여부 제어
    - 데이터 로드 및 저장 지원
    
    아키텍처:
    - 헬퍼 패턴 적용
    - 위젯 딕셔너리를 통한 상태 공유
    - 단일 탭의 책임만 담당
    """
    
    def __init__(self, parent: ctk.CTkFrame, widgets: Dict[str, Any]):
        """
        기본 정보 탭 헬퍼 초기화
        
        Args:
            parent: 탭 프레임
            widgets: 위젯 참조 딕셔너리
        """
        self.parent = parent
        self.widgets = widgets
        
        # UI 생성
        self._create_ui()
    
    def _create_ui(self):
        """UI 생성"""
        frame = ctk.CTkScrollableFrame(self.parent)
        frame.pack(fill='both', expand=True)
        
        # 프로파일 이름
        self._create_name_field(frame, 0)
        
        # 설명
        self._create_description_field(frame, 1)
        
        # 기반 프로파일
        self._create_parent_field(frame, 2)
        
        # 생성일시
        self._create_created_field(frame, 3)
        
        # 수정일시
        self._create_modified_field(frame, 4)
        
        # 프로파일 종류
        self._create_type_field(frame, 5)
    
    def _create_name_field(self, parent: ctk.CTkScrollableFrame, row: int):
        """프로파일 이름 필드 생성"""
        name_label = ctk.CTkLabel(parent, text="프로파일 이름:")
        name_label.grid(row=row, column=0, sticky='w', padx=10, pady=5)
        
        self.widgets['name'] = ctk.CTkEntry(parent, width=300, state='readonly')
        self.widgets['name'].grid(row=row, column=1, padx=10, pady=5)
    
    def _create_description_field(self, parent: ctk.CTkScrollableFrame, row: int):
        """설명 필드 생성"""
        desc_label = ctk.CTkLabel(parent, text="설명:")
        desc_label.grid(row=row, column=0, sticky='nw', padx=10, pady=5)
        
        self.widgets['description'] = ctk.CTkTextbox(parent, width=300, height=100)
        self.widgets['description'].grid(row=row, column=1, padx=10, pady=5)
    
    def _create_parent_field(self, parent: ctk.CTkScrollableFrame, row: int):
        """기반 프로파일 필드 생성"""
        parent_label = ctk.CTkLabel(parent, text="기반 프로파일:")
        parent_label.grid(row=row, column=0, sticky='w', padx=10, pady=5)
        
        self.widgets['parent'] = ctk.CTkEntry(parent, width=300, state='readonly')
        self.widgets['parent'].grid(row=row, column=1, padx=10, pady=5)
    
    def _create_created_field(self, parent: ctk.CTkScrollableFrame, row: int):
        """생성일시 필드 생성"""
        created_label = ctk.CTkLabel(parent, text="생성일시:")
        created_label.grid(row=row, column=0, sticky='w', padx=10, pady=5)
        
        self.widgets['created'] = ctk.CTkEntry(parent, width=300, state='readonly')
        self.widgets['created'].grid(row=row, column=1, padx=10, pady=5)
    
    def _create_modified_field(self, parent: ctk.CTkScrollableFrame, row: int):
        """수정일시 필드 생성"""
        modified_label = ctk.CTkLabel(parent, text="수정일시:")
        modified_label.grid(row=row, column=0, sticky='w', padx=10, pady=5)
        
        self.widgets['modified'] = ctk.CTkEntry(parent, width=300, state='readonly')
        self.widgets['modified'].grid(row=row, column=1, padx=10, pady=5)
    
    def _create_type_field(self, parent: ctk.CTkScrollableFrame, row: int):
        """프로파일 종류 필드 생성"""
        type_label = ctk.CTkLabel(parent, text="종류:")
        type_label.grid(row=row, column=0, sticky='w', padx=10, pady=5)
        
        self.widgets['type'] = ctk.CTkEntry(parent, width=300, state='readonly')
        self.widgets['type'].grid(row=row, column=1, padx=10, pady=5)
    
    def load_profile_data(self, profile_info: ProfileInfo):
        """
        프로파일 데이터 로드
        
        Args:
            profile_info: 프로파일 정보 객체
        """
        # 프로파일 이름
        self._set_readonly_field('name', profile_info.name)
        
        # 설명
        self.widgets['description'].delete('1.0', 'end')
        self.widgets['description'].insert('1.0', profile_info.description or '')
        
        # 기반 프로파일
        self._set_readonly_field('parent', profile_info.parent_profile or '-')
        
        # 생성일시
        self._set_readonly_field('created', profile_info.created_at or '-')
        
        # 수정일시
        self._set_readonly_field('modified', profile_info.modified_at or '-')
        
        # 프로파일 종류
        profile_type = '내장' if profile_info.is_builtin else '사용자'
        self._set_readonly_field('type', profile_type)
    
    def _set_readonly_field(self, field_name: str, value: str):
        """읽기 전용 필드 값 설정"""
        if field_name not in self.widgets:
            return
        
        widget = self.widgets[field_name]
        if isinstance(widget, ctk.CTkEntry):
            widget.configure(state='normal')
            widget.delete(0, 'end')
            widget.insert(0, value)
            widget.configure(state='readonly')
    
    def set_editing_enabled(self, enabled: bool):
        """
        편집 가능 여부 설정
        
        Args:
            enabled: 편집 가능 여부
        """
        # 설명 필드만 편집 가능 (나머지는 메타데이터)
        description_widget = self.widgets.get('description')
        if description_widget:
            if enabled:
                description_widget.configure(state='normal')
            else:
                description_widget.configure(state='disabled')
    
    def get_description(self) -> str:
        """설명 텍스트 반환"""
        description_widget = self.widgets.get('description')
        if description_widget:
            return description_widget.get('1.0', 'end-1c')
        return ''
    
    def clear_fields(self):
        """모든 필드 초기화"""
        # 읽기 전용 필드들 초기화
        readonly_fields = ['name', 'parent', 'created', 'modified', 'type']
        for field in readonly_fields:
            if field in self.widgets:
                widget = self.widgets[field]
                if isinstance(widget, ctk.CTkEntry):
                    widget.configure(state='normal')
                    widget.delete(0, 'end')
                    widget.configure(state='readonly')
        
        # 설명 필드 초기화
        if 'description' in self.widgets:
            self.widgets['description'].delete('1.0', 'end')
    
    def validate_data(self) -> tuple[bool, str]:
        """
        데이터 검증
        
        Returns:
            tuple: (유효성, 오류 메시지)
        """
        # 기본 정보 탭에서는 특별한 검증 없음
        # 필요시 여기에 검증 로직 추가
        return True, ""
    
    def get_field_value(self, field_name: str) -> Optional[str]:
        """
        특정 필드 값 반환
        
        Args:
            field_name: 필드 이름
            
        Returns:
            필드 값 또는 None
        """
        if field_name not in self.widgets:
            return None
        
        widget = self.widgets[field_name]
        
        if isinstance(widget, ctk.CTkEntry):
            return widget.get()
        elif isinstance(widget, ctk.CTkTextbox):
            return widget.get('1.0', 'end-1c')
        
        return None