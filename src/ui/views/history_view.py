# src/ui/views/history_view.py
"""
처리 이력 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 history/ 디렉토리에 모듈화되어 있습니다.

최종 수정: 2025-01-12
"""

from .history import HistoryView

# 호환성을 위한 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # 원본에 있던 속성들을 직접 접근 가능하도록 매핑
    original_attrs = [
        'tree', 'search_entry', 'date_menu', 'custom_date_frame',
        'status_menu', 'profile_menu', 'empty_label',
        'delete_button', 'selection_label', 'total_label',
        'prev_button', 'page_label', 'next_button'
    ]
    
    # 속성 접근자 생성
    def make_property(attr_name):
        def getter(self):
            # widgets 딕셔너리에서 찾기
            if hasattr(self, 'widgets') and attr_name in self.widgets:
                return self.widgets[attr_name]
            # 직접 속성에서 찾기
            if hasattr(self, f'_{attr_name}'):
                return getattr(self, f'_{attr_name}')
            return None
            
        def setter(self, value):
            if hasattr(self, 'widgets'):
                self.widgets[attr_name] = value
            else:
                setattr(self, f'_{attr_name}', value)
                
        return property(getter, setter)
    
    # 모든 속성에 대해 property 생성
    for attr in original_attrs:
        if not hasattr(HistoryView, attr):
            setattr(HistoryView, attr, make_property(attr))
    
    # 원본에 있던 private 메서드들 매핑
    original_methods = [
        '_create_ui', '_create_header', '_create_filter_section',
        '_create_table_section', '_create_bottom_controls',
        '_update_table', '_update_ui_state', '_update_selection_info',
        '_update_profile_filter', '_calculate_date_range', '_get_status_text'
    ]
    
    def make_method_wrapper(method_name):
        def wrapper(self, *args, **kwargs):
            # 적절한 헬퍼에서 메서드 찾기
            if method_name == '_update_table':
                if hasattr(self, 'list_manager'):
                    return self.list_manager.update_table(*args, **kwargs)
            elif method_name == '_update_ui_state':
                if hasattr(self, 'list_manager'):
                    return self.list_manager.update_ui_state(*args, **kwargs)
            elif method_name == '_update_selection_info':
                if hasattr(self, 'list_manager'):
                    return self.list_manager.update_selection_info(*args, **kwargs)
            elif method_name == '_update_profile_filter':
                if hasattr(self, 'filter_manager'):
                    return self.filter_manager.update_profile_filter(*args, **kwargs)
            elif method_name == '_calculate_date_range':
                if hasattr(self, 'filter_manager'):
                    return self.filter_manager.calculate_date_range(*args, **kwargs)
            elif method_name == '_get_status_text':
                if hasattr(self, 'list_manager'):
                    return self.list_manager._get_status_text(*args, **kwargs)
            # UI 빌더 메서드들
            elif method_name.startswith('_create_'):
                if hasattr(self, 'ui_builder'):
                    if hasattr(self.ui_builder, method_name):
                        return getattr(self.ui_builder, method_name)(*args, **kwargs)
            return None
        return wrapper
    
    # 메서드 매핑
    for method in original_methods:
        if not hasattr(HistoryView, method):
            setattr(HistoryView, method, make_method_wrapper(method))
    
    # 이벤트 핸들러 메서드 매핑
    event_methods = [
        'on_tree_click', 'on_tree_double_click', 'on_date_range_change',
        'on_per_page_change', 'show_date_picker'
    ]
    
    def make_event_wrapper(method_name):
        def wrapper(self, *args, **kwargs):
            if method_name in ['on_tree_click', 'on_tree_double_click']:
                if hasattr(self, 'list_manager'):
                    return getattr(self.list_manager, method_name)(*args, **kwargs)
            else:
                if hasattr(self, 'event_handler'):
                    return getattr(self.event_handler, method_name)(*args, **kwargs)
            return None
        return wrapper
    
    for method in event_methods:
        if not hasattr(HistoryView, method):
            setattr(HistoryView, method, make_event_wrapper(method))

_add_compat_methods()

__all__ = ['HistoryView']