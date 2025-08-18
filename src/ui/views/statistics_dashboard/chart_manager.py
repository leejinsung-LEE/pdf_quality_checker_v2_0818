"""
차트 매니저 - 통계 차트 관리
"""

import tkinter as tk
from typing import TYPE_CHECKING, Dict, Any, List
import math

if TYPE_CHECKING:
    from .base import StatisticsDashboardView


class ChartManager:
    """차트 매니저"""
    
    def __init__(self, view: 'StatisticsDashboardView'):
        self.view = view
        self.chart_canvas = None
        self.max_value = 100
        
    def update_chart(self, stats: Dict[str, Any]):
        """차트 업데이트"""
        if 'chart_canvas_frame' not in self.view.widgets:
            return
            
        parent = self.view.widgets['chart_canvas_frame']
        
        # 기존 캔버스 제거
        if self.chart_canvas:
            self.chart_canvas.destroy()
            
        # 새 캔버스 생성
        self.chart_canvas = tk.Canvas(
            parent,
            bg="#212121",
            highlightthickness=0,
            height=250
        )
        self.chart_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 차트 데이터 준비
        chart_data = self._prepare_chart_data(stats)
        
        # 차트 그리기
        if chart_data:
            self._draw_bar_chart(chart_data)
        else:
            self._draw_empty_chart()
            
    def _prepare_chart_data(self, stats: Dict[str, Any]) -> List[tuple]:
        """차트 데이터 준비"""
        period = self.view.current_period
        
        if period == "day":
            # 최근 7일 데이터
            return self._get_daily_data(stats)
        elif period == "week":
            # 최근 4주 데이터
            return self._get_weekly_data(stats)
        elif period == "month":
            # 최근 12개월 데이터
            return self._get_monthly_data(stats)
        else:  # year
            # 최근 5년 데이터
            return self._get_yearly_data(stats)
            
    def _get_daily_data(self, stats: Dict[str, Any]) -> List[tuple]:
        """일별 데이터 가져오기"""
        daily_stats = stats.get('daily_stats', {})
        data = []
        
        for i in range(7):
            day_key = f"day_{i}"
            if day_key in daily_stats:
                data.append((f"Day {i+1}", daily_stats[day_key]))
            else:
                data.append((f"Day {i+1}", 0))
                
        return data
        
    def _get_weekly_data(self, stats: Dict[str, Any]) -> List[tuple]:
        """주별 데이터 가져오기"""
        weekly_stats = stats.get('weekly_stats', {})
        data = []
        
        for i in range(4):
            week_key = f"week_{i}"
            if week_key in weekly_stats:
                data.append((f"Week {i+1}", weekly_stats[week_key]))
            else:
                data.append((f"Week {i+1}", 0))
                
        return data
        
    def _get_monthly_data(self, stats: Dict[str, Any]) -> List[tuple]:
        """월별 데이터 가져오기"""
        monthly_stats = stats.get('monthly_stats', {})
        months = ["1월", "2월", "3월", "4월", "5월", "6월",
                 "7월", "8월", "9월", "10월", "11월", "12월"]
        data = []
        
        for i, month in enumerate(months):
            month_key = f"month_{i}"
            if month_key in monthly_stats:
                data.append((month, monthly_stats[month_key]))
            else:
                data.append((month, 0))
                
        return data
        
    def _get_yearly_data(self, stats: Dict[str, Any]) -> List[tuple]:
        """연도별 데이터 가져오기"""
        yearly_stats = stats.get('yearly_stats', {})
        data = []
        
        for i in range(5):
            year_key = f"year_{i}"
            if year_key in yearly_stats:
                data.append((f"Year {i+1}", yearly_stats[year_key]))
            else:
                data.append((f"Year {i+1}", 0))
                
        return data
        
    def _draw_bar_chart(self, data: List[tuple]):
        """막대 차트 그리기"""
        if not data:
            self._draw_empty_chart()
            return
            
        canvas = self.chart_canvas
        width = canvas.winfo_reqwidth()
        height = 250
        
        # 마진과 차트 영역
        margin_x = 50
        margin_y = 30
        chart_width = width - (margin_x * 2)
        chart_height = height - (margin_y * 2)
        
        # 최대값 계산
        max_value = max(value for _, value in data)
        if max_value == 0:
            max_value = 1
        self.max_value = max_value
        
        # 막대 너비와 간격
        bar_count = len(data)
        bar_width = chart_width / (bar_count * 2)
        bar_spacing = bar_width
        
        # Y축 그리기
        canvas.create_line(
            margin_x, margin_y,
            margin_x, height - margin_y,
            fill="gray", width=2
        )
        
        # X축 그리기
        canvas.create_line(
            margin_x, height - margin_y,
            width - margin_x, height - margin_y,
            fill="gray", width=2
        )
        
        # Y축 눈금과 레이블
        for i in range(5):
            y = margin_y + (chart_height * i / 4)
            value = max_value * (1 - i / 4)
            
            # 눈금
            canvas.create_line(
                margin_x - 5, y,
                margin_x, y,
                fill="gray"
            )
            
            # 레이블
            canvas.create_text(
                margin_x - 20, y,
                text=f"{int(value)}",
                fill="white",
                anchor="e"
            )
        
        # 막대 그리기
        for i, (label, value) in enumerate(data):
            # 막대 위치와 높이
            x = margin_x + (i * (bar_width + bar_spacing)) + bar_spacing
            bar_height = (value / max_value) * chart_height
            y1 = height - margin_y
            y2 = height - margin_y - bar_height
            
            # 막대 색상 (그라데이션 효과)
            color = self._get_bar_color(value, max_value)
            
            # 막대 그리기
            canvas.create_rectangle(
                x, y1,
                x + bar_width, y2,
                fill=color,
                outline=""
            )
            
            # 값 표시
            if value > 0:
                canvas.create_text(
                    x + bar_width / 2, y2 - 10,
                    text=str(int(value)),
                    fill="white",
                    font=("Arial", 10, "bold")
                )
            
            # X축 레이블
            canvas.create_text(
                x + bar_width / 2, height - margin_y + 15,
                text=label,
                fill="gray",
                font=("Arial", 9),
                anchor="n"
            )
    
    def _get_bar_color(self, value: float, max_value: float) -> str:
        """막대 색상 계산 (그라데이션)"""
        if max_value == 0:
            return "#667eea"
            
        ratio = value / max_value
        
        # 파란색 그라데이션
        r = int(102 + (100 * (1 - ratio)))
        g = int(126 + (50 * (1 - ratio)))
        b = int(234 - (50 * (1 - ratio)))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _draw_empty_chart(self):
        """빈 차트 그리기"""
        canvas = self.chart_canvas
        width = canvas.winfo_reqwidth()
        height = 250
        
        canvas.create_text(
            width / 2, height / 2,
            text="데이터가 없습니다",
            fill="gray",
            font=("Arial", 14)
        )