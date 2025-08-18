"""
현대적인 GUI 프로토타입 - Flet 버전
실시간으로 디자인을 확인할 수 있는 프로토타입

설치: pip install flet
실행: python modern_gui_preview.py
"""

import flet as ft
from datetime import datetime
import random

def main(page: ft.Page):
    # 페이지 설정
    page.title = "PDF Quality Checker - Modern UI"
    page.window_width = 1400
    page.window_height = 800
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    # Material 3 색상 테마
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#6750A4",  # Material You Purple
            primary_container="#EADDFF",
            secondary="#625B71",
            tertiary="#7D5260",
            surface="#1C1B1F",
            background="#1C1B1F",
            error="#F2B8B5",
        ),
        use_material3=True,
    )
    
    # 상태 관리
    processing_files = []
    
    # 사이드바 네비게이션 레일 (현대적 스타일)
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        bgcolor=ft.Colors.SURFACE_VARIANT,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.DASHBOARD_OUTLINED,
                selected_icon=ft.icons.DASHBOARD,
                label="대시보드",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.FOLDER_OUTLINED,
                selected_icon=ft.icons.FOLDER,
                label="파일 처리",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.HISTORY_OUTLINED,
                selected_icon=ft.icons.HISTORY,
                label="히스토리",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon=ft.icons.SETTINGS,
                label="설정",
            ),
        ],
    )
    
    # 대시보드 카드들 (Material 3 스타일)
    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(title, size=14, weight=ft.FontWeight.W_500),
                ]),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD),
                ft.Text("↑ 12% from last week", size=12, color=ft.Colors.GREEN),
            ]),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE_VARIANT,
            width=250,
            height=130,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=lambda e: setattr(e.control, "bgcolor", 
                ft.Colors.SECONDARY_CONTAINER if e.data == "true" else ft.Colors.SURFACE_VARIANT),
        )
    
    # 차트 컨테이너 (플레이스홀더)
    chart_container = ft.Container(
        content=ft.Column([
            ft.Text("처리 통계", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Text("📊 실시간 차트 영역", size=16),
                height=300,
                bgcolor=ft.Colors.SURFACE_VARIANT,
                border_radius=12,
                alignment=ft.alignment.center,
            )
        ]),
        padding=20,
    )
    
    # 최근 파일 리스트 (모던 카드 스타일)
    def create_file_item(filename, status, time):
        status_color = {
            "성공": ft.Colors.GREEN,
            "처리중": ft.Colors.BLUE,
            "실패": ft.Colors.RED,
        }.get(status, ft.Colors.GREY)
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.PICTURE_AS_PDF, color=ft.Colors.RED),
                ft.Column([
                    ft.Text(filename, weight=ft.FontWeight.W_500),
                    ft.Text(time, size=12, color=ft.Colors.GREY),
                ], expand=True),
                ft.Chip(
                    label=ft.Text(status, size=12),
                    bgcolor=status_color,
                    label_style=ft.TextStyle(color=ft.Colors.WHITE),
                ),
            ]),
            padding=15,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_VARIANT,
            margin=ft.margin.only(bottom=10),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=lambda e: setattr(e.control, "bgcolor", 
                ft.Colors.SECONDARY_CONTAINER if e.data == "true" else ft.Colors.SURFACE_VARIANT),
        )
    
    # 대시보드 뷰
    dashboard_view = ft.Column([
        # 헤더
        ft.Container(
            content=ft.Row([
                ft.Text("대시보드", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(ft.icons.NOTIFICATIONS_OUTLINED),
                ft.IconButton(ft.icons.PERSON_OUTLINED),
            ]),
            padding=20,
        ),
        
        # 통계 카드들
        ft.Row([
            create_stat_card("총 처리 파일", "1,234", ft.icons.FILE_COPY, ft.Colors.BLUE),
            create_stat_card("성공률", "98.5%", ft.icons.CHECK_CIRCLE, ft.Colors.GREEN),
            create_stat_card("평균 처리 시간", "2.3초", ft.icons.TIMER, ft.Colors.ORANGE),
            create_stat_card("오류 발생", "18", ft.icons.ERROR, ft.Colors.RED),
        ], wrap=True, spacing=20, run_spacing=20),
        
        # 차트와 최근 파일
        ft.Row([
            ft.Container(chart_container, expand=2),
            ft.Container(
                content=ft.Column([
                    ft.Text("최근 처리 파일", size=20, weight=ft.FontWeight.BOLD),
                    ft.Column([
                        create_file_item("report_2024.pdf", "성공", "2분 전"),
                        create_file_item("invoice_march.pdf", "처리중", "5분 전"),
                        create_file_item("presentation.pdf", "실패", "10분 전"),
                        create_file_item("manual_v2.pdf", "성공", "15분 전"),
                    ], scroll=ft.ScrollMode.AUTO, height=350),
                ]),
                padding=20,
                expand=1,
            ),
        ], expand=True),
    ])
    
    # 파일 처리 뷰 (드래그 앤 드롭 영역)
    def handle_file_drop(e):
        files = e.files if hasattr(e, 'files') else []
        for file in files:
            processing_files.append(file)
        page.update()
    
    file_drop_area = ft.Container(
        content=ft.Column([
            ft.Icon(ft.icons.CLOUD_UPLOAD, size=64, color=ft.Colors.BLUE),
            ft.Text("PDF 파일을 여기에 드래그하세요", size=18, weight=ft.FontWeight.W_500),
            ft.Text("또는", size=14, color=ft.Colors.GREY),
            ft.ElevatedButton(
                "파일 선택",
                icon=ft.icons.FOLDER_OPEN,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PRIMARY,
                ),
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        border=ft.border.all(2, ft.Colors.BLUE),
        border_radius=16,
        padding=60,
        bgcolor="#1E88E510",  # 반투명 파란색
        alignment=ft.alignment.center,
    )
    
    processing_view = ft.Column([
        ft.Container(
            content=ft.Text("파일 처리", size=28, weight=ft.FontWeight.BOLD),
            padding=20,
        ),
        ft.Container(
            content=file_drop_area,
            padding=20,
            expand=True,
        ),
    ])
    
    # 설정 뷰 (모던 스위치와 슬라이더)
    settings_view = ft.Column([
        ft.Container(
            content=ft.Text("설정", size=28, weight=ft.FontWeight.BOLD),
            padding=20,
        ),
        ft.Container(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.icons.DARK_MODE),
                    title=ft.Text("다크 모드"),
                    subtitle=ft.Text("어두운 테마 사용"),
                    trailing=ft.Switch(value=True),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.NOTIFICATIONS),
                    title=ft.Text("알림"),
                    subtitle=ft.Text("처리 완료 시 알림 받기"),
                    trailing=ft.Switch(value=True),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.IMAGE),
                    title=ft.Text("이미지 품질"),
                    subtitle=ft.Slider(
                        min=150, max=600, value=300,
                        label="{value} DPI",
                        width=200,
                    ),
                ),
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.COLOR_LENS),
                    title=ft.Text("테마 색상"),
                    subtitle=ft.Row([
                        ft.Container(width=30, height=30, bgcolor="#6750A4", border_radius=15),
                        ft.Container(width=30, height=30, bgcolor="#3F51B5", border_radius=15),
                        ft.Container(width=30, height=30, bgcolor="#4CAF50", border_radius=15),
                        ft.Container(width=30, height=30, bgcolor="#FF9800", border_radius=15),
                    ], spacing=10),
                ),
            ]),
            padding=20,
        ),
    ])
    
    # 뷰 전환 함수
    views = [dashboard_view, processing_view, dashboard_view, settings_view]
    
    def change_view(e):
        content_area.content = views[e.control.selected_index]
        page.update()
    
    rail.on_change = change_view
    
    # 컨텐츠 영역
    content_area = ft.Container(
        content=dashboard_view,
        expand=True,
        bgcolor=ft.Colors.BACKGROUND,
    )
    
    # FAB (플로팅 액션 버튼)
    fab = ft.FloatingActionButton(
        icon=ft.icons.ADD,
        bgcolor=ft.Colors.PRIMARY,
        tooltip="새 파일 추가",
    )
    
    # 레이아웃 구성
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1),
            content_area,
        ], expand=True)
    )
    
    # FAB 오버레이
    page.overlay.append(fab)
    page.update()

# 앱 실행
if __name__ == "__main__":
    ft.app(target=main)