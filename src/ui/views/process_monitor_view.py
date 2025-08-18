# src/ui/views/process_monitor_view.py
"""
통합 처리 모니터 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 process_monitor/ 디렉토리에 모듈화되어 있습니다.

최종 수정: 2025-01-12
"""

from .process_monitor import ProcessMonitorView

# 호환성을 위한 상수 및 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # 원본에 있던 상수들
    if not hasattr(ProcessMonitorView, 'STATUS_ICONS'):
        from ..controllers import FileStatus
        ProcessMonitorView.STATUS_ICONS = {
            FileStatus.WAITING: '⏳',
            FileStatus.PROCESSING: '⚙️',
            FileStatus.COMPLETED: '✅',
            FileStatus.ERROR: '❌',
            FileStatus.CANCELLED: '🚫'
        }
    
    if not hasattr(ProcessMonitorView, 'STATUS_TAGS'):
        from ..controllers import FileStatus
        ProcessMonitorView.STATUS_TAGS = {
            FileStatus.WAITING: 'waiting',
            FileStatus.PROCESSING: 'processing',
            FileStatus.COMPLETED: 'success',
            FileStatus.ERROR: 'error',
            FileStatus.CANCELLED: 'cancelled'
        }
    
    # 원본에 있던 속성들을 직접 접근 가능하도록 매핑
    original_attrs = [
        # 트리뷰 관련
        'current_tree', 'history_tree',
        # 버튼 관련
        'pause_button', 'cancel_button', 'retry_button', 
        'clear_completed_button', 'export_button',
        # 필터 관련
        'search_entry', 'status_menu', 'folder_menu',
        'date_menu', 'profile_menu',
        # 레이블 관련
        'stats_labels', 'selection_label', 'total_label',
        'page_label', 'prev_button', 'next_button',
        # 프레임 관련
        'current_frame', 'history_frame', 'custom_date_frame'
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
        if not hasattr(ProcessMonitorView, attr):
            setattr(ProcessMonitorView, attr, make_property(attr))
    
    # 원본에 있던 private 메서드들 매핑
    original_methods = [
        '_create_ui', '_create_header', '_create_stats_section',
        '_create_current_section', '_create_history_section',
        '_create_bottom_controls', '_update_stats', '_refresh_current_view',
        '_update_table', '_update_history_table', '_update_ui_state',
        '_calculate_date_range', '_get_status_text', '_format_time',
        '_start_auto_refresh', '_stop_auto_refresh'
    ]
    
    def make_method_wrapper(method_name):
        def wrapper(self, *args, **kwargs):
            # 적절한 헬퍼에서 메서드 찾기
            if hasattr(self, 'ui_builder') and hasattr(self.ui_builder, method_name):
                return getattr(self.ui_builder, method_name)(*args, **kwargs)
            elif hasattr(self, 'tree_handler') and hasattr(self.tree_handler, method_name):
                return getattr(self.tree_handler, method_name)(*args, **kwargs)
            elif hasattr(self, 'event_handler') and hasattr(self.event_handler, method_name):
                return getattr(self.event_handler, method_name)(*args, **kwargs)
            elif hasattr(self, 'action_handler') and hasattr(self.action_handler, method_name):
                return getattr(self.action_handler, method_name)(*args, **kwargs)
            # 기본 메서드 확인
            elif hasattr(self, method_name.lstrip('_')):
                return getattr(self, method_name.lstrip('_'))(*args, **kwargs)
            return None
        return wrapper
    
    # 메서드 매핑
    for method in original_methods:
        if not hasattr(ProcessMonitorView, method):
            setattr(ProcessMonitorView, method, make_method_wrapper(method))
    
    # 이벤트 핸들러 메서드 매핑
    event_methods = [
        'on_selection_change', 'on_history_selection_change',
        'on_tree_double_click', 'on_history_double_click',
        'on_search_change', 'on_filter_change', 'on_date_change',
        'pause_selected', 'cancel_selected', 'retry_selected',
        'clear_completed', 'export_results', 'show_details',
        'refresh_data', 'apply_filters'
    ]
    
    def make_event_wrapper(method_name):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'event_handler') and hasattr(self.event_handler, method_name):
                return getattr(self.event_handler, method_name)(*args, **kwargs)
            elif hasattr(self, 'tree_handler') and hasattr(self.tree_handler, method_name):
                return getattr(self.tree_handler, method_name)(*args, **kwargs)
            elif hasattr(self, 'action_handler') and hasattr(self.action_handler, method_name):
                return getattr(self.action_handler, method_name)(*args, **kwargs)
            return None
        return wrapper
    
    for method in event_methods:
        if not hasattr(ProcessMonitorView, method):
            setattr(ProcessMonitorView, method, make_event_wrapper(method))

_add_compat_methods()

__all__ = ['ProcessMonitorView']