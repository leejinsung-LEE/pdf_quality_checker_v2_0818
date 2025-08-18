"""
대시보드 뷰 - 메인 클래스
기능: PDF 처리 통계와 분석 정보를 시각적으로 표시
의존성: customtkinter, FileController, matplotlib (선택적)
최종 수정: 2025-01-12

AI 친화적 문서화:
- 역할: 통계 시각화 및 분석 대시보드
- 입력: parent 위젯, FileController
- 출력: 대시보드 뷰 위젯
- 상태: period_var, stat_cards, 차트 인스턴스
"""

import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from ...controllers import FileController

# 헬퍼 클래스 import
from .stats_manager import StatisticsManager
from .stats_widgets import StatsWidgetBuilder
from .charts import ChartManager
from .quick_actions import QuickActionsBuilder

# matplotlib 체크 (차트 모듈에서 처리)
from .charts import HAS_MATPLOTLIB


class DashboardView(ctk.CTkFrame):
    """
    대시보드 뷰 - 통계와 분석 정보를 표시
    
    주요 기능:
    - 실시간 통계 표시
    - 처리 현황 차트
    - 통계 보고서 생성
    - 기간별 필터링
    
    아키텍처:
    - MVC 패턴의 View 컴포넌트
    - 헬퍼 클래스를 통한 책임 분리
    - matplotlib 선택적 사용
    """
    
    def __init__(self, parent, controller: FileController, **kwargs):
        """
        뷰 초기화
        
        Args:
            parent: 부모 위젯
            controller: 파일 컨트롤러
            **kwargs: 추가 옵션
        """
        super().__init__(parent, **kwargs)
        
        self.controller = controller
        self.stats_manager = StatisticsManager()
        
        # UI 상태
        self.period_var = tk.StringVar(value="today")
        
        # 색상 테마
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'bg_card': '#2a2a2a',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#667eea',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'info': '#17a2b8',
            'border': '#404040'
        }
        
        # 통계 카드 참조 (오류 방지를 위해 초기화)
        self.stat_cards = {}
        
        # 차트 관련 위젯 (오류 방지를 위해 None으로 초기화)
        self.stats_text = None
        self.chart_manager = None
        
        # 헬퍼 클래스 초기화
        self.stats_widget_builder = StatsWidgetBuilder(self)
        self.quick_actions_builder = QuickActionsBuilder(self)
        
        # 차트 매니저는 조건부 초기화
        if HAS_MATPLOTLIB:
            self.chart_manager = ChartManager(self)
        
        # UI 생성
        self._create_ui()
        
        # 초기 데이터 로드
        self.refresh_data()
    
    def _create_ui(self):
        """UI 구성"""
        self.configure(fg_color=self.colors['bg_primary'])
        
        # 스크롤 가능한 프레임
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color=self.colors['bg_primary'])
        scroll_frame.pack(fill='both', expand=True)
        
        # 헤더
        header_frame = self.quick_actions_builder.create_header(scroll_frame)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # 통계 카드
        cards_frame = self.stats_widget_builder.create_stat_cards(scroll_frame)
        cards_frame.pack(fill='x', padx=20, pady=10)
        
        # 차트 영역
        charts_frame = self._create_charts_area(scroll_frame)
        charts_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
    
    def _create_charts_area(self, parent) -> ctk.CTkFrame:
        """차트 영역 생성"""
        charts_container = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_card'],
            corner_radius=10
        )
        
        inner = ctk.CTkFrame(charts_container, fg_color="transparent")
        inner.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 차트 제목
        ctk.CTkLabel(
            inner,
            text="📈 처리 현황 분석",
            font=('Arial', 18, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        # matplotlib 사용 가능 여부에 따라 분기
        if self.chart_manager:
            self.chart_manager.create_charts(inner)
        else:
            # 텍스트 기반 통계
            self.stats_text = tk.Text(
                inner,
                height=20,
                wrap='word',
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary'],
                font=('Consolas', 11),
                relief='flat',
                padx=20,
                pady=20
            )
            self.stats_text.pack(fill='both', expand=True)
        
        return charts_container
    
    def refresh_data(self):
        """데이터 새로고침"""
        # 기간 계산
        date_range = self.calculate_date_range(self.period_var.get())
        
        # 통계 데이터 가져오기
        stats = self.stats_manager.get_statistics(date_range)
        
        # 현재 처리 중인 파일 통계 추가
        current_stats = {}
        if self.controller:
            current_stats = self.controller.get_statistics()
        
        # 카드 업데이트
        self.stats_widget_builder.update_stat_cards(stats, current_stats)
        
        # 차트 업데이트
        if self.chart_manager:
            self.chart_manager.update_charts(stats)
        elif self.stats_text:
            self.quick_actions_builder.update_text_stats(stats)
    
    def calculate_date_range(self, period: str) -> Optional[Tuple[datetime, datetime]]:
        """기간 계산"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if period == 'today':
            return (today, today + timedelta(days=1))
        elif period == 'week':
            start = today - timedelta(days=today.weekday())
            return (start, today + timedelta(days=1))
        elif period == 'month':
            start = today.replace(day=1)
            return (start, today + timedelta(days=1))
        else:  # all
            return None
    
    def record_file_completion(self, file_item):
        """파일 처리 완료 기록 (외부에서 호출)"""
        self.stats_manager.record_file_processing(file_item)
        # 화면 갱신
        self.refresh_data()
    
    def update_statistics(self):
        """통계 업데이트 (탭 변경 시 호출)"""
        self.refresh_data()