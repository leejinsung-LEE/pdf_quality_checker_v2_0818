# src/reporting/html_builder/chart_generator.py
"""
차트 및 시각화 요소 생성
"""

from typing import Dict, Any


class ChartGenerator:
    """차트 생성기"""
    
    @staticmethod
    def create_score_circle(score: float, color: str) -> str:
        """
        원형 점수 차트 생성
        
        Args:
            score: 품질 점수 (0-100)
            color: 색상 코드
            
        Returns:
            SVG 원형 차트 HTML
        """
        # SVG 원형 차트
        # 둘레: 2πr = 2 * 3.14159 * 90 ≈ 565
        # 점수에 따른 dash 길이 계산
        dash_length = score * 5.65  # 100점일 때 전체 둘레
        
        return f"""
            <div class="score-circle">
                <svg width="200" height="200" viewBox="0 0 200 200">
                    <!-- 배경 원 -->
                    <circle cx="100" cy="100" r="90" 
                            fill="none" 
                            stroke="#e9ecef" 
                            stroke-width="20"/>
                    <!-- 점수 원 -->
                    <circle cx="100" cy="100" r="90" 
                            fill="none" 
                            stroke="{color}" 
                            stroke-width="20"
                            stroke-dasharray="{dash_length} 565" 
                            stroke-dashoffset="0"
                            transform="rotate(-90 100 100)"/>
                </svg>
                <div class="score-value" style="color: {color}">{score:.0f}</div>
            </div>
        """
    
    @staticmethod
    def create_progress_bar(value: float, max_value: float, color: str = '#007bff') -> str:
        """
        진행률 바 생성
        
        Args:
            value: 현재 값
            max_value: 최대 값
            color: 바 색상
            
        Returns:
            진행률 바 HTML
        """
        percentage = (value / max_value * 100) if max_value > 0 else 0
        
        return f"""
            <div class="progress-bar" style="width: 100%; background: #e9ecef; border-radius: 4px; height: 20px; overflow: hidden;">
                <div style="width: {percentage}%; background: {color}; height: 100%; transition: width 0.5s ease;">
                </div>
            </div>
        """
    
    @staticmethod
    def create_pie_chart(data: Dict[str, int], width: int = 200, height: int = 200) -> str:
        """
        파이 차트 생성
        
        Args:
            data: 데이터 딕셔너리
            width: 차트 너비
            height: 차트 높이
            
        Returns:
            SVG 파이 차트 HTML
        """
        if not data or sum(data.values()) == 0:
            return ""
        
        total = sum(data.values())
        colors = ['#dc3545', '#ffc107', '#17a2b8', '#28a745', '#6610f2']
        
        svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        
        # 중심점
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 2 - 10
        
        # 시작 각도
        start_angle = 0
        
        for i, (label, value) in enumerate(data.items()):
            if value == 0:
                continue
            
            # 각도 계산
            angle = (value / total) * 360
            end_angle = start_angle + angle
            
            # 큰 호 플래그
            large_arc = 1 if angle > 180 else 0
            
            # 시작점과 끝점 계산
            start_x = cx + radius * self._cos(start_angle)
            start_y = cy + radius * self._sin(start_angle)
            end_x = cx + radius * self._cos(end_angle)
            end_y = cy + radius * self._sin(end_angle)
            
            # SVG path
            color = colors[i % len(colors)]
            path = f"""
                <path d="M {cx} {cy} L {start_x} {start_y} 
                         A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y} Z"
                      fill="{color}" 
                      stroke="white" 
                      stroke-width="2"/>
            """
            svg += path
            
            start_angle = end_angle
        
        svg += '</svg>'
        return svg
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], width: int = 400, height: int = 200) -> str:
        """
        막대 차트 생성
        
        Args:
            data: 데이터 딕셔너리
            width: 차트 너비
            height: 차트 높이
            
        Returns:
            막대 차트 HTML
        """
        if not data:
            return ""
        
        max_value = max(data.values()) if data.values() else 1
        bar_width = width // len(data) - 10
        
        html = f'<div class="bar-chart" style="display: flex; align-items: flex-end; height: {height}px; gap: 10px;">'
        
        for label, value in data.items():
            bar_height = (value / max_value) * height if max_value > 0 else 0
            html += f"""
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center;">
                    <div style="background: #007bff; width: {bar_width}px; height: {bar_height}px; 
                                border-radius: 4px 4px 0 0; transition: height 0.5s ease;">
                    </div>
                    <div style="margin-top: 5px; font-size: 0.8em; color: #6c757d;">{label}</div>
                    <div style="font-size: 0.9em; font-weight: bold;">{value:.0f}</div>
                </div>
            """
        
        html += '</div>'
        return html
    
    @staticmethod
    def _sin(degrees: float) -> float:
        """각도를 라디안으로 변환하여 sin 계산"""
        import math
        return math.sin(math.radians(degrees))
    
    @staticmethod
    def _cos(degrees: float) -> float:
        """각도를 라디안으로 변환하여 cos 계산"""
        import math
        return math.cos(math.radians(degrees))