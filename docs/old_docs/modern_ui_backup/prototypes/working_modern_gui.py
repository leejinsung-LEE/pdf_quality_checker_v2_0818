"""
현대적인 GUI 프로토타입 - 작동 버전
Flet 최신 API 호환
"""

import flet as ft

def main(page: ft.Page):
    # 페이지 기본 설정
    page.title = "PDF Quality Checker - Modern UI"
    page.window_width = 1400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    
    # 색상 정의
    PRIMARY = "#6750A4"
    SURFACE = "#2B2930"
    BACKGROUND = "#1C1B1F"
    SUCCESS = "#4CAF50"
    ERROR = "#F44336"
    INFO = "#2196F3"
    WARNING = "#FF9800"
    
    # 사이드바 메뉴 아이템
    def create_menu_item(icon_name, label, selected=False):
        return ft.Container(
            content=ft.Row([
                ft.Icon(name=icon_name, color="#FFFFFF" if selected else "#888888"),
                ft.Text(label, color="#FFFFFF" if selected else "#888888", size=16)
            ]),
            padding=15,
            bgcolor=PRIMARY if selected else None,
            border_radius=10,
        )
    
    # 사이드바
    sidebar = ft.Container(
        content=ft.Column([
            ft.Text("📄 PDF Quality Checker", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            ft.Divider(height=30, color="#444444"),
            create_menu_item("dashboard", "대시보드", True),
            create_menu_item("folder", "파일 처리"),
            create_menu_item("history", "히스토리"),
            create_menu_item("settings", "설정"),
        ]),
        width=250,
        bgcolor=SURFACE,
        padding=20,
    )
    
    # 통계 카드
    def create_stat_card(title, value, icon, color):
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
                    ft.Icon(name="arrow_upward", color=SUCCESS, size=16),
                    ft.Text("12% 증가", size=12, color=SUCCESS),
                ]),
            ]),
            padding=20,
            width=250,
            height=140,
            bgcolor=SURFACE,
            border_radius=15,
        )
    
    # 파일 아이템
    def create_file_item(name, status, time):
        status_config = {
            "성공": {"color": SUCCESS, "icon": "check_circle"},
            "처리중": {"color": INFO, "icon": "pending"},
            "실패": {"color": ERROR, "icon": "error"}
        }
        
        config = status_config.get(status, {"color": "#888888", "icon": "help"})
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(name="picture_as_pdf", color=ERROR, size=24),
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
            bgcolor=SURFACE,
            border_radius=10,
            margin=ft.margin.only(bottom=10),
        )
    
    # 드래그 앤 드롭 영역
    drop_area = ft.Container(
        content=ft.Column([
            ft.Icon(name="cloud_upload", color=INFO, size=64),
            ft.Container(height=20),
            ft.Text("PDF 파일을 여기에 드래그하세요", size=18, color="#FFFFFF"),
            ft.Container(height=10),
            ft.Text("또는", size=14, color="#888888"),
            ft.Container(height=10),
            ft.ElevatedButton(
                "파일 선택",
                icon="folder_open",
                bgcolor=PRIMARY,
                color="#FFFFFF",
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        border=ft.border.all(2, INFO),
        border_radius=16,
        padding=60,
        bgcolor="#1E88E510",
        alignment=ft.alignment.center,
        height=300,
    )
    
    # 메인 컨텐츠 영역
    main_content = ft.Container(
        content=ft.Column([
            # 헤더
            ft.Container(
                content=ft.Row([
                    ft.Text("대시보드", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Container(expand=True),
                    ft.IconButton(icon="notifications", icon_color="#FFFFFF"),
                    ft.IconButton(icon="person", icon_color="#FFFFFF"),
                ]),
                padding=20,
            ),
            
            # 통계 카드들
            ft.Container(
                content=ft.Row([
                    create_stat_card("총 처리 파일", "1,234", "description", INFO),
                    create_stat_card("성공률", "98.5%", "check_circle", SUCCESS),
                    create_stat_card("평균 시간", "2.3초", "schedule", WARNING),
                    create_stat_card("오류", "18", "error", ERROR),
                ], wrap=True, spacing=20),
                padding=ft.padding.symmetric(horizontal=20),
            ),
            
            ft.Container(height=20),
            
            # 차트와 파일 리스트
            ft.Container(
                content=ft.Row([
                    # 왼쪽: 드래그 앤 드롭
                    ft.Container(
                        content=ft.Column([
                            ft.Text("파일 처리", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            ft.Container(height=10),
                            drop_area,
                        ]),
                        expand=2,
                        padding=20,
                    ),
                    
                    # 오른쪽: 최근 파일
                    ft.Container(
                        content=ft.Column([
                            ft.Text("최근 처리 파일", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            ft.Container(height=10),
                            ft.Column([
                                create_file_item("report_2024.pdf", "성공", "2분 전"),
                                create_file_item("invoice_march.pdf", "처리중", "5분 전"),
                                create_file_item("presentation.pdf", "실패", "10분 전"),
                                create_file_item("manual_v2.pdf", "성공", "15분 전"),
                            ], scroll=ft.ScrollMode.AUTO, height=300),
                        ]),
                        expand=1,
                        padding=20,
                    ),
                ], expand=True),
                expand=True,
            ),
        ]),
        expand=True,
        bgcolor=BACKGROUND,
    )
    
    # 플로팅 액션 버튼
    fab = ft.FloatingActionButton(
        icon="add",
        bgcolor=PRIMARY,
        tooltip="새 파일 추가",
    )
    
    # 전체 레이아웃
    page.add(
        ft.Row([
            sidebar,
            ft.VerticalDivider(width=1, color="#444444"),
            main_content,
        ], expand=True)
    )
    
    # FAB 추가
    page.overlay.append(fab)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)