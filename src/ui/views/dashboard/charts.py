"""
차트 관리자
기능: matplotlib를 사용한 차트 생성 및 관리
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING, Dict, Any, List
import customtkinter as ctk
import platform

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import DashboardView

# matplotlib 선택적 import (오류 방지)
HAS_MATPLOTLIB = False
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib
    
    # 한글 폰트 설정 (플랫폼별 최적화)
    system = platform.system()
    if system == 'Windows':
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = ['Malgun Gothic', 'NanumGothic', 'Arial Unicode MS']
    elif system == 'Darwin':  # macOS
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = ['AppleGothic', 'Apple SD Gothic Neo', 'Helvetica']
    else:  # Linux
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = ['NanumGothic', 'DejaVu Sans', 'Liberation Sans']
    
    # 마이너스 기호 깨짐 방지
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    # 폰트 캐시 초기화 (폰트 문제 해결)
    try:
        from matplotlib import font_manager
        font_manager._rebuild()
    except Exception:
        pass
    
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class ChartManager:
    """
    차트 관리자
    
    역할:
    - matplotlib 차트 생성
    - 차트 데이터 업데이트
    - 차트 스타일 관리
    """
    
    def __init__(self, view: 'DashboardView'):
        """
        관리자 초기화
        
        Args:
            view: 메인 대시보드 뷰
        """
        self.view = view
        
        # 차트 인스턴스 (오류 방지를 위해 None으로 초기화)
        self.daily_fig = None
        self.daily_ax = None
        self.daily_canvas = None
        
        self.issues_fig = None
        self.issues_ax = None
        self.issues_canvas = None
    
    def create_charts(self, parent):
        """matplotlib 차트 생성"""
        if not HAS_MATPLOTLIB:
            return
        
        # 차트 컨테이너
        charts_frame = ctk.CTkFrame(parent, fg_color="transparent")
        charts_frame.pack(fill='both', expand=True)
        
        # 1. 일별 처리량 차트
        daily_frame = ctk.CTkFrame(
            charts_frame, 
            fg_color=self.view.colors['bg_secondary']
        )
        daily_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.daily_fig = Figure(
            figsize=(6, 4), 
            dpi=80, 
            facecolor=self.view.colors['bg_secondary']
        )
        self.daily_ax = self.daily_fig.add_subplot(111)
        self.daily_ax.set_facecolor(self.view.colors['bg_secondary'])
        
        self.daily_canvas = FigureCanvasTkAgg(self.daily_fig, master=daily_frame)
        self.daily_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # 2. 문제 유형별 차트
        issues_frame = ctk.CTkFrame(
            charts_frame, 
            fg_color=self.view.colors['bg_secondary']
        )
        issues_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        self.issues_fig = Figure(
            figsize=(6, 4), 
            dpi=80, 
            facecolor=self.view.colors['bg_secondary']
        )
        self.issues_ax = self.issues_fig.add_subplot(111)
        self.issues_ax.set_facecolor(self.view.colors['bg_secondary'])
        
        self.issues_canvas = FigureCanvasTkAgg(self.issues_fig, master=issues_frame)
        self.issues_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # 그리드 설정
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # 차트 스타일 설정
        self._setup_chart_style()
    
    def _setup_chart_style(self):
        """차트 스타일 설정"""
        if not HAS_MATPLOTLIB:
            return
        
        for ax in [self.daily_ax, self.issues_ax]:
            if ax:
                ax.tick_params(colors='white', which='both')
                ax.spines['bottom'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
    
    def update_charts(self, stats: Dict[str, Any]):
        """차트 업데이트"""
        if not HAS_MATPLOTLIB:
            return
        
        # 1. 일별 처리량 차트
        self._update_daily_chart(stats.get('daily', []))
        
        # 2. 문제 유형별 차트
        self._update_issues_chart(stats.get('common_issues', []))
    
    def _update_daily_chart(self, daily_data: List[Dict[str, Any]]):
        """일별 처리량 차트 업데이트"""
        if not self.daily_ax or not self.daily_canvas:
            return
        
        self.daily_ax.clear()
        
        if not daily_data:
            self.daily_ax.text(0.5, 0.5, '데이터 없음',
                              ha='center', va='center',
                              transform=self.daily_ax.transAxes,
                              color='white', fontsize=14)
        else:
            dates = [d['date'] for d in daily_data]
            files = [d['files'] for d in daily_data]
            
            bars = self.daily_ax.bar(dates, files, color=self.view.colors['accent'])
            
            # 스타일 설정
            self.daily_ax.set_xlabel('날짜', fontsize=10, color='white')
            self.daily_ax.set_ylabel('파일 수', fontsize=10, color='white')
            self.daily_ax.set_title('일별 처리량', fontsize=12, fontweight='bold', color='white')
            self.daily_ax.grid(True, alpha=0.3)
            
            # 값 표시
            for bar, value in zip(bars, files):
                height = bar.get_height()
                self.daily_ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + 0.5,
                    f'{value}',
                    ha='center', va='bottom',
                    fontsize=9, color='white'
                )
            
            # X축 레이블 회전
            if HAS_MATPLOTLIB:
                plt.setp(self.daily_ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self.daily_fig.tight_layout()
        self.daily_canvas.draw()
    
    def _update_issues_chart(self, issue_data: List[Dict[str, Any]]):
        """문제 유형별 차트 업데이트"""
        if not self.issues_ax or not self.issues_canvas:
            return
        
        self.issues_ax.clear()
        
        if not issue_data:
            self.issues_ax.text(0.5, 0.5, '데이터 없음',
                               ha='center', va='center',
                               transform=self.issues_ax.transAxes,
                               color='white', fontsize=14)
        else:
            # 상위 5개만 표시
            top_issues = issue_data[:5]
            
            # 한글 레이블 매핑
            type_labels = {
                'font_not_embedded': '폰트 미임베딩',
                'low_resolution_image': '저해상도 이미지',
                'rgb_only': 'RGB 색상',
                'high_ink_coverage': '높은 잉크량',
                'page_size_inconsistent': '페이지 크기 불일치',
                'font_embedding': '폰트 임베딩',
                'rgb_color_usage': 'RGB 색상 사용',
                'image_resolution': '이미지 해상도'
            }
            
            types = [type_labels.get(i['type'], i['type']) for i in top_issues]
            counts = [i['count'] for i in top_issues]
            
            # 수평 막대 그래프
            bars = self.issues_ax.barh(types, counts, color=self.view.colors['warning'])
            
            # 스타일 설정
            self.issues_ax.set_xlabel('발생 횟수', fontsize=10, color='white')
            self.issues_ax.set_title('주요 문제 유형', fontsize=12, fontweight='bold', color='white')
            self.issues_ax.grid(True, alpha=0.3, axis='x')
            
            # 값 표시
            for bar, value in zip(bars, counts):
                width = bar.get_width()
                self.issues_ax.text(
                    width + 0.5,
                    bar.get_y() + bar.get_height()/2.,
                    f'{value}',
                    ha='left', va='center',
                    fontsize=9, color='white'
                )
        
        self.issues_fig.tight_layout()
        self.issues_canvas.draw()