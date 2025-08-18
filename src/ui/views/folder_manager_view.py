# src/ui/views/folder_manager_view.py
"""
폴더 관리 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 folder_manager/ 디렉토리에 모듈화되어 있습니다.

최종 수정: 2025-01-12
Phase 3-D 모듈화 완료
"""

from .folder_manager import FolderManagerView

# 호환성을 위한 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # 원본에 있던 private 메서드들 매핑
    method_mappings = {
        # UIBuilder 메서드
        '_create_ui': lambda self: self.ui_builder.create_ui,
        '_create_basic_settings': lambda self: self.ui_builder._create_basic_settings,
        '_create_check_settings': lambda self: self.ui_builder._create_check_settings,
        '_create_fix_settings': lambda self: self.ui_builder._create_fix_settings,
        '_create_report_settings': lambda self: self.ui_builder._create_report_settings,
        
        # FolderListManager 메서드
        '_load_folders': lambda self: self.folder_list_manager.load_folders,
        '_on_folder_select': lambda self: self.on_folder_select,
        
        # SettingsManager 메서드
        '_load_folder_settings': lambda self: self.settings_manager.load_folder_settings,
        '_save_settings': lambda self: self.save_settings,
        '_toggle_report_formats': lambda self: self.toggle_report_formats,
        
        # EventHandler 메서드
        '_add_folder': lambda self: self.add_folder,
        '_remove_folder': lambda self: self.remove_folder,
        '_browse_output_folder': lambda self: self.browse_output_folder,
    }
    
    # 메서드 매핑 적용
    for method_name, method_func in method_mappings.items():
        if not hasattr(FolderManagerView, method_name):
            setattr(FolderManagerView, method_name,
                   lambda self, *args, method_func=method_func, **kwargs:
                   method_func(self)(*args, **kwargs))

# 호환성 메서드 추가 실행
_add_compat_methods()

# 모든 공개 심볼 export
__all__ = ['FolderManagerView']