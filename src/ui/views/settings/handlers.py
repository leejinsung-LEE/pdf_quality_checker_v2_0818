# src/ui/views/settings/handlers.py
"""
환경설정 뷰 - 이벤트 핸들러와 유틸리티

이 모듈은 환경설정 뷰의 이벤트 처리와 유틸리티 함수들을 담당합니다.
- 설정 로드/저장 로직
- 검증 및 에러 처리
- 외부 도구 관리
- 기본값 복원

AI 친화적 설계:
- 이벤트 처리 로직을 중앙화
- 에러 처리와 검증을 체계화
- 각 탭별 설정 통합 관리
"""

from typing import Dict, Any, Optional, Callable
from tkinter import messagebox
from pathlib import Path

from .general_tab import GeneralTabHelper
from .processing_tab import ProcessingTabHelper
from .folders_tab import FoldersTabHelper
from .interface_tab import InterfaceTabHelper
from .alarm_tab import AlarmTabHelper
from .advanced_tools_tab import AdvancedTabHelper, ToolsTabHelper
from ...controllers import UserSettings


class SettingsEventHandlers:
    """환경설정 이벤트 핸들러 클래스"""
    
    def __init__(self, view, settings_controller):
        self.view = view
        self.settings_controller = settings_controller
        self.widgets = view.widgets
    
    def load_all_settings(self) -> None:
        """모든 설정 로드"""
        settings = self.settings_controller.get_settings()
        
        # 일반 설정
        GeneralTabHelper.load_settings(self.widgets, settings)
        
        # 처리 설정
        ProcessingTabHelper.load_settings(self.widgets, settings)
        
        # 폴더 설정
        FoldersTabHelper.load_settings(self.widgets, settings)
        
        # 인터페이스 설정 (레이블 참조 필요)
        if hasattr(self.view, 'sidebar_width_label'):
            InterfaceTabHelper.load_settings(
                self.widgets, settings, self.view.sidebar_width_label
            )
        
        # 알람 설정 (레이블 참조 필요)
        if hasattr(self.view, 'volume_label'):
            AlarmTabHelper.load_settings(
                self.widgets, settings, self.view.volume_label
            )
        
        # 고급 설정 (레이블 참조 필요)
        if hasattr(self.view, 'concurrent_label'):
            AdvancedTabHelper.load_settings(
                self.widgets, settings, self.view.concurrent_label
            )
    
    def collect_all_settings(self) -> Dict[str, Any]:
        """모든 설정 수집"""
        settings = {}
        
        # 각 탭별 설정 수집
        settings.update(GeneralTabHelper.collect_settings(self.widgets))
        settings.update(ProcessingTabHelper.collect_settings(self.widgets))
        settings.update(FoldersTabHelper.collect_settings(self.widgets))
        settings.update(InterfaceTabHelper.collect_settings(self.widgets))
        settings.update(AlarmTabHelper.collect_settings(self.widgets))
        settings.update(AdvancedTabHelper.collect_settings(self.widgets))
        
        return settings
    
    def apply_settings(self) -> bool:
        """설정 적용"""
        try:
            # 설정 수집
            new_settings = self.collect_all_settings()
            
            # 설정 검증
            if not self._validate_settings(new_settings):
                return False
            
            # 설정 업데이트
            if self.settings_controller.update_settings(new_settings):
                # 외부 도구 설정 저장
                ToolsTabHelper.save_tool_settings(self.widgets, self.settings_controller)
                
                # 콜백 호출
                if hasattr(self.view, 'on_settings_applied') and self.view.on_settings_applied:
                    self.view.on_settings_applied(new_settings)
                
                messagebox.showinfo("성공", "설정이 적용되었습니다.")
                return True
            else:
                messagebox.showerror("오류", "설정 적용에 실패했습니다.")
                return False
                
        except Exception as e:
            messagebox.showerror("오류", f"설정 적용 중 오류 발생:\n{e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """기본값으로 초기화"""
        if messagebox.askyesno("확인", "모든 설정을 기본값으로 초기화하시겠습니까?"):
            try:
                # 기본 설정 객체 생성
                default_settings = UserSettings()
                
                # 컨트롤러에 적용
                self.settings_controller.settings = default_settings
                self.view.settings = default_settings
                
                # UI 다시 로드
                self.load_all_settings()
                
                messagebox.showinfo("완료", "설정이 기본값으로 초기화되었습니다.")
                
            except Exception as e:
                messagebox.showerror("오류", f"초기화 중 오류 발생:\n{e}")
    
    def browse_folder(self, widget_key: str) -> None:
        """폴더 찾아보기"""
        FoldersTabHelper.browse_folder(widget_key, self.widgets)
    
    def browse_tool(self, widget_key: str) -> None:
        """도구 실행 파일 찾아보기"""
        ToolsTabHelper.browse_tool(widget_key, self.widgets)
    
    def test_tool(self, tool_name: str) -> None:
        """외부 도구 테스트"""
        ToolsTabHelper.test_tool(tool_name, self.widgets, self.settings_controller)
    
    def auto_detect_tools(self) -> None:
        """외부 도구 자동 감지"""
        ToolsTabHelper.auto_detect_tools(self.widgets, self.settings_controller)
    
    def _validate_settings(self, settings: Dict[str, Any]) -> bool:
        """설정 검증"""
        try:
            # 숫자 필드 검증
            numeric_fields = {
                'processing_timeout': (1, 3600, "처리 타임아웃은 1-3600초 사이여야 합니다."),
                'keep_log_days': (1, 365, "로그 보관 기간은 1-365일 사이여야 합니다."),
                'max_concurrent_files': (1, 20, "동시 처리 파일 수는 1-20개 사이여야 합니다."),
                'sidebar_width': (200, 500, "사이드바 너비는 200-500px 사이여야 합니다."),
                'alarm_volume': (0, 100, "알림음 볼륨은 0-100% 사이여야 합니다."),
                'alarm_dpi_threshold': (50, 1000, "DPI 임계값은 50-1000 사이여야 합니다."),
                'alarm_ink_threshold': (100, 500, "잉크 커버리지 임계값은 100-500% 사이여야 합니다.")
            }
            
            for field, (min_val, max_val, message) in numeric_fields.items():
                if field in settings:
                    value = settings[field]
                    if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                        messagebox.showerror("검증 오류", message)
                        return False
            
            # 폴더 경로 검증
            folder_fields = ['default_output_folder', 'default_completed_folder']
            for field in folder_fields:
                if field in settings and settings[field]:
                    path = Path(settings[field])
                    try:
                        # 상대 경로는 허용, 절대 경로인 경우 존재 여부 확인
                        if path.is_absolute() and not path.parent.exists():
                            if not messagebox.askyesno(
                                "폴더 없음", 
                                f"{field} 경로의 상위 폴더가 존재하지 않습니다.\n계속 진행하시겠습니까?"
                            ):
                                return False
                    except Exception:
                        # 경로가 유효하지 않은 경우
                        messagebox.showerror("경로 오류", f"{field} 경로가 유효하지 않습니다.")
                        return False
            
            # 시간 형식 검증 (방해 금지 시간)
            time_fields = ['quiet_hours_start', 'quiet_hours_end']
            for field in time_fields:
                if field in settings and settings[field]:
                    if not self._validate_time_format(settings[field]):
                        messagebox.showerror("시간 형식 오류", f"{field}는 HH:MM 형식이어야 합니다.")
                        return False
            
            # 보고서 형식 최소 1개 선택 검증
            if settings.get('generate_report', False):
                if not settings.get('report_formats') or len(settings['report_formats']) == 0:
                    messagebox.showwarning("보고서 형식", "보고서를 생성하려면 최소 1개의 형식을 선택해야 합니다.")
                    return False
            
            return True
            
        except Exception as e:
            messagebox.showerror("검증 오류", f"설정 검증 중 오류 발생:\n{e}")
            return False
    
    def _validate_time_format(self, time_str: str) -> bool:
        """시간 형식 검증 (HH:MM)"""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
            
        except (ValueError, AttributeError):
            return False


class SettingsValidators:
    """설정 검증 유틸리티 클래스"""
    
    @staticmethod
    def validate_positive_integer(value: Any, min_val: int = 1, max_val: int = None) -> bool:
        """양의 정수 검증"""
        try:
            int_val = int(value)
            if int_val < min_val:
                return False
            if max_val is not None and int_val > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_path(path_str: str) -> bool:
        """경로 유효성 검증"""
        try:
            path = Path(path_str)
            return True  # Path 객체 생성에 성공하면 기본적으로 유효
        except Exception:
            return False
    
    @staticmethod
    def validate_percentage(value: Any) -> bool:
        """퍼센트 값 검증 (0-100)"""
        try:
            float_val = float(value)
            return 0 <= float_val <= 100
        except (ValueError, TypeError):
            return False


class SettingsUtils:
    """설정 관련 유틸리티 함수들"""
    
    @staticmethod
    def get_default_widget_values() -> Dict[str, Any]:
        """기본 위젯 값들 반환"""
        return {
            'language': '한국어',
            'theme': '다크',
            'default_profile': 'default',
            'sidebar_width': 250,
            'max_concurrent_files': 3,
            'processing_timeout': 300,
            'log_level': 'INFO',
            'keep_log_days': 30,
            'alarm_volume': 50,
            'alarm_dpi_threshold': 300,
            'alarm_ink_threshold': 320,
            'quiet_hours_start': '22:00',
            'quiet_hours_end': '07:00'
        }
    
    @staticmethod
    def create_backup_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
        """설정 백업 생성"""
        return settings.copy()
    
    @staticmethod
    def restore_from_backup(backup: Dict[str, Any]) -> Dict[str, Any]:
        """백업에서 설정 복원"""
        return backup.copy()