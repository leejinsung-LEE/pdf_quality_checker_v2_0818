"""
통계 위젯 빌더
기능: 대시보드 통계 카드 생성 및 관리
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING, Dict, Any
import customtkinter as ctk

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import DashboardView


class StatsWidgetBuilder:
    """
    통계 위젯 빌더
    
    역할:
    - 통계 카드 생성
    - 카드 데이터 업데이트
    - 동적 정보 표시
    """
    
    def __init__(self, view: 'DashboardView'):
        """
        빌더 초기화
        
        Args:
            view: 메인 대시보드 뷰
        """
        self.view = view
    
    def create_stat_cards(self, parent) -> ctk.CTkFrame:
        """통계 카드 생성"""
        cards_container = ctk.CTkFrame(parent, fg_color="transparent")
        
        # 카드 데이터 설정
        card_configs = [
            {
                'key': 'total_files',
                'title': '총 처리',
                'icon': '📄',
                'color': self.view.colors['accent'],
                'value': '0'
            },
            {
                'key': 'success_count',
                'title': '성공',
                'icon': '✅',
                'color': self.view.colors['success'],
                'value': '0'
            },
            {
                'key': 'warning_count',
                'title': '경고',
                'icon': '⚠️',
                'color': self.view.colors['warning'],
                'value': '0'
            },
            {
                'key': 'error_count',
                'title': '오류',
                'icon': '❌',
                'color': self.view.colors['error'],
                'value': '0'
            },
            {
                'key': 'auto_fixed',
                'title': '자동수정',
                'icon': '🔧',
                'color': self.view.colors['info'],
                'value': '0'
            }
        ]
        
        # 카드 생성
        for i, config in enumerate(card_configs):
            card = self._create_stat_card(cards_container, config)
            card.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            self.view.stat_cards[config['key']] = card
        
        # 그리드 설정
        for i in range(len(card_configs)):
            cards_container.grid_columnconfigure(i, weight=1)
        
        return cards_container
    
    def _create_stat_card(self, parent, config: Dict[str, Any]) -> ctk.CTkFrame:
        """개별 통계 카드 생성"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.view.colors['bg_card'],
            corner_radius=10,
            height=120
        )
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill='both', expand=True, padx=20, pady=15)
        
        # 아이콘과 제목
        header_frame = ctk.CTkFrame(inner, fg_color="transparent")
        header_frame.pack(fill='x')
        
        ctk.CTkLabel(
            header_frame,
            text=config['icon'],
            font=('Arial', 28)
        ).pack(side='left')
        
        ctk.CTkLabel(
            header_frame,
            text=config['title'],
            font=('Arial', 12),
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(10, 0))
        
        # 값
        value_label = ctk.CTkLabel(
            inner,
            text=config['value'],
            font=('Arial', 32, 'bold'),
            text_color=config['color']
        )
        value_label.pack(pady=(10, 0))
        
        # 레이블 참조 저장 (오류 방지를 위해 card 객체에 속성 추가)
        card.value_label = value_label
        
        # 부가 정보 레이블
        card.info_label = ctk.CTkLabel(
            inner,
            text="",
            font=('Arial', 10),
            text_color=self.view.colors['text_secondary']
        )
        card.info_label.pack()
        
        return card
    
    def update_stat_cards(self, stats: Dict[str, Any], current_stats: Dict[str, Any]):
        """통계 카드 업데이트"""
        basic = stats.get('basic', {})
        
        # 총 처리 파일 카드
        if 'total_files' in self.view.stat_cards:
            card = self.view.stat_cards['total_files']
            if hasattr(card, 'value_label'):
                card.value_label.configure(
                    text=str(basic.get('total_files', 0))
                )
            # 현재 처리 중 표시
            processing = current_stats.get('processing', 0)
            if processing > 0 and hasattr(card, 'info_label'):
                card.info_label.configure(
                    text=f"처리 중: {processing}"
                )
        
        # 성공 카드
        if 'success_count' in self.view.stat_cards:
            card = self.view.stat_cards['success_count']
            if hasattr(card, 'value_label'):
                card.value_label.configure(
                    text=str(basic.get('success_count', 0))
                )
            # 성공률 표시
            total = basic.get('total_files', 0)
            if total > 0 and hasattr(card, 'info_label'):
                rate = (basic.get('success_count', 0) / total) * 100
                card.info_label.configure(
                    text=f"{rate:.1f}%"
                )
        
        # 경고 카드
        if 'warning_count' in self.view.stat_cards:
            card = self.view.stat_cards['warning_count']
            if hasattr(card, 'value_label'):
                card.value_label.configure(
                    text=str(basic.get('total_warnings', 0))
                )
        
        # 오류 카드
        if 'error_count' in self.view.stat_cards:
            card = self.view.stat_cards['error_count']
            if hasattr(card, 'value_label'):
                card.value_label.configure(
                    text=str(basic.get('total_errors', 0))
                )
        
        # 자동 수정 카드
        if 'auto_fixed' in self.view.stat_cards:
            card = self.view.stat_cards['auto_fixed']
            if hasattr(card, 'value_label'):
                card.value_label.configure(
                    text=str(basic.get('auto_fixed_count', 0))
                )
            # 자동 수정률 표시
            total_errors = basic.get('total_errors', 0)
            if total_errors > 0 and hasattr(card, 'info_label'):
                rate = (basic.get('auto_fixed_count', 0) / total_errors) * 100
                card.info_label.configure(
                    text=f"{rate:.1f}%"
                )