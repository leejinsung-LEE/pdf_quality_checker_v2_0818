"""
메인 윈도우 모듈 (통합 버전)

애플리케이션의 메인 윈도우 관련 기능을 제공합니다.
파일 구조가 통합되어 더 효율적으로 관리됩니다.
"""

from .main_window import MainWindow
from .window_ui import UIBuilder, DialogManager
from .window_managers import FileManager, FolderWatcherManager

# MainWindow 초기화 헬퍼
def create_main_window():
    """메인 윈도우 생성 및 초기화"""
    window = MainWindow()
    
    # 헬퍼 클래스 생성
    ui_builder = UIBuilder(window)
    file_manager = FileManager(window)
    folder_watcher_manager = FolderWatcherManager(window)
    dialog_manager = DialogManager(window)
    
    # 헬퍼 클래스 설정
    window.set_helpers(ui_builder, file_manager, folder_watcher_manager, dialog_manager)
    
    return window

__all__ = ['MainWindow', 'create_main_window', 'UIBuilder', 'DialogManager', 
           'FileManager', 'FolderWatcherManager']