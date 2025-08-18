"""
뷰 매니저 - 뷰 전환 및 관리
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import MainWindow


class ViewManager:
    """뷰 매니저"""
    
    def __init__(self, window: 'MainWindow'):
        self.window = window
    
    def on_tab_changed(self, selected_tab: int):
        """탭 변경 이벤트 처리"""
        # 탭별 새로고침
        if selected_tab == 0:  # 통합 처리 탭
            self.window.current_view = 'unified_processing'
            if 'unified_processing' in self.window.views:
                self.window.views['unified_processing'].refresh()
                
        elif selected_tab == 1:  # 대시보드 탭
            self.window.current_view = 'dashboard'
            if 'dashboard' in self.window.views:
                self.window.views['dashboard'].update_statistics()
                
        elif selected_tab == 2:  # 통계 분석 탭
            self.window.current_view = 'statistics'
            if 'statistics' in self.window.views:
                self.window.views['statistics'].refresh_data()
                
        elif selected_tab == 3:  # 프로파일 설정 탭
            self.window.current_view = 'profile_settings'
            if 'profile_settings' in self.window.views:
                self.window.views['profile_settings'].load_profile_list()
    
    def switch_tab(self, view_name: str):
        """뷰 이름으로 탭 전환"""
        tab_index = {
            'unified_processing': 0,
            'dashboard': 1,
            'statistics': 2,
            'profile_settings': 3
        }
        
        if view_name in tab_index:
            if hasattr(self.window, 'notebook'):
                self.window.notebook.select(tab_index[view_name])
                
                # 뷰별 새로고침
                if view_name == 'dashboard' and 'dashboard' in self.window.views:
                    self.window.views['dashboard'].refresh_data()
                elif view_name == 'unified_processing' and 'unified_processing' in self.window.views:
                    self.window.views['unified_processing'].refresh()
                elif view_name == 'statistics' and 'statistics' in self.window.views:
                    self.window.views['statistics'].refresh_data()
                elif view_name == 'profile_settings' and 'profile_settings' in self.window.views:
                    self.window.views['profile_settings'].load_profile_list()
    
    def toggle_sidebar(self):
        """사이드바 토글"""
        if hasattr(self.window, 'sidebar'):
            if self.window.sidebar.winfo_viewable():
                self.window.sidebar.pack_forget()
            else:
                main_container = self.window.widgets.get('main_container')
                if main_container:
                    self.window.sidebar.pack(side='left', fill='y', 
                                            before=self.window.widgets.get('content_container'))
    
    def toggle_statusbar(self):
        """상태바 토글"""
        if hasattr(self.window, 'statusbar'):
            if self.window.statusbar.winfo_viewable():
                self.window.statusbar.pack_forget()
            else:
                content_container = self.window.widgets.get('content_container')
                if content_container:
                    self.window.statusbar.pack(side='bottom', fill='x')
    
    def refresh_current_view(self):
        """현재 뷰 새로고침"""
        if self.window.current_view == 'unified_processing':
            if 'unified_processing' in self.window.views:
                self.window.views['unified_processing'].refresh()
        elif self.window.current_view == 'dashboard':
            if 'dashboard' in self.window.views:
                self.window.views['dashboard'].update_statistics()
        elif self.window.current_view == 'statistics':
            if 'statistics' in self.window.views:
                self.window.views['statistics'].refresh_data()
        elif self.window.current_view == 'profile_settings':
            if 'profile_settings' in self.window.views:
                self.window.views['profile_settings'].load_profile_list()
    
    def get_current_view(self):
        """현재 활성 뷰 반환"""
        return self.window.views.get(self.window.current_view)
    
    def update_all_views(self):
        """모든 뷰 업데이트"""
        for view_name, view in self.window.views.items():
            if hasattr(view, 'refresh'):
                view.refresh()
            elif hasattr(view, 'update_statistics'):
                view.update_statistics()
            elif hasattr(view, 'refresh_data'):
                view.refresh_data()
            elif hasattr(view, 'load_profile_list'):
                view.load_profile_list()