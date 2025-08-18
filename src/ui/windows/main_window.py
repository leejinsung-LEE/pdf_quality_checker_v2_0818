# src/ui/windows/main_window.py
"""
메인 윈도우 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 main_window/ 디렉토리에 모듈화되어 있습니다.

최종 수정: 2025-01-12
Phase 3 모듈화 완료
"""

from .main_window import MainWindow

# 호환성을 위한 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # 원본에 있던 속성들을 직접 접근 가능하도록 매핑
    original_attrs = [
        'sidebar', 'menubar', 'statusbar', 'notebook',
        'views', 'current_view', 'folder_watchers', 'recent_files'
    ]
    
    # property 생성 함수
    def make_property(attr_name):
        def getter(self):
            # widgets 딕셔너리 확인
            if hasattr(self, 'widgets') and attr_name in self.widgets:
                return self.widgets[attr_name]
            # 직접 속성 확인
            if hasattr(self, attr_name):
                return getattr(self, attr_name)
            return None
        
        def setter(self, value):
            if hasattr(self, 'widgets'):
                self.widgets[attr_name] = value
            else:
                setattr(self, attr_name, value)
        
        return property(getter, setter)
    
    # 메서드 래핑 - 헬퍼 클래스 메서드를 메인 클래스에서 직접 호출 가능하도록
    method_mappings = {
        # ViewManager 메서드
        '_switch_tab': lambda self: self.view_manager.switch_tab,
        'toggle_sidebar': lambda self: self.view_manager.toggle_sidebar,
        'toggle_statusbar': lambda self: self.view_manager.toggle_statusbar,
        
        # FileManager 메서드
        'open_files': lambda self: self.file_manager.open_files,
        'open_folder': lambda self: self.file_manager.open_folder,
        'open_recent_files': lambda self: self.file_manager.open_recent_files,
        'process_files': lambda self: self.file_manager.process_files,
        '_load_recent_files': lambda self: self.file_manager.load_recent_files,
        '_save_recent_files': lambda self: self.file_manager.save_recent_files,
        '_add_recent_file': lambda self: self.file_manager.add_recent_file,
        
        # FolderWatcherManager 메서드
        'add_watch_folder': lambda self: self.folder_watcher_manager.add_watch_folder,
        'on_watched_file_found': lambda self: self.folder_watcher_manager.on_watched_file_found,
        'start_all_folder_watchers': lambda self: self.folder_watcher_manager.start_all_watchers,
        'stop_all_folder_watchers': lambda self: self.folder_watcher_manager.stop_all_watchers,
        '_update_folder_watch_status': lambda self: self.folder_watcher_manager._update_folder_watch_status,
        
        # DialogManager 메서드
        'show_preferences': lambda self: self.dialog_manager.show_preferences,
        'show_profile_manager': lambda self: self.dialog_manager.show_profile_manager,
        'show_batch_dialog': lambda self: self.dialog_manager.show_batch_dialog,
        'show_folder_watch_dialog': lambda self: self.dialog_manager.show_folder_watch_dialog,
        'show_batch_scheduler_dialog': lambda self: self.dialog_manager.show_batch_scheduler_dialog,
        'show_backup_manager_dialog': lambda self: self.dialog_manager.show_backup_manager_dialog,
        'export_current_report': lambda self: self.dialog_manager.export_current_report,
        
        # EventHandler 메서드
        'on_file_status_changed': lambda self: self.event_handler.on_file_status_changed,
        'on_file_progress': lambda self: self.event_handler.on_file_progress,
        'on_file_completed': lambda self: self.event_handler.on_file_completed,
        'on_file_error': lambda self: self.event_handler.on_file_error,
        'on_profile_change': lambda self: self.event_handler.on_profile_change,
        '_setup_menu_callbacks': lambda self: self.event_handler._setup_menu_callbacks,
        '_setup_sidebar_callbacks': lambda self: self.event_handler._setup_sidebar_callbacks,
        '_setup_controller_callbacks': lambda self: self.event_handler._setup_controller_callbacks,
        '_bind_shortcuts': lambda self: self.event_handler.bind_shortcuts,
        
        # UIBuilder 메서드
        '_create_ui': lambda self: self.ui_builder.create_ui,
        '_create_views': lambda self: self.ui_builder._create_views,
        '_setup_tab_style': lambda self: self.ui_builder._setup_tab_style,
        '_on_tab_changed': lambda self: self.ui_builder._on_tab_changed,
    }
    
    # 속성 매핑
    for attr in original_attrs:
        if not hasattr(MainWindow, attr):
            setattr(MainWindow, attr, make_property(attr))
    
    # 메서드 매핑
    for method_name, method_func in method_mappings.items():
        if not hasattr(MainWindow, method_name):
            setattr(MainWindow, method_name, 
                   lambda self, *args, method_func=method_func, **kwargs: 
                   method_func(self)(*args, **kwargs))

# 호환성 메서드 추가 실행
_add_compat_methods()

# 모든 공개 심볼 export
__all__ = ['MainWindow']