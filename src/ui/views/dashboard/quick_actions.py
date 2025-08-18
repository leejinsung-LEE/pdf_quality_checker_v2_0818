"""
빠른 액션 빌더
기능: 헤더, 액션 버튼, 보고서 생성 등 빠른 작업 관리
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING, Dict, Any
from tkinter import filedialog
from datetime import datetime
import customtkinter as ctk
import json
import webbrowser

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import DashboardView


class QuickActionsBuilder:
    """
    빠른 액션 빌더
    
    역할:
    - 헤더 생성
    - 기간 선택
    - 보고서 생성
    - 텍스트 통계 표시
    """
    
    def __init__(self, view: 'DashboardView'):
        """
        빌더 초기화
        
        Args:
            view: 메인 대시보드 뷰
        """
        self.view = view
    
    def create_header(self, parent) -> ctk.CTkFrame:
        """헤더 생성"""
        header = ctk.CTkFrame(parent, fg_color="transparent", height=50)
        
        # 제목
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side='left', fill='y')
        
        ctk.CTkLabel(
            title_frame,
            text="📊 대시보드",
            font=('Arial', 24, 'bold')
        ).pack(side='left')
        
        ctk.CTkLabel(
            title_frame,
            text="PDF 처리 통계 및 분석",
            font=('Arial', 12),
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(20, 0))
        
        # 기간 선택
        period_frame = ctk.CTkFrame(header, fg_color="transparent")
        period_frame.pack(side='right', fill='y')
        
        periods = [
            ("오늘", "today"),
            ("이번 주", "week"),
            ("이번 달", "month"),
            ("전체", "all")
        ]
        
        for text, value in periods:
            btn = ctk.CTkRadioButton(
                period_frame,
                text=text,
                variable=self.view.period_var,
                value=value,
                command=self.view.refresh_data,
                width=80
            )
            btn.pack(side='left', padx=5)
        
        # 새로고침 버튼
        ctk.CTkButton(
            period_frame,
            text="🔄",
            width=40,
            height=32,
            command=self.view.refresh_data
        ).pack(side='left', padx=(20, 0))
        
        # 보고서 생성 버튼
        ctk.CTkButton(
            period_frame,
            text="📄 보고서",
            width=80,
            height=32,
            command=self.generate_report,
            fg_color=self.view.colors['bg_secondary']
        ).pack(side='left', padx=(10, 0))
        
        return header
    
    def generate_report(self):
        """통계 보고서 생성"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML 파일", "*.html"), ("JSON 파일", "*.json"), ("모든 파일", "*.*")],
            initialfile=f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        if filename:
            # 현재 통계 데이터
            date_range = self.view.calculate_date_range(self.view.period_var.get())
            stats = self.view.stats_manager.get_statistics(date_range)
            
            if filename.endswith('.json'):
                # JSON 형식으로 저장
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
            else:
                # HTML 형식으로 저장
                self._generate_html_report(filename, stats)
            
            # 생성된 파일 열기
            webbrowser.open(filename)
    
    def _generate_html_report(self, filename: str, stats: Dict[str, Any]):
        """HTML 보고서 생성"""
        basic = stats.get('basic', {})
        
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>PDF 처리 통계 보고서</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        .stat-card {{ display: inline-block; margin: 10px; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF 처리 통계 보고서</h1>
        <p>생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>기간: {self.view.period_var.get()}</p>
        
        <h2>기본 통계</h2>
        <div>
            <div class="stat-card">
                <div class="stat-value">{basic.get('total_files', 0)}</div>
                <div class="stat-label">총 처리 파일</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{basic.get('success_count', 0)}</div>
                <div class="stat-label">성공</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{basic.get('total_errors', 0)}</div>
                <div class="stat-label">오류</div>
            </div>
        </div>
        
        <h2>일별 처리량</h2>
        <table>
            <tr><th>날짜</th><th>파일 수</th><th>페이지 수</th></tr>
"""
        
        for daily in stats.get('daily', []):
            html += f"<tr><td>{daily['date']}</td><td>{daily['files']}</td><td>{daily.get('pages', 0)}</td></tr>"
        
        html += """
        </table>
    </div>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def update_text_stats(self, stats: Dict[str, Any]):
        """텍스트 통계 업데이트 (matplotlib 없을 때)"""
        if not self.view.stats_text:
            return
        
        basic = stats.get('basic', {})
        
        text = f"""
PDF 처리 통계 요약 ({self.view.period_var.get()})
{'='*50}

📊 기본 통계
  • 총 처리 파일: {basic.get('total_files', 0)}개
  • 성공: {basic.get('success_count', 0)}개
  • 오류: {basic.get('total_errors', 0)}개
  • 경고: {basic.get('total_warnings', 0)}개
  • 자동 수정: {basic.get('auto_fixed_count', 0)}개

⏱️ 성능
  • 평균 처리 시간: {basic.get('avg_processing_time', 0):.1f}초
  • 총 페이지: {basic.get('total_pages', 0)}페이지

📅 일별 처리량
"""
        
        # 일별 데이터
        for daily in stats.get('daily', []):
            text += f"  • {daily['date']}: {daily['files']}개 파일\n"
        
        text += "\n❗ 주요 문제 유형\n"
        
        # 문제 유형
        for i, issue in enumerate(stats.get('common_issues', [])[:5], 1):
            text += f"  {i}. {issue['type']}: {issue['count']}회 발생\n"
        
        self.view.stats_text.delete('1.0', 'end')
        self.view.stats_text.insert('1.0', text)