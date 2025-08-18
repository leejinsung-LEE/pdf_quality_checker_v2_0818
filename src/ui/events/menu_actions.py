# src/ui/events/menu_actions.py
"""
메뉴 액션 정의

메뉴 시스템에서 사용되는 액션들을 중앙에서 관리합니다.
"""

from dataclasses import dataclass
from typing import Optional, List
from .event_types import EventType


@dataclass
class MenuAction:
    """메뉴 액션 정의"""
    id: str
    label: str
    event_type: EventType
    accelerator: Optional[str] = None
    icon: Optional[str] = None
    tooltip: Optional[str] = None
    enabled: bool = True
    separator_after: bool = False
    
    def __hash__(self):
        return hash(self.id)


class MenuDefinitions:
    """메뉴 정의 중앙 관리"""
    
    # === 파일 메뉴 ===
    FILE_MENU: List[MenuAction] = [
        MenuAction(
            id="file.open",
            label="파일 열기...",
            event_type=EventType.FILE_OPEN,
            accelerator="Ctrl+O",
            icon="📄",
            tooltip="PDF 파일을 선택하여 엽니다"
        ),
        MenuAction(
            id="file.open_folder",
            label="폴더 열기...",
            event_type=EventType.FILE_OPEN_FOLDER,
            accelerator="Ctrl+Shift+O",
            icon="📁",
            tooltip="폴더 내의 모든 PDF 파일을 처리합니다"
        ),
        MenuAction(
            id="file.recent",
            label="최근 파일",
            event_type=EventType.FILE_RECENT_OPEN,
            icon="🕐",
            tooltip="최근에 사용한 파일 목록",
            separator_after=True
        ),
        MenuAction(
            id="file.exit",
            label="종료",
            event_type=EventType.APP_EXIT,
            accelerator="Ctrl+Q",
            icon="❌",
            tooltip="프로그램을 종료합니다"
        ),
    ]
    
    # === 편집 메뉴 ===
    EDIT_MENU: List[MenuAction] = [
        MenuAction(
            id="edit.preferences",
            label="환경설정...",
            event_type=EventType.SETTINGS_OPEN,
            accelerator="Ctrl+,",
            icon="⚙️",
            tooltip="프로그램 설정을 변경합니다",
            separator_after=True
        ),
        MenuAction(
            id="edit.profiles",
            label="프로파일 관리...",
            event_type=EventType.PROFILE_CHANGED,
            icon="👤",
            tooltip="검사 프로파일을 관리합니다"
        ),
    ]
    
    # === 보기 메뉴 ===
    VIEW_MENU: List[MenuAction] = [
        MenuAction(
            id="view.processing",
            label="처리 화면",
            event_type=EventType.VIEW_PROCESSING,
            accelerator="F1",
            icon="⚡",
            tooltip="파일 처리 화면으로 전환"
        ),
        MenuAction(
            id="view.dashboard",
            label="대시보드",
            event_type=EventType.VIEW_DASHBOARD,
            accelerator="F2",
            icon="📊",
            tooltip="대시보드 화면으로 전환"
        ),
        MenuAction(
            id="view.statistics",
            label="통계 분석",
            event_type=EventType.VIEW_STATISTICS,
            accelerator="F3",
            icon="📈",
            tooltip="통계 분석 화면으로 전환"
        ),
        MenuAction(
            id="view.profile_settings",
            label="프로파일 설정",
            event_type=EventType.VIEW_PROFILE_SETTINGS,
            accelerator="F4",
            icon="🔧",
            tooltip="프로파일 설정 화면으로 전환",
            separator_after=True
        ),
        MenuAction(
            id="view.sidebar",
            label="사이드바",
            event_type=EventType.SIDEBAR_TOGGLE,
            icon="◧",
            tooltip="사이드바 표시/숨기기"
        ),
        MenuAction(
            id="view.statusbar",
            label="상태바",
            event_type=EventType.STATUSBAR_TOGGLE,
            icon="▬",
            tooltip="상태바 표시/숨기기"
        ),
    ]
    
    # === 도구 메뉴 ===
    TOOLS_MENU: List[MenuAction] = [
        MenuAction(
            id="tools.batch_process",
            label="일괄 처리...",
            event_type=EventType.BATCH_PROCESS_START,
            accelerator="Ctrl+B",
            icon="🔄",
            tooltip="여러 파일을 일괄 처리합니다"
        ),
        MenuAction(
            id="tools.folder_watch",
            label="폴더 감시 설정...",
            event_type=EventType.FOLDER_WATCH_START,
            icon="👁️",
            tooltip="폴더 감시를 설정합니다",
            separator_after=True
        ),
        MenuAction(
            id="tools.batch_scheduler",
            label="배치 스케줄러...",
            event_type=EventType.BATCH_SCHEDULER_OPEN,
            accelerator="Ctrl+S",
            icon="⏰",
            tooltip="예약 작업을 설정합니다"
        ),
        MenuAction(
            id="tools.backup_manager",
            label="백업 관리자...",
            event_type=EventType.BACKUP_MANAGER_OPEN,
            accelerator="Ctrl+R",
            icon="💾",
            tooltip="백업을 관리합니다",
            separator_after=True
        ),
        MenuAction(
            id="tools.export_report",
            label="보고서 내보내기...",
            event_type=EventType.EXPORT_REPORT,
            icon="📑",
            tooltip="처리 결과를 보고서로 내보냅니다"
        ),
    ]
    
    # === 도움말 메뉴 ===
    HELP_MENU: List[MenuAction] = [
        MenuAction(
            id="help.docs",
            label="사용 설명서",
            event_type=EventType.HELP_OPEN,
            accelerator="F1",
            icon="📖",
            tooltip="온라인 도움말을 엽니다",
            separator_after=True
        ),
        MenuAction(
            id="help.update",
            label="업데이트 확인",
            event_type=EventType.UPDATE_CHECK,
            icon="🔄",
            tooltip="새 버전을 확인합니다"
        ),
        MenuAction(
            id="help.about",
            label="정보",
            event_type=EventType.ABOUT_OPEN,
            icon="ℹ️",
            tooltip="프로그램 정보를 표시합니다"
        ),
    ]
    
    @classmethod
    def get_all_menus(cls) -> dict:
        """모든 메뉴 정의 반환"""
        return {
            "파일": cls.FILE_MENU,
            "편집": cls.EDIT_MENU,
            "보기": cls.VIEW_MENU,
            "도구": cls.TOOLS_MENU,
            "도움말": cls.HELP_MENU,
        }
    
    @classmethod
    def get_action_by_id(cls, action_id: str) -> Optional[MenuAction]:
        """ID로 액션 찾기"""
        for menu_items in cls.get_all_menus().values():
            for action in menu_items:
                if action.id == action_id:
                    return action
        return None
    
    @classmethod
    def get_shortcuts(cls) -> dict:
        """모든 단축키 매핑 반환"""
        shortcuts = {}
        for menu_items in cls.get_all_menus().values():
            for action in menu_items:
                if action.accelerator:
                    shortcuts[action.accelerator] = action
        return shortcuts


class ContextMenuDefinitions:
    """컨텍스트 메뉴 정의"""
    
    # 파일 리스트 컨텍스트 메뉴
    FILE_LIST_CONTEXT: List[MenuAction] = [
        MenuAction(
            id="context.open",
            label="열기",
            event_type=EventType.FILE_OPEN,
            icon="📄"
        ),
        MenuAction(
            id="context.remove",
            label="목록에서 제거",
            event_type=EventType.QUEUE_REMOVE,
            icon="❌"
        ),
        MenuAction(
            id="context.reprocess",
            label="다시 처리",
            event_type=EventType.FILE_PROCESSING_START,
            icon="🔄",
            separator_after=True
        ),
        MenuAction(
            id="context.show_report",
            label="보고서 보기",
            event_type=EventType.EXPORT_REPORT,
            icon="📑"
        ),
    ]
    
    # 폴더 감시 컨텍스트 메뉴
    FOLDER_WATCH_CONTEXT: List[MenuAction] = [
        MenuAction(
            id="context.watch.start",
            label="감시 시작",
            event_type=EventType.FOLDER_WATCH_START,
            icon="▶️"
        ),
        MenuAction(
            id="context.watch.stop",
            label="감시 중지",
            event_type=EventType.FOLDER_WATCH_STOP,
            icon="⏸️"
        ),
        MenuAction(
            id="context.watch.remove",
            label="폴더 제거",
            event_type=EventType.FOLDER_WATCH_REMOVE,
            icon="❌"
        ),
    ]