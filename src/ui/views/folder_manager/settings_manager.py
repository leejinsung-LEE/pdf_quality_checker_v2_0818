"""
설정 매니저 - 폴더별 설정 관리
"""

from typing import TYPE_CHECKING, Dict, Any
import json
from pathlib import Path

from ....processing.folder_watcher import FolderConfig

if TYPE_CHECKING:
    from .base import FolderManagerView


class SettingsManager:
    """설정 매니저"""
    
    def __init__(self, view: 'FolderManagerView'):
        self.view = view
        self.current_settings = {}
    
    def load_folder_settings(self, folder_path: str):
        """폴더 설정 로드"""
        # 설정 파일에서 해당 폴더 설정 로드
        try:
            config_file = Path(f"data/folder_settings/{Path(folder_path).name}.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                # 기본 설정
                settings = self._get_default_settings()
            
            self.current_settings = settings
            self._apply_settings_to_ui(settings)
            
        except Exception as e:
            print(f"설정 로드 실패: {e}")
            self.current_settings = self._get_default_settings()
            self._apply_settings_to_ui(self.current_settings)
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """기본 설정 반환"""
        return {
            'enabled': True,
            'auto_process': True,
            'output_folder': '',
            'profile': '기본',
            'file_pattern': '*.pdf',
            'check_images': True,
            'check_fonts': True,
            'check_colors': True,
            'check_resolution': True,
            'check_bleed': False,
            'check_transparency': False,
            'check_layers': False,
            'check_annotations': False,
            'auto_fix': False,
            'fix_images': False,
            'fix_fonts': False,
            'fix_colors': False,
            'fix_compression': False,
            'generate_report': True,
            'report_pdf': True,
            'report_html': False,
            'report_excel': False,
            'report_json': False,
            'send_email': False,
            'email_recipients': ''
        }
    
    def _apply_settings_to_ui(self, settings: Dict[str, Any]):
        """설정을 UI에 적용"""
        for key, value in settings.items():
            widget = self.view.widgets.get(key)
            if widget:
                if hasattr(widget, 'set'):
                    widget.set(value)
                elif hasattr(widget, 'select') and value:
                    widget.select()
                elif hasattr(widget, 'deselect') and not value:
                    widget.deselect()
                elif hasattr(widget, 'insert'):
                    widget.delete('1.0', 'end')
                    widget.insert('1.0', value)
    
    def get_current_settings(self) -> Dict[str, Any]:
        """현재 UI 설정 가져오기"""
        settings = {}
        
        for key in self._get_default_settings().keys():
            widget = self.view.widgets.get(key)
            if widget:
                if hasattr(widget, 'get'):
                    value = widget.get()
                    if hasattr(value, '__bool__'):
                        settings[key] = bool(value)
                    else:
                        settings[key] = value
                elif hasattr(widget, 'cget'):
                    # CheckBox의 경우
                    try:
                        settings[key] = widget.cget('variable').get() if hasattr(widget, 'cget') else False
                    except:
                        settings[key] = False
                elif hasattr(widget, 'get'):
                    # Textbox의 경우
                    settings[key] = widget.get('1.0', 'end-1c')
            else:
                # 위젯이 없으면 현재 설정 유지
                settings[key] = self.current_settings.get(key, 
                                self._get_default_settings().get(key))
        
        return settings
    
    def save_settings(self, folder_path: str, settings: Dict[str, Any]):
        """설정 저장"""
        try:
            config_dir = Path("data/folder_settings")
            config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = config_dir / f"{Path(folder_path).name}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            # FolderConfig 업데이트
            if self.view.folder_watcher:
                folder_config = FolderConfig(
                    path=Path(folder_path),
                    enabled=settings.get('enabled', True),
                    auto_process=settings.get('auto_process', True),
                    output_folder=Path(settings.get('output_folder', '')),
                    profile_name=settings.get('profile', '기본')
                )
                self.view.folder_watcher.update_config(folder_config)
                
        except Exception as e:
            print(f"설정 저장 실패: {e}")
    
    def clear_settings(self):
        """설정 초기화"""
        self.current_settings = {}
        # UI 비활성화 또는 초기화
        for widget in self.view.widgets.values():
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(state='disabled')
                except:
                    pass
    
    def toggle_report_formats(self):
        """리포트 형식 토글"""
        generate_report = self.view.widgets.get('generate_report')
        format_frame = self.view.widgets.get('format_frame')
        
        if generate_report and format_frame:
            if generate_report.get():
                format_frame.configure(state='normal')
                # 포맷 체크박스들 활성화
                for key in ['report_pdf', 'report_html', 'report_excel', 'report_json']:
                    widget = self.view.widgets.get(key)
                    if widget:
                        widget.configure(state='normal')
            else:
                format_frame.configure(state='disabled')
                # 포맷 체크박스들 비활성화
                for key in ['report_pdf', 'report_html', 'report_excel', 'report_json']:
                    widget = self.view.widgets.get(key)
                    if widget:
                        widget.configure(state='disabled')