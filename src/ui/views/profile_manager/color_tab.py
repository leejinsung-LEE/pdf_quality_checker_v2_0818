# src/ui/views/profile_manager/color_tab.py
"""
프로파일 관리 뷰 - 색상 설정 탭
PDF 색상 검사 옵션들(RGB, 별색, 잉크 커버리지)을 설정

AI 친화적 문서화:
- RGB 색상 검사 설정
- 별색(Spot Color) 관련 설정
- 잉크 커버리지 검사 옵션
- 체크박스 기반 옵션 관리
"""

import customtkinter as ctk
from typing import Dict, Optional, Any, Tuple


class ColorTabHelper:
    """
    색상 설정 탭 헬퍼 클래스
    
    역할:
    - RGB 색상 검사 옵션 UI
    - 별색 허용/제한 설정 UI
    - 잉크 커버리지 검사 옵션 UI
    - 색상 관련 체크옵션 관리
    
    아키텍처:
    - 헬퍼 패턴으로 단일 탭 책임
    - 섹션별 UI 그룹화
    - 체크박스 상태 관리
    """
    
    def __init__(self, parent: ctk.CTkFrame, widgets: Dict[str, Any]):
        """
        색상 설정 탭 헬퍼 초기화
        
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
        
        # RGB 설정 섹션
        self._create_rgb_section(frame)
        
        # 별색 설정 섹션
        self._create_spot_section(frame)
        
        # 잉크 커버리지 섹션
        self._create_ink_coverage_section(frame)
    
    def _create_rgb_section(self, parent: ctk.CTkScrollableFrame):
        """RGB 설정 섹션 생성"""
        # 섹션 헤더
        rgb_label = ctk.CTkLabel(
            parent,
            text="RGB 색상",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        rgb_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        # RGB 색상 검사 체크박스
        self.widgets['check_rgb'] = ctk.CTkCheckBox(
            parent,
            text="RGB 색상 검사"
        )
        self.widgets['check_rgb'].pack(anchor='w', padx=20, pady=5)
        
        # RGB 색상 허용 체크박스
        self.widgets['allow_rgb'] = ctk.CTkCheckBox(
            parent,
            text="RGB 색상 허용"
        )
        self.widgets['allow_rgb'].pack(anchor='w', padx=20, pady=5)
    
    def _create_spot_section(self, parent: ctk.CTkScrollableFrame):
        """별색 설정 섹션 생성"""
        # 섹션 헤더
        spot_label = ctk.CTkLabel(
            parent,
            text="별색 (Spot Color)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        spot_label.pack(anchor='w', padx=10, pady=(20, 5))
        
        # 별색 검사 체크박스
        self.widgets['check_spot'] = ctk.CTkCheckBox(
            parent,
            text="별색 검사"
        )
        self.widgets['check_spot'].pack(anchor='w', padx=20, pady=5)
        
        # 별색 허용 체크박스
        self.widgets['allow_spot'] = ctk.CTkCheckBox(
            parent,
            text="별색 허용"
        )
        self.widgets['allow_spot'].pack(anchor='w', padx=20, pady=5)
        
        # 별색 개수 제한
        self._create_spot_limit_section(parent)
    
    def _create_spot_limit_section(self, parent: ctk.CTkScrollableFrame):
        """별색 개수 제한 섹션 생성"""
        spot_limit_frame = ctk.CTkFrame(parent)
        spot_limit_frame.pack(anchor='w', padx=20, pady=5)
        
        spot_limit_label = ctk.CTkLabel(
            spot_limit_frame,
            text="별색 개수 제한:"
        )
        spot_limit_label.pack(side='left', padx=(0, 10))
        
        self.widgets['spot_limit'] = ctk.CTkEntry(
            spot_limit_frame,
            width=50
        )
        self.widgets['spot_limit'].pack(side='left')
        
        # 도움말 라벨
        help_label = ctk.CTkLabel(
            spot_limit_frame,
            text="개 (0: 제한 없음)",
            text_color="gray"
        )
        help_label.pack(side='left', padx=(5, 0))
    
    def _create_ink_coverage_section(self, parent: ctk.CTkScrollableFrame):
        """잉크 커버리지 섹션 생성"""
        # 섹션 헤더
        ink_label = ctk.CTkLabel(
            parent,
            text="잉크 커버리지",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ink_label.pack(anchor='w', padx=10, pady=(20, 5))
        
        # 잉크 커버리지 검사 체크박스
        self.widgets['check_ink_coverage'] = ctk.CTkCheckBox(
            parent,
            text="잉크 커버리지 검사"
        )
        self.widgets['check_ink_coverage'].pack(anchor='w', padx=20, pady=5)
        
        # 설명 라벨
        ink_info_label = ctk.CTkLabel(
            parent,
            text="※ 세부 기준값은 '품질 기준' 탭에서 설정합니다.",
            text_color="gray"
        )
        ink_info_label.pack(anchor='w', padx=30, pady=(0, 5))
    
    def load_profile_data(self, profile_data: Dict[str, Any]):
        """
        프로파일 데이터 로드
        
        Args:
            profile_data: 프로파일 데이터 딕셔너리
        """
        options = profile_data.get('check_options', {})
        
        # 기본값 설정
        defaults = {
            'check_rgb': True,
            'allow_rgb': False,
            'check_spot': True,
            'allow_spot': True,
            'spot_color_limit': 2,
            'ink_coverage': False
        }
        
        # RGB 설정 로드
        self._set_checkbox('check_rgb', options.get('check_rgb', defaults['check_rgb']))
        self._set_checkbox('allow_rgb', options.get('allow_rgb', defaults['allow_rgb']))
        
        # 별색 설정 로드
        self._set_checkbox('check_spot', options.get('check_spot', defaults['check_spot']))
        self._set_checkbox('allow_spot', options.get('allow_spot', defaults['allow_spot']))
        
        # 별색 개수 제한
        spot_limit = options.get('spot_color_limit', defaults['spot_color_limit'])
        self.widgets['spot_limit'].delete(0, 'end')
        self.widgets['spot_limit'].insert(0, str(spot_limit))
        
        # 잉크 커버리지 설정
        self._set_checkbox('check_ink_coverage', options.get('ink_coverage', defaults['ink_coverage']))
    
    def _set_checkbox(self, field_name: str, value: bool):
        """체크박스 값 설정"""
        if field_name not in self.widgets:
            return
        
        checkbox = self.widgets[field_name]
        if isinstance(checkbox, ctk.CTkCheckBox):
            if value:
                checkbox.select()
            else:
                checkbox.deselect()
    
    def set_editing_enabled(self, enabled: bool):
        """
        편집 가능 여부 설정
        
        Args:
            enabled: 편집 가능 여부
        """
        color_fields = [
            'check_rgb', 'allow_rgb', 'check_spot', 
            'allow_spot', 'spot_limit', 'check_ink_coverage'
        ]
        
        for field in color_fields:
            if field in self.widgets:
                widget = self.widgets[field]
                if enabled:
                    if isinstance(widget, ctk.CTkCheckBox):
                        widget.configure(state='normal')
                    elif isinstance(widget, ctk.CTkEntry):
                        widget.configure(state='normal')
                else:
                    if isinstance(widget, ctk.CTkCheckBox):
                        widget.configure(state='disabled')
                    elif isinstance(widget, ctk.CTkEntry):
                        widget.configure(state='disabled')
    
    def get_color_options(self) -> Dict[str, Any]:
        """
        현재 색상 옵션 데이터 반환
        
        Returns:
            색상 옵션 데이터 딕셔너리
        """
        try:
            spot_limit_value = self.widgets['spot_limit'].get()
            spot_limit = int(spot_limit_value) if spot_limit_value else 2
        except ValueError:
            spot_limit = 2
        
        return {
            'check_rgb': self.widgets['check_rgb'].get(),
            'allow_rgb': self.widgets['allow_rgb'].get(),
            'check_spot': self.widgets['check_spot'].get(),
            'allow_spot': self.widgets['allow_spot'].get(),
            'spot_color_limit': spot_limit,
            'ink_coverage': self.widgets['check_ink_coverage'].get()
        }
    
    def validate_data(self) -> Tuple[bool, str]:
        """
        데이터 검증
        
        Returns:
            tuple: (유효성, 오류 메시지)
        """
        try:
            # 별색 개수 제한 검증
            spot_limit_value = self.widgets['spot_limit'].get()
            if spot_limit_value:
                spot_limit = int(spot_limit_value)
                if spot_limit < 0:
                    return False, "별색 개수 제한은 0 이상이어야 합니다."
                if spot_limit > 10:
                    return False, "별색 개수 제한은 10개 이하를 권장합니다."
            
            # RGB 설정 논리 검증
            check_rgb = self.widgets['check_rgb'].get()
            allow_rgb = self.widgets['allow_rgb'].get()
            
            if not check_rgb and allow_rgb:
                return False, "RGB 색상을 허용하려면 RGB 검사를 활성화해야 합니다."
            
            # 별색 설정 논리 검증
            check_spot = self.widgets['check_spot'].get()
            allow_spot = self.widgets['allow_spot'].get()
            
            if not check_spot and allow_spot:
                return False, "별색을 허용하려면 별색 검사를 활성화해야 합니다."
            
            return True, ""
            
        except ValueError:
            return False, "별색 개수 제한에 올바른 숫자를 입력하세요."
    
    def clear_fields(self):
        """모든 필드 초기화"""
        # 체크박스 초기화
        checkboxes = ['check_rgb', 'allow_rgb', 'check_spot', 'allow_spot', 'check_ink_coverage']
        for checkbox_name in checkboxes:
            if checkbox_name in self.widgets:
                self.widgets[checkbox_name].deselect()
        
        # 별색 제한 초기화
        if 'spot_limit' in self.widgets:
            self.widgets['spot_limit'].delete(0, 'end')
    
    def reset_to_defaults(self):
        """기본값으로 재설정"""
        defaults = {
            'check_rgb': True,
            'allow_rgb': False,
            'check_spot': True,
            'allow_spot': True,
            'spot_color_limit': '2',
            'check_ink_coverage': False
        }
        
        # 체크박스 기본값 설정
        self._set_checkbox('check_rgb', defaults['check_rgb'])
        self._set_checkbox('allow_rgb', defaults['allow_rgb'])
        self._set_checkbox('check_spot', defaults['check_spot'])
        self._set_checkbox('allow_spot', defaults['allow_spot'])
        self._set_checkbox('check_ink_coverage', defaults['check_ink_coverage'])
        
        # 별색 제한 기본값 설정
        self.widgets['spot_limit'].delete(0, 'end')
        self.widgets['spot_limit'].insert(0, defaults['spot_color_limit'])
    
    def get_checkbox_value(self, field_name: str) -> bool:
        """
        특정 체크박스 값 반환
        
        Args:
            field_name: 필드 이름
            
        Returns:
            체크박스 값
        """
        if field_name in self.widgets:
            widget = self.widgets[field_name]
            if isinstance(widget, ctk.CTkCheckBox):
                return widget.get()
        return False
    
    def set_checkbox_value(self, field_name: str, value: bool):
        """
        특정 체크박스 값 설정
        
        Args:
            field_name: 필드 이름
            value: 설정할 값
        """
        self._set_checkbox(field_name, value)
    
    def get_spot_limit_value(self) -> int:
        """별색 개수 제한 값 반환"""
        try:
            value = self.widgets['spot_limit'].get()
            return int(value) if value else 2
        except (ValueError, KeyError):
            return 2