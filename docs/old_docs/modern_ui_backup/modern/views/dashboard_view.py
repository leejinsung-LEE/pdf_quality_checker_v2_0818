# src/ui/modern/views/dashboard_view.py
"""
Modern 대시보드 뷰

Classic DashboardView와 동일한 기능을 제공하는 Modern 버전
"""

import flet as ft
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..app import ModernApp


class ModernDashboardView(ft.Container):
    """Modern 대시보드 뷰"""
    
    def __init__(self, app: 'ModernApp'):
        self.app = app
        
        super().__init__(
            expand=True,
            padding=30,
            content=self._build_content()
        )
        
    def _build_content(self):
        """대시보드 컨텐츠 생성"""
        # 헤더
        header = ft.Container(
            content=ft.Row([
                ft.Text("대시보드", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Container(expand=True),
                ft.IconButton(icon="refresh", icon_color="#FFFFFF", tooltip="새로고침"),
                ft.IconButton(icon="more_vert", icon_color="#FFFFFF", tooltip="옵션"),
            ]),
            padding=ft.padding.only(bottom=20),
        )
        
        # 통계 카드들
        stats_cards = ft.Row([
            self._create_stat_card("총 처리 파일", "0", "description", "#2196F3"),
            self._create_stat_card("성공률", "0%", "check_circle", "#4CAF50"),
            self._create_stat_card("평균 처리 시간", "0초", "schedule", "#FF9800"),
            self._create_stat_card("오류 발생", "0", "error", "#F44336"),
        ], wrap=True, spacing=20)
        
        # 차트 영역 (플레이스홀더)
        chart_area = ft.Container(
            content=ft.Column([
                ft.Text("처리 통계", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name="bar_chart", size=64, color="#444444"),
                        ft.Text("차트 영역", size=16, color="#888888"),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    height=300,
                    bgcolor="#2B2930",
                    border_radius=12,
                    alignment=ft.alignment.center,
                ),
            ]),
            expand=2,
        )
        
        # 최근 파일 리스트
        recent_files = ft.Container(
            content=ft.Column([
                ft.Text("최근 처리 파일", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Column([
                    self._create_file_item("샘플 파일 1.pdf", "성공", "방금 전"),
                    self._create_file_item("샘플 파일 2.pdf", "처리중", "5분 전"),
                    self._create_file_item("샘플 파일 3.pdf", "실패", "10분 전"),
                ], scroll=ft.ScrollMode.AUTO, height=300),
            ]),
            expand=1,
            padding=ft.padding.only(left=20),
        )
        
        # 메인 레이아웃
        return ft.Column([
            header,
            stats_cards,
            ft.Container(height=20),
            ft.Row([
                chart_area,
                recent_files,
            ], expand=True),
        ])
    
    def _create_stat_card(self, title: str, value: str, icon: str, color: str):
        """통계 카드 생성"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(name=icon, color=color, size=30),
                    ft.Container(width=10),
                    ft.Text(title, size=14, color="#CCCCCC"),
                ]),
                ft.Container(height=10),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Container(height=5),
                ft.Row([
                    ft.Icon(name="arrow_upward", color="#4CAF50", size=16),
                    ft.Text("변화 없음", size=12, color="#888888"),
                ]),
            ]),
            padding=20,
            width=250,
            height=140,
            bgcolor="#2B2930",
            border_radius=15,
        )
    
    def _create_file_item(self, name: str, status: str, time: str):
        """파일 아이템 생성"""
        status_config = {
            "성공": {"color": "#4CAF50", "icon": "check_circle"},
            "처리중": {"color": "#2196F3", "icon": "pending"},
            "실패": {"color": "#F44336", "icon": "error"}
        }
        
        config = status_config.get(status, {"color": "#888888", "icon": "help"})
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(name="picture_as_pdf", color="#F44336", size=24),
                ft.Container(width=10),
                ft.Column([
                    ft.Text(name, weight=ft.FontWeight.W_500, color="#FFFFFF"),
                    ft.Text(time, size=12, color="#888888"),
                ], expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(name=config["icon"], color="#FFFFFF", size=14),
                        ft.Text(status, size=12, color="#FFFFFF"),
                    ]),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=config["color"],
                    border_radius=10,
                ),
            ]),
            padding=15,
            bgcolor="#2B2930",
            border_radius=10,
            margin=ft.margin.only(bottom=10),
        )