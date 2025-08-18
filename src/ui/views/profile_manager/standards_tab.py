# src/ui/views/profile_manager/standards_tab.py
"""
프로파일 관리 뷰 - 품질 기준 탭
PDF 품질 검사 기준값들(DPI, 재단선, 텍스트 크기 등)을 설정

AI 친화적 문서화:
- 품질 기준값 입력 UI 관리
- 수치 유효성 검증
- 카테고리별 설정 구분 표시
- 타입 힌트를 통한 안전한 데이터 처리
"""

import customtkinter as ctk
from typing import Dict, Optional, Any, Tuple
# QualityStandards import는 필요시 활성화
# from ....config.constants import QualityStandards


class StandardsTabHelper:
    """
    품질 기준 탭 헬퍼 클래스
    
    역할:
    - 이미지 DPI 설정 UI
    - 재단선 크기 설정 UI
    - 텍스트 크기 제한 UI
    - 잉크 커버리지 한계값 UI
    - 수치 데이터 검증
    
    아키텍처:
    - 헬퍼 패턴으로 단일 탭 책임
    - 카테고리별 UI 그룹화
    - 상수 클래스 활용한 기본값 관리
    """
    
    def __init__(self, parent: ctk.CTkFrame, widgets: Dict[str, Any]):
        """
        품질 기준 탭 헬퍼 초기화
        
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
        
        row = 0
        
        # 이미지 해상도 섹션
        row = self._create_image_section(frame, row)
        
        # 재단선 섹션
        row = self._create_bleed_section(frame, row)
        
        # 텍스트 섹션
        row = self._create_text_section(frame, row)
        
        # 잉크 커버리지 섹션
        row = self._create_ink_section(frame, row)
    
    def _create_image_section(self, parent: ctk.CTkScrollableFrame, start_row: int) -> int:
        """이미지 해상도 섹션 생성"""
        # 섹션 헤더
        image_label = ctk.CTkLabel(
            parent,
            text="이미지 해상도",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        image_label.grid(row=start_row, column=0, columnspan=2, 
                        sticky='w', padx=10, pady=(10, 5))
        
        current_row = start_row + 1
        
        # 최소 DPI
        min_dpi_label = ctk.CTkLabel(parent, text="최소 DPI:")
        min_dpi_label.grid(row=current_row, column=0, sticky='w', 
                          padx=20, pady=5)
        
        self.widgets['min_dpi'] = ctk.CTkEntry(parent, width=100)
        self.widgets['min_dpi'].grid(row=current_row, column=1, 
                                    sticky='w', padx=10, pady=5)
        
        # 경고 DPI
        current_row += 1
        warning_dpi_label = ctk.CTkLabel(parent, text="경고 DPI:")
        warning_dpi_label.grid(row=current_row, column=0, sticky='w', 
                              padx=20, pady=5)
        
        self.widgets['warning_dpi'] = ctk.CTkEntry(parent, width=100)
        self.widgets['warning_dpi'].grid(row=current_row, column=1, 
                                        sticky='w', padx=10, pady=5)
        
        # 최적 DPI
        current_row += 1
        optimal_dpi_label = ctk.CTkLabel(parent, text="최적 DPI:")
        optimal_dpi_label.grid(row=current_row, column=0, sticky='w', 
                              padx=20, pady=5)
        
        self.widgets['optimal_dpi'] = ctk.CTkEntry(parent, width=100)
        self.widgets['optimal_dpi'].grid(row=current_row, column=1, 
                                        sticky='w', padx=10, pady=5)
        
        return current_row + 1
    
    def _create_bleed_section(self, parent: ctk.CTkScrollableFrame, start_row: int) -> int:
        """재단선 섹션 생성"""
        # 섹션 헤더
        bleed_label = ctk.CTkLabel(
            parent,
            text="재단선",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        bleed_label.grid(row=start_row, column=0, columnspan=2, 
                        sticky='w', padx=10, pady=(20, 5))
        
        current_row = start_row + 1
        
        # 재단선 크기
        bleed_size_label = ctk.CTkLabel(parent, text="표준 재단선 (mm):")
        bleed_size_label.grid(row=current_row, column=0, sticky='w', 
                             padx=20, pady=5)
        
        self.widgets['bleed_size'] = ctk.CTkEntry(parent, width=100)
        self.widgets['bleed_size'].grid(row=current_row, column=1, 
                                       sticky='w', padx=10, pady=5)
        
        return current_row + 1
    
    def _create_text_section(self, parent: ctk.CTkScrollableFrame, start_row: int) -> int:
        """텍스트 섹션 생성"""
        # 섹션 헤더
        text_label = ctk.CTkLabel(
            parent,
            text="텍스트",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        text_label.grid(row=start_row, column=0, columnspan=2, 
                       sticky='w', padx=10, pady=(20, 5))
        
        current_row = start_row + 1
        
        # 최소 텍스트 크기
        min_text_label = ctk.CTkLabel(parent, text="최소 텍스트 크기 (pt):")
        min_text_label.grid(row=current_row, column=0, sticky='w', 
                           padx=20, pady=5)
        
        self.widgets['min_text_size'] = ctk.CTkEntry(parent, width=100)
        self.widgets['min_text_size'].grid(row=current_row, column=1, 
                                          sticky='w', padx=10, pady=5)
        
        return current_row + 1
    
    def _create_ink_section(self, parent: ctk.CTkScrollableFrame, start_row: int) -> int:
        """잉크 커버리지 섹션 생성"""
        # 섹션 헤더
        ink_label = ctk.CTkLabel(
            parent,
            text="잉크 커버리지",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ink_label.grid(row=start_row, column=0, columnspan=2, 
                      sticky='w', padx=10, pady=(20, 5))
        
        current_row = start_row + 1
        
        # 최대 잉크 커버리지
        max_ink_label = ctk.CTkLabel(parent, text="최대 잉크 커버리지 (%):")
        max_ink_label.grid(row=current_row, column=0, sticky='w', 
                          padx=20, pady=5)
        
        self.widgets['max_ink'] = ctk.CTkEntry(parent, width=100)
        self.widgets['max_ink'].grid(row=current_row, column=1, 
                                    sticky='w', padx=10, pady=5)
        
        # 경고 잉크 커버리지
        current_row += 1
        warning_ink_label = ctk.CTkLabel(parent, text="경고 잉크 커버리지 (%):")
        warning_ink_label.grid(row=current_row, column=0, sticky='w', 
                              padx=20, pady=5)
        
        self.widgets['warning_ink'] = ctk.CTkEntry(parent, width=100)
        self.widgets['warning_ink'].grid(row=current_row, column=1, 
                                        sticky='w', padx=10, pady=5)
        
        return current_row + 1
    
    def load_profile_data(self, profile_data: Dict[str, Any]):
        """
        프로파일 데이터 로드
        
        Args:
            profile_data: 프로파일 데이터 딕셔너리
        """
        standards = profile_data.get('quality_standards', {})
        
        # 기본값 설정 (constants에서 가져오기)
        defaults = {
            'min_image_dpi': 300,
            'warning_image_dpi': 200,
            'optimal_image_dpi': 300,
            'standard_bleed_size': 3.0,
            'min_text_size': 6.0,
            'max_ink_coverage': 320,
            'warning_ink_coverage': 300
        }
        
        # 각 필드에 값 설정
        self._set_field_value('min_dpi', standards.get('min_image_dpi', defaults['min_image_dpi']))
        self._set_field_value('warning_dpi', standards.get('warning_image_dpi', defaults['warning_image_dpi']))
        self._set_field_value('optimal_dpi', standards.get('optimal_image_dpi', defaults['optimal_image_dpi']))
        self._set_field_value('bleed_size', standards.get('standard_bleed_size', defaults['standard_bleed_size']))
        self._set_field_value('min_text_size', standards.get('min_text_size', defaults['min_text_size']))
        self._set_field_value('max_ink', standards.get('max_ink_coverage', defaults['max_ink_coverage']))
        self._set_field_value('warning_ink', standards.get('warning_ink_coverage', defaults['warning_ink_coverage']))
    
    def _set_field_value(self, field_name: str, value: Any):
        """필드 값 설정"""
        if field_name not in self.widgets:
            return
        
        widget = self.widgets[field_name]
        if isinstance(widget, ctk.CTkEntry):
            widget.delete(0, 'end')
            widget.insert(0, str(value))
    
    def set_editing_enabled(self, enabled: bool):
        """
        편집 가능 여부 설정
        
        Args:
            enabled: 편집 가능 여부
        """
        standards_fields = [
            'min_dpi', 'warning_dpi', 'optimal_dpi',
            'bleed_size', 'min_text_size', 'max_ink', 'warning_ink'
        ]
        
        for field in standards_fields:
            if field in self.widgets:
                widget = self.widgets[field]
                if isinstance(widget, ctk.CTkEntry):
                    if enabled:
                        widget.configure(state='normal')
                    else:
                        widget.configure(state='disabled')
    
    def get_standards_data(self) -> Dict[str, Any]:
        """
        현재 품질 기준 데이터 반환
        
        Returns:
            품질 기준 데이터 딕셔너리
        """
        try:
            return {
                'min_image_dpi': int(self.widgets['min_dpi'].get() or '300'),
                'warning_image_dpi': int(self.widgets['warning_dpi'].get() or '200'),
                'optimal_image_dpi': int(self.widgets['optimal_dpi'].get() or '300'),
                'standard_bleed_size': float(self.widgets['bleed_size'].get() or '3.0'),
                'min_text_size': float(self.widgets['min_text_size'].get() or '6.0'),
                'max_ink_coverage': int(self.widgets['max_ink'].get() or '320'),
                'warning_ink_coverage': int(self.widgets['warning_ink'].get() or '300')
            }
        except ValueError as e:
            # 잘못된 값이 입력된 경우 기본값 반환
            return {
                'min_image_dpi': 300,
                'warning_image_dpi': 200,
                'optimal_image_dpi': 300,
                'standard_bleed_size': 3.0,
                'min_text_size': 6.0,
                'max_ink_coverage': 320,
                'warning_ink_coverage': 300
            }
    
    def validate_data(self) -> Tuple[bool, str]:
        """
        데이터 검증
        
        Returns:
            tuple: (유효성, 오류 메시지)
        """
        try:
            # DPI 값들 검증
            min_dpi = int(self.widgets['min_dpi'].get() or '0')
            warning_dpi = int(self.widgets['warning_dpi'].get() or '0')
            optimal_dpi = int(self.widgets['optimal_dpi'].get() or '0')
            
            if min_dpi <= 0 or warning_dpi <= 0 or optimal_dpi <= 0:
                return False, "DPI 값은 양수여야 합니다."
            
            if min_dpi > optimal_dpi:
                return False, "최소 DPI는 최적 DPI보다 작거나 같아야 합니다."
            
            # 재단선 크기 검증
            bleed_size = float(self.widgets['bleed_size'].get() or '0')
            if bleed_size < 0:
                return False, "재단선 크기는 0 이상이어야 합니다."
            
            # 텍스트 크기 검증
            min_text_size = float(self.widgets['min_text_size'].get() or '0')
            if min_text_size <= 0:
                return False, "최소 텍스트 크기는 양수여야 합니다."
            
            # 잉크 커버리지 검증
            max_ink = int(self.widgets['max_ink'].get() or '0')
            warning_ink = int(self.widgets['warning_ink'].get() or '0')
            
            if max_ink <= 0 or warning_ink <= 0:
                return False, "잉크 커버리지 값은 양수여야 합니다."
            
            if max_ink > 400:
                return False, "최대 잉크 커버리지는 400% 이하여야 합니다."
            
            if warning_ink > max_ink:
                return False, "경고 잉크 커버리지는 최대값보다 작거나 같아야 합니다."
            
            return True, ""
            
        except ValueError:
            return False, "숫자 형식이 올바르지 않습니다."
    
    def clear_fields(self):
        """모든 필드 초기화"""
        standards_fields = [
            'min_dpi', 'warning_dpi', 'optimal_dpi',
            'bleed_size', 'min_text_size', 'max_ink', 'warning_ink'
        ]
        
        for field in standards_fields:
            if field in self.widgets:
                widget = self.widgets[field]
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, 'end')
    
    def reset_to_defaults(self):
        """기본값으로 재설정"""
        defaults = {
            'min_dpi': '300',
            'warning_dpi': '200', 
            'optimal_dpi': '300',
            'bleed_size': '3.0',
            'min_text_size': '6.0',
            'max_ink': '320',
            'warning_ink': '300'
        }
        
        for field, value in defaults.items():
            self._set_field_value(field, value)