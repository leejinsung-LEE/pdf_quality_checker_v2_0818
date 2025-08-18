"""
심플하고 현대적인 GUI 프로토타입
Flet 최신 버전 호환
"""

import flet as ft

def main(page: ft.Page):
    # 페이지 기본 설정
    page.title = "PDF Quality Checker - Modern UI"
    page.window_width = 1400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    
    # 색상 정의 (간단한 색상만 사용)
    PRIMARY = "#6750A4"
    SURFACE = "#2B2930"
    BACKGROUND = "#1C1B1F"
    
    # 사이드바 메뉴
    def create_menu_item(icon, label, selected=False):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color="#FFFFFF" if selected else "#888888"),
                ft.Text(label, color="#FFFFFF" if selected else "#888888", size=16)
            ]),
            padding=15,
            bgcolor=PRIMARY if selected else None,
            border_radius=10,
            on_click=lambda e: print(f"클릭: {label}"),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
    
    sidebar = ft.Container(
        content=ft.Column([
            ft.Text("PDF Quality Checker", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=30, color="#444444"),
            create_menu_item(ft.Icons.DASHBOARD, "대시보드", True),
            create_menu_item(ft.Icons.FOLDER, "파일 처리"),
            create_menu_item(ft.Icons.HISTORY, "히스토리"),
            create_menu_item(ft.Icons.SETTINGS, "설정"),
        ]),
        width=250,
        bgcolor=SURFACE,
        padding=20,
    )
    
    # 통계 카드 생성
    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(title, size=14),
                ]),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD),
                ft.Text("↑ 12%", size=12, color="#4CAF50"),
            ]),
            padding=20,
            width=250,
            height=130,
            bgcolor=SURFACE,
            border_radius=15,
        )
    
    # 파일 아이템
    def create_file_item(name, status, time):
        status_colors = {
            "성공": "#4CAF50",
            "처리중": "#2196F3", 
            "실패": "#F44336"
        }
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, color="#F44336"),
                ft.Column([
                    ft.Text(name, weight=ft.FontWeight.W_500),
                    ft.Text(time, size=12, color="#888888"),
                ], expand=True),
                ft.Container(
                    content=ft.Text(status, size=12, color="#FFFFFF"),
                    padding=ft.padding.symmetric(8, 4),
                    bgcolor=status_colors.get(status, "#888888"),
                    border_radius=10,
                ),
            ]),
            padding=15,
            bgcolor=SURFACE,
            border_radius=10,
            margin=ft.margin.only(bottom=10),
        )
    
    # 메인 컨텐츠
    main_content = ft.Container(
        content=ft.Column([
            # 헤더
            ft.Container(
                content=ft.Row([
                    ft.Text("대시보드", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(ft.Icons.NOTIFICATIONS),
                    ft.IconButton(ft.Icons.PERSON),
                ]),
                padding=20,
            ),
            
            # 통계 카드들
            ft.Container(
                content=ft.Row([
                    create_stat_card("총 처리 파일", "1,234", ft.Icons.FILE_COPY, "#2196F3"),
                    create_stat_card("성공률", "98.5%", ft.Icons.CHECK_CIRCLE, "#4CAF50"),
                    create_stat_card("평균 시간", "2.3초", ft.Icons.TIMER, "#FF9800"),
                    create_stat_card("오류", "18", ft.Icons.ERROR, "#F44336"),
                ], wrap=True, spacing=20),
                padding=ft.padding.symmetric(20, 0),
            ),
            
            # 차트와 파일 리스트
            ft.Container(
                content=ft.Row([
                    # 차트 영역
                    ft.Container(
                        content=ft.Column([
                            ft.Text("처리 통계", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text("📊 차트 영역", size=16),
                                height=250,
                                bgcolor=SURFACE,
                                border_radius=10,
                                alignment=ft.alignment.center,
                            ),
                        ]),
                        expand=2,
                        padding=20,
                    ),
                    
                    # 최근 파일
                    ft.Container(
                        content=ft.Column([
                            ft.Text("최근 처리 파일", size=20, weight=ft.FontWeight.BOLD),
                            ft.Column([
                                create_file_item("report_2024.pdf", "성공", "2분 전"),
                                create_file_item("invoice.pdf", "처리중", "5분 전"),
                                create_file_item("manual.pdf", "실패", "10분 전"),
                            ]),
                        ]),
                        expand=1,
                        padding=20,
                    ),
                ]),
                expand=True,
            ),
        ]),
        expand=True,
        bgcolor=BACKGROUND,
    )
    
    # 플로팅 액션 버튼
    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=PRIMARY,
    )
    
    # 레이아웃 구성
    page.add(
        ft.Row([
            sidebar,
            main_content,
        ], expand=True)
    )
    
    page.overlay.append(fab)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)