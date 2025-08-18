# src/ui/events/event_types.py
"""
이벤트 타입 정의

애플리케이션 전체에서 사용되는 이벤트 타입을 중앙에서 관리합니다.
"""

from enum import Enum


class EventType(Enum):
    """이벤트 타입 열거형"""
    
    # === 파일 관련 이벤트 ===
    FILE_OPEN = "file.open"
    FILE_OPEN_FOLDER = "file.open_folder"
    FILE_DROPPED = "file.dropped"
    FILE_PROCESSING_START = "file.processing.start"
    FILE_PROCESSING_PROGRESS = "file.processing.progress"
    FILE_PROCESSING_COMPLETE = "file.processing.complete"
    FILE_PROCESSING_ERROR = "file.processing.error"
    FILE_RECENT_OPEN = "file.recent.open"
    FILE_RECENT_CLEAR = "file.recent.clear"
    
    # === 프로파일 관련 이벤트 ===
    PROFILE_CHANGED = "profile.changed"
    PROFILE_CREATED = "profile.created"
    PROFILE_UPDATED = "profile.updated"
    PROFILE_DELETED = "profile.deleted"
    PROFILE_LOADED = "profile.loaded"
    PROFILE_SAVED = "profile.saved"
    
    # === UI 관련 이벤트 ===
    VIEW_CHANGED = "view.changed"
    VIEW_PROCESSING = "view.processing"
    VIEW_DASHBOARD = "view.dashboard"
    VIEW_STATISTICS = "view.statistics"
    VIEW_PROFILE_SETTINGS = "view.profile_settings"
    VIEW_HISTORY = "view.history"
    
    # === UI 토글 이벤트 ===
    SIDEBAR_TOGGLE = "ui.sidebar.toggle"
    SIDEBAR_SHOWN = "ui.sidebar.shown"
    SIDEBAR_HIDDEN = "ui.sidebar.hidden"
    STATUSBAR_TOGGLE = "ui.statusbar.toggle"
    STATUSBAR_SHOWN = "ui.statusbar.shown"
    STATUSBAR_HIDDEN = "ui.statusbar.hidden"
    
    # === 폴더 감시 이벤트 ===
    FOLDER_WATCH_START = "folder.watch.start"
    FOLDER_WATCH_STOP = "folder.watch.stop"
    FOLDER_WATCH_ADD = "folder.watch.add"
    FOLDER_WATCH_REMOVE = "folder.watch.remove"
    FOLDER_WATCH_FILE_FOUND = "folder.watch.file_found"
    FOLDER_WATCH_STATUS_CHANGED = "folder.watch.status_changed"
    
    # === 설정 관련 이벤트 ===
    SETTINGS_OPEN = "settings.open"
    SETTINGS_CLOSED = "settings.closed"
    SETTINGS_CHANGED = "settings.changed"
    SETTINGS_SAVED = "settings.saved"
    SETTINGS_RESET = "settings.reset"
    SETTINGS_APPLIED = "settings.applied"
    
    # === 설정 - 일반 탭 ===
    THEME_CHANGED = "settings.theme.changed"
    LANGUAGE_CHANGED = "settings.language.changed"
    STARTUP_OPTIONS_CHANGED = "settings.startup.changed"
    TRAY_MINIMIZE_CHANGED = "settings.tray.changed"
    
    # === 설정 - 처리 탭 ===
    PROFILE_SELECTED = "settings.profile.selected"
    AUTO_PROCESS_CHANGED = "settings.auto_process.changed"
    REPORT_FORMAT_CHANGED = "settings.report_format.changed"
    
    # === 설정 - 폴더 탭 ===
    FOLDER_OUTPUT_CHANGED = "settings.folder.output.changed"
    FOLDER_COMPLETE_CHANGED = "settings.folder.complete.changed"
    FOLDER_STRUCTURE_CHANGED = "settings.folder.structure.changed"
    
    # === 설정 - 인터페이스 탭 ===
    NOTIFICATION_SETTINGS_CHANGED = "settings.notification.changed"
    SIDEBAR_SETTINGS_CHANGED = "settings.sidebar.changed"
    COLUMN_VISIBILITY_CHANGED = "settings.columns.changed"
    
    # === 설정 - 알람 탭 ===
    ALARM_ENABLED = "settings.alarm.enabled"
    ALARM_DISABLED = "settings.alarm.disabled"
    ALARM_CONFIG_CHANGED = "settings.alarm.config.changed"
    ALARM_CONDITION_ADDED = "settings.alarm.condition.added"
    ALARM_CONDITION_REMOVED = "settings.alarm.condition.removed"
    
    # === 설정 - 고급/도구 탭 ===
    CONCURRENT_FILES_CHANGED = "settings.concurrent.changed"
    LOG_LEVEL_CHANGED = "settings.log_level.changed"
    TOOL_PATH_CHANGED = "settings.tool.path.changed"
    TOOL_TEST_REQUESTED = "settings.tool.test"
    TOOL_AUTO_DETECT = "settings.tool.auto_detect"
    
    # === 도구 관련 이벤트 ===
    BATCH_PROCESS_START = "batch.process.start"
    BATCH_PROCESS_COMPLETE = "batch.process.complete"
    BATCH_SCHEDULER_OPEN = "batch.scheduler.open"
    BACKUP_MANAGER_OPEN = "backup.manager.open"
    EXPORT_REPORT = "export.report"
    
    # === 도움말 관련 이벤트 ===
    HELP_OPEN = "help.open"
    ABOUT_OPEN = "about.open"
    UPDATE_CHECK = "update.check"
    
    # === 애플리케이션 라이프사이클 ===
    APP_START = "app.start"
    APP_READY = "app.ready"
    APP_EXIT = "app.exit"
    APP_ERROR = "app.error"
    
    # === 알림 이벤트 ===
    NOTIFICATION_SHOW = "notification.show"
    NOTIFICATION_INFO = "notification.info"
    NOTIFICATION_SUCCESS = "notification.success"
    NOTIFICATION_WARNING = "notification.warning"
    NOTIFICATION_ERROR = "notification.error"
    
    # === 통계 업데이트 이벤트 ===
    STATS_UPDATE = "stats.update"
    STATS_RESET = "stats.reset"
    
    # === 작업 큐 이벤트 ===
    QUEUE_ADD = "queue.add"
    QUEUE_REMOVE = "queue.remove"
    QUEUE_CLEAR = "queue.clear"
    QUEUE_PROCESS = "queue.process"
    
    # === 플러그인 이벤트 (향후 확장용) ===
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ACTION = "plugin.action"


class EventPriority(Enum):
    """이벤트 우선순위"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# 이벤트 카테고리 매핑 (그룹화용)
EVENT_CATEGORIES = {
    "파일": [
        EventType.FILE_OPEN,
        EventType.FILE_OPEN_FOLDER,
        EventType.FILE_DROPPED,
        EventType.FILE_PROCESSING_START,
        EventType.FILE_PROCESSING_PROGRESS,
        EventType.FILE_PROCESSING_COMPLETE,
        EventType.FILE_PROCESSING_ERROR,
        EventType.FILE_RECENT_OPEN,
        EventType.FILE_RECENT_CLEAR,
    ],
    "프로파일": [
        EventType.PROFILE_CHANGED,
        EventType.PROFILE_CREATED,
        EventType.PROFILE_UPDATED,
        EventType.PROFILE_DELETED,
        EventType.PROFILE_LOADED,
        EventType.PROFILE_SAVED,
    ],
    "UI": [
        EventType.VIEW_CHANGED,
        EventType.VIEW_PROCESSING,
        EventType.VIEW_DASHBOARD,
        EventType.VIEW_STATISTICS,
        EventType.VIEW_PROFILE_SETTINGS,
        EventType.VIEW_HISTORY,
        EventType.SIDEBAR_TOGGLE,
        EventType.SIDEBAR_SHOWN,
        EventType.SIDEBAR_HIDDEN,
        EventType.STATUSBAR_TOGGLE,
        EventType.STATUSBAR_SHOWN,
        EventType.STATUSBAR_HIDDEN,
    ],
    "폴더감시": [
        EventType.FOLDER_WATCH_START,
        EventType.FOLDER_WATCH_STOP,
        EventType.FOLDER_WATCH_ADD,
        EventType.FOLDER_WATCH_REMOVE,
        EventType.FOLDER_WATCH_FILE_FOUND,
        EventType.FOLDER_WATCH_STATUS_CHANGED,
    ],
    "설정": [
        EventType.SETTINGS_OPEN,
        EventType.SETTINGS_CLOSED,
        EventType.SETTINGS_CHANGED,
        EventType.SETTINGS_SAVED,
        EventType.SETTINGS_RESET,
        EventType.SETTINGS_APPLIED,
        EventType.THEME_CHANGED,
        EventType.LANGUAGE_CHANGED,
        EventType.STARTUP_OPTIONS_CHANGED,
        EventType.TRAY_MINIMIZE_CHANGED,
        EventType.PROFILE_SELECTED,
        EventType.AUTO_PROCESS_CHANGED,
        EventType.REPORT_FORMAT_CHANGED,
        EventType.FOLDER_OUTPUT_CHANGED,
        EventType.FOLDER_COMPLETE_CHANGED,
        EventType.FOLDER_STRUCTURE_CHANGED,
        EventType.NOTIFICATION_SETTINGS_CHANGED,
        EventType.SIDEBAR_SETTINGS_CHANGED,
        EventType.COLUMN_VISIBILITY_CHANGED,
        EventType.ALARM_ENABLED,
        EventType.ALARM_DISABLED,
        EventType.ALARM_CONFIG_CHANGED,
        EventType.ALARM_CONDITION_ADDED,
        EventType.ALARM_CONDITION_REMOVED,
        EventType.CONCURRENT_FILES_CHANGED,
        EventType.LOG_LEVEL_CHANGED,
        EventType.TOOL_PATH_CHANGED,
        EventType.TOOL_TEST_REQUESTED,
        EventType.TOOL_AUTO_DETECT,
    ],
    "도구": [
        EventType.BATCH_PROCESS_START,
        EventType.BATCH_PROCESS_COMPLETE,
        EventType.BATCH_SCHEDULER_OPEN,
        EventType.BACKUP_MANAGER_OPEN,
        EventType.EXPORT_REPORT,
    ],
    "도움말": [
        EventType.HELP_OPEN,
        EventType.ABOUT_OPEN,
        EventType.UPDATE_CHECK,
    ],
    "시스템": [
        EventType.APP_START,
        EventType.APP_READY,
        EventType.APP_EXIT,
        EventType.APP_ERROR,
        EventType.NOTIFICATION_SHOW,
        EventType.NOTIFICATION_INFO,
        EventType.NOTIFICATION_SUCCESS,
        EventType.NOTIFICATION_WARNING,
        EventType.NOTIFICATION_ERROR,
    ],
}


def get_event_category(event_type: EventType) -> str:
    """이벤트 타입의 카테고리 반환"""
    for category, events in EVENT_CATEGORIES.items():
        if event_type in events:
            return category
    return "기타"