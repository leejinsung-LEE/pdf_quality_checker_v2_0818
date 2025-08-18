# src/ui/views/batch_process_view.py
"""
일괄 처리 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 batch_process/ 디렉토리에 모듈화되어 있습니다.

최종 수정: 2025-01-12
"""

from .batch_process import BatchProcessView

# 호환성을 위한 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # 원본에 있던 속성들을 직접 접근 가능하도록 매핑
    original_attrs = [
        # 트리뷰 및 UI 요소
        'file_tree', 'file_count_label', 'profile_combo',
        'output_entry', 'keep_structure', 'create_subfolders',
        'auto_fix', 'generate_report', 'stop_on_error',
        'progress_bar', 'status_label', 'start_btn', 'cancel_btn',
        # 버튼들
        'add_files_btn', 'add_folder_btn', 'clear_btn'
    ]
    
    # 속성 접근자 생성
    def make_property(attr_name):
        def getter(self):
            # widgets 딕셔너리에서 먼저 찾기
            if hasattr(self, 'widgets') and attr_name in self.widgets:
                return self.widgets[attr_name]
            # 직접 속성에서 찾기
            if hasattr(self, f'_{attr_name}'):
                return getattr(self, f'_{attr_name}')
            # 기본 속성 확인
            if hasattr(self, attr_name):
                return getattr(self, attr_name)
            return None
            
        def setter(self, value):
            if hasattr(self, 'widgets'):
                self.widgets[attr_name] = value
            else:
                setattr(self, f'_{attr_name}', value)
                
        return property(getter, setter)
    
    # 모든 속성에 대해 property 생성
    for attr in original_attrs:
        if not hasattr(BatchProcessView, attr):
            setattr(BatchProcessView, attr, make_property(attr))
    
    # 원본에 있던 private 메서드들 매핑
    original_methods = [
        '_create_ui', '_add_files', '_add_folder', '_clear_list',
        '_update_file_list', '_browse_output', '_start_process',
        '_process_files', '_cancel_process', '_monitor_queue',
        '_on_process_complete', '_on_process_cancelled', '_reset_ui',
        '_on_closing'
    ]
    
    def make_method_wrapper(method_name):
        def wrapper(self, *args, **kwargs):
            # 적절한 헬퍼에서 메서드 찾기
            if method_name == '_create_ui':
                if hasattr(self, 'ui_builder'):
                    return self.ui_builder.create_ui(*args, **kwargs)
            elif method_name in ['_add_files', '_add_folder', '_clear_list', '_update_file_list', '_browse_output']:
                if hasattr(self, 'file_manager'):
                    method = method_name.lstrip('_')
                    if hasattr(self.file_manager, method):
                        return getattr(self.file_manager, method)(*args, **kwargs)
            elif method_name in ['_start_process', '_process_files', '_cancel_process']:
                if hasattr(self, 'process_handler'):
                    method = method_name.lstrip('_')
                    if hasattr(self.process_handler, method):
                        return getattr(self.process_handler, method)(*args, **kwargs)
            elif method_name in ['_monitor_queue', '_on_process_complete', '_on_process_cancelled', '_reset_ui']:
                if hasattr(self, 'progress_monitor'):
                    method = method_name.lstrip('_')
                    if hasattr(self.progress_monitor, method):
                        return getattr(self.progress_monitor, method)(*args, **kwargs)
            # 기본 메서드 확인
            elif hasattr(self, method_name.lstrip('_')):
                return getattr(self, method_name.lstrip('_'))(*args, **kwargs)
            return None
        return wrapper
    
    # 메서드 매핑
    for method in original_methods:
        if not hasattr(BatchProcessView, method):
            setattr(BatchProcessView, method, make_method_wrapper(method))

_add_compat_methods()

__all__ = ['BatchProcessView']