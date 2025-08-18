# src/ui/views/profile_manager/rules_tab.py
"""
프로파일 관리 뷰 - 검사 규칙 탭
PDF 검사 규칙들의 활성화 여부와 심각도를 설정

AI 친화적 문서화:
- 검사 규칙 활성화/비활성화 관리
- 규칙별 심각도 설정 (오류/경고/정보)
- 카테고리별 규칙 그룹화 표시
- 동적 UI 생성으로 확장성 확보
"""

import customtkinter as ctk
from typing import Dict, List, Optional, Any, Tuple
from ...controllers import ProfileController


class RulesTabHelper:
    """
    검사 규칙 탭 헬퍼 클래스
    
    역할:
    - 검사 규칙 목록 동적 생성
    - 카테고리별 규칙 그룹화
    - 규칙별 활성화/비활성화 체크박스
    - 심각도 선택 콤보박스
    - 내장 프로파일 편집 제한
    
    아키텍처:
    - 헬퍼 패턴으로 단일 탭 책임
    - 동적 위젯 생성으로 확장성 확보
    - 컨트롤러와 연계한 규칙 정보 관리
    """
    
    def __init__(
        self,
        parent: ctk.CTkFrame,
        profile_controller: ProfileController,
        widgets: Dict[str, Any]
    ):
        """
        검사 규칙 탭 헬퍼 초기화
        
        Args:
            parent: 탭 프레임
            profile_controller: 프로파일 컨트롤러
            widgets: 위젯 참조 딕셔너리
        """
        self.parent = parent
        self.profile_controller = profile_controller
        self.widgets = widgets
        
        # 규칙별 위젯 저장소
        self.rule_widgets: Dict[str, Dict[str, Any]] = {}
        
        # UI 생성
        self._create_ui()
    
    def _create_ui(self):
        """UI 생성"""
        frame = ctk.CTkScrollableFrame(self.parent)
        frame.pack(fill='both', expand=True)
        
        # 설명 라벨
        self._create_info_label(frame)
        
        # 규칙별 UI 생성
        self._create_rules_ui(frame)
    
    def _create_info_label(self, parent: ctk.CTkScrollableFrame):
        """설명 라벨 생성"""
        info_label = ctk.CTkLabel(
            parent,
            text="각 규칙의 활성화 여부와 심각도를 설정합니다.",
            text_color="gray"
        )
        info_label.pack(pady=10)
    
    def _create_rules_ui(self, parent: ctk.CTkScrollableFrame):
        """규칙별 UI 생성"""
        categories = self.profile_controller.get_rule_categories()
        
        for category in categories:
            self._create_category_section(parent, category)
    
    def _create_category_section(self, parent: ctk.CTkScrollableFrame, category: str):
        """카테고리별 섹션 생성"""
        # 카테고리 헤더
        cat_label = ctk.CTkLabel(
            parent,
            text=self._get_category_display_name(category),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cat_label.pack(anchor='w', padx=10, pady=(15, 5))
        
        # 카테고리 프레임
        cat_frame = ctk.CTkFrame(parent)
        cat_frame.pack(fill='x', padx=20, pady=5)
        
        # 해당 카테고리의 규칙들
        rules = [
            rule for rule in self.profile_controller.get_available_rules()
            if rule['category'] == category
        ]
        
        self._create_rules_in_category(cat_frame, rules)
    
    def _create_rules_in_category(self, parent: ctk.CTkFrame, rules: List[Dict[str, Any]]):
        """카테고리 내 규칙들 생성"""
        for i, rule in enumerate(rules):
            self._create_single_rule_ui(parent, rule, i)
    
    def _create_single_rule_ui(self, parent: ctk.CTkFrame, rule: Dict[str, Any], row: int):
        """개별 규칙 UI 생성"""
        rule_frame = ctk.CTkFrame(parent)
        rule_frame.grid(row=row, column=0, sticky='ew', padx=10, pady=2)
        rule_frame.grid_columnconfigure(1, weight=1)
        
        # 체크박스 (규칙 활성화)
        checkbox = ctk.CTkCheckBox(
            rule_frame,
            text=rule['display'],
            width=250
        )
        checkbox.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        # 심각도 콤보박스
        severity_combo = ctk.CTkComboBox(
            rule_frame,
            values=['오류', '경고', '정보'],
            width=100
        )
        severity_combo.grid(row=0, column=1, sticky='e', padx=5, pady=5)
        severity_combo.set('경고')
        
        # 위젯 저장
        self.rule_widgets[rule['name']] = {
            'enabled': checkbox,
            'severity': severity_combo,
            'display': rule['display'],
            'category': rule['category']
        }
    
    def _get_category_display_name(self, category: str) -> str:
        """카테고리 표시 이름 반환"""
        category_names = {
            'font': '폰트',
            'color': '색상', 
            'image': '이미지',
            'layout': '레이아웃',
            'print': '인쇄'
        }
        return category_names.get(category, category)
    
    def load_profile_data(self, profile_data: Dict[str, Any], is_builtin: bool = False):
        """
        프로파일 데이터 로드
        
        Args:
            profile_data: 프로파일 데이터 딕셔너리
            is_builtin: 내장 프로파일 여부
        """
        enabled_rules = profile_data.get('enabled_rules')
        rule_severities = profile_data.get('rule_severities', {})
        
        # 심각도 매핑
        severity_map = {'error': '오류', 'warning': '경고', 'info': '정보'}
        
        for rule_name, widgets in self.rule_widgets.items():
            # 활성화 여부 설정
            if enabled_rules is None or rule_name in enabled_rules:
                widgets['enabled'].select()
            else:
                widgets['enabled'].deselect()
            
            # 심각도 설정
            severity = rule_severities.get(rule_name, 'warning')
            display_severity = severity_map.get(severity, '경고')
            widgets['severity'].set(display_severity)
        
        # 편집 가능 여부 설정
        self.set_editing_enabled(not is_builtin)
    
    def set_editing_enabled(self, enabled: bool):
        """
        편집 가능 여부 설정
        
        Args:
            enabled: 편집 가능 여부
        """
        for rule_name, widgets in self.rule_widgets.items():
            checkbox = widgets['enabled']
            severity_combo = widgets['severity']
            
            if enabled:
                checkbox.configure(state='normal')
                severity_combo.configure(state='normal')
            else:
                checkbox.configure(state='disabled')
                severity_combo.configure(state='disabled')
    
    def get_rules_data(self) -> Tuple[List[str], Dict[str, str]]:
        """
        현재 규칙 설정 데이터 반환
        
        Returns:
            tuple: (활성화된 규칙 리스트, 규칙별 심각도 딕셔너리)
        """
        enabled_rules = []
        rule_severities = {}
        
        # 심각도 역매핑
        severity_reverse_map = {'오류': 'error', '경고': 'warning', '정보': 'info'}
        
        for rule_name, widgets in self.rule_widgets.items():
            # 활성화된 규칙 수집
            if widgets['enabled'].get():
                enabled_rules.append(rule_name)
            
            # 심각도 설정 수집
            severity_display = widgets['severity'].get()
            severity_code = severity_reverse_map.get(severity_display, 'warning')
            rule_severities[rule_name] = severity_code
        
        return enabled_rules, rule_severities
    
    def validate_data(self) -> Tuple[bool, str]:
        """
        데이터 검증
        
        Returns:
            tuple: (유효성, 오류 메시지)
        """
        # 최소 하나의 규칙은 활성화되어야 함
        enabled_count = sum(
            1 for widgets in self.rule_widgets.values()
            if widgets['enabled'].get()
        )
        
        if enabled_count == 0:
            return False, "최소 하나의 검사 규칙은 활성화되어야 합니다."
        
        return True, ""
    
    def clear_fields(self):
        """모든 필드 초기화"""
        for rule_name, widgets in self.rule_widgets.items():
            widgets['enabled'].deselect()
            widgets['severity'].set('경고')
    
    def select_all_rules(self):
        """모든 규칙 활성화"""
        for rule_name, widgets in self.rule_widgets.items():
            widgets['enabled'].select()
    
    def deselect_all_rules(self):
        """모든 규칙 비활성화"""
        for rule_name, widgets in self.rule_widgets.items():
            widgets['enabled'].deselect()
    
    def get_rule_count_by_category(self) -> Dict[str, int]:
        """카테고리별 규칙 개수 반환"""
        category_counts = {}
        
        for rule_name, widgets in self.rule_widgets.items():
            category = widgets['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
    
    def get_enabled_rule_count_by_category(self) -> Dict[str, int]:
        """카테고리별 활성화된 규칙 개수 반환"""
        category_counts = {}
        
        for rule_name, widgets in self.rule_widgets.items():
            if widgets['enabled'].get():
                category = widgets['category']
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
    
    def set_category_rules_enabled(self, category: str, enabled: bool):
        """특정 카테고리의 모든 규칙 활성화/비활성화"""
        for rule_name, widgets in self.rule_widgets.items():
            if widgets['category'] == category:
                if enabled:
                    widgets['enabled'].select()
                else:
                    widgets['enabled'].deselect()
    
    def set_rules_severity(self, severity: str):
        """모든 규칙의 심각도 일괄 설정"""
        severity_map = {'error': '오류', 'warning': '경고', 'info': '정보'}
        display_severity = severity_map.get(severity, '경고')
        
        for rule_name, widgets in self.rule_widgets.items():
            widgets['severity'].set(display_severity)