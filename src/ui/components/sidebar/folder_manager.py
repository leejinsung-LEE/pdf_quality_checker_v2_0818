# src/ui/components/sidebar/folder_manager.py
"""
폴더 감시 관리

폴더 추가, 제거, 상태 업데이트 및 UI 관리를 담당합니다.
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from pathlib import Path
from datetime import datetime

if TYPE_CHECKING:
    from .base import SidebarBase


class FolderManager:
    """폴더 감시 관리 클래스"""
    
    def __init__(self, parent: 'SidebarBase'):
        self.parent = parent
        self.watch_enabled = False
    
    def _on_watch_toggle(self):
        """폴더 감시 토글"""
        toggle_switch = self.parent.widgets.get('watch_toggle')
        if toggle_switch:
            self.watch_enabled = toggle_switch.get() == 1
            
            # 폴더 감시 상태에 따른 UI 업데이트
            self._update_watch_status()
    
    def _on_add_folder(self):
        """폴더 추가 대화상자"""
        try:
            folder_path = filedialog.askdirectory(title="감시할 폴더 선택")
            
            if folder_path:
                path = Path(folder_path)
                
                # 이미 추가된 폴더인지 확인
                if any(f['path'] == path for f in self.parent.folders):
                    print(f"폴더가 이미 추가되어 있습니다: {path}")
                    return
                
                # 폴더 추가
                self.add_watch_folder(path)
                
                # UI 업데이트
                self._update_folder_list()
                
                # 콜백 호출
                if self.parent.on_folder_select:
                    self.parent.on_folder_select(path)
                    
        except Exception as e:
            print(f"폴더 추가 오류: {e}")
    
    def add_watch_folder(self, path: Path):
        """감시 폴더 추가"""
        folder_info = {
            'path': path,
            'name': path.name,
            'active': self.watch_enabled,
            'file_count': 0,
            'last_processed': None,
            'added_date': datetime.now()
        }
        
        self.parent.folders.append(folder_info)
        print(f"폴더 추가됨: {path}")
    
    def remove_watch_folder(self, path: Path):
        """감시 폴더 제거"""
        original_count = len(self.parent.folders)
        self.parent.folders = [f for f in self.parent.folders if f['path'] != path]
        
        if len(self.parent.folders) < original_count:
            print(f"폴더 제거됨: {path}")
            self._update_folder_list()
    
    def _update_folder_list(self):
        """폴더 목록 UI 업데이트"""
        folder_frame = self.parent.widgets.get('folder_frame')
        if not folder_frame:
            return
        
        # 기존 위젯 제거
        for widget in folder_frame.winfo_children():
            widget.destroy()
        
        if not self.parent.folders:
            # 폴더가 없을 때 안내 메시지
            empty_label = ctk.CTkLabel(
                folder_frame,
                text="감시할 폴더를 추가해주세요",
                font=('맑은 고딕', 10),
                text_color=self.parent.colors['text_secondary']
            )
            empty_label.pack(expand=True)
        else:
            # 폴더 목록 생성
            for folder_info in self.parent.folders:
                self._create_folder_item(folder_frame, folder_info)
    
    def _create_folder_item(self, parent_frame: ctk.CTkFrame, folder_info: Dict[str, Any]):
        """폴더 아이템 UI 생성"""
        # 폴더 아이템 프레임
        item_frame = ctk.CTkFrame(
            parent_frame,
            fg_color="transparent",
            height=40
        )
        item_frame.pack(fill='x', padx=10, pady=2)
        item_frame.pack_propagate(False)
        
        # 폴더 아이콘 및 이름
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side='left', fill='both', expand=True)
        
        # 폴더 이름 (상단)
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"📁 {folder_info['name']}",
            font=('맑은 고딕', 10, 'bold'),
            text_color=self.parent.colors['text_primary'],
            anchor='w'
        )
        name_label.pack(anchor='w', padx=5)
        
        # 폴더 경로 (하단)
        path_label = ctk.CTkLabel(
            info_frame,
            text=str(folder_info['path'])[:30] + "..." if len(str(folder_info['path'])) > 30 else str(folder_info['path']),
            font=('맑은 고딕', 8),
            text_color=self.parent.colors['text_secondary'],
            anchor='w'
        )
        path_label.pack(anchor='w', padx=5)
        
        # 상태 및 제어 버튼
        control_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        control_frame.pack(side='right', padx=5)
        
        # 상태 표시
        status_color = self.parent.colors['success'] if folder_info['active'] else self.parent.colors['text_secondary']
        status_text = "●" if folder_info['active'] else "○"
        
        status_label = ctk.CTkLabel(
            control_frame,
            text=status_text,
            font=('Arial', 12),
            text_color=status_color,
            width=20
        )
        status_label.pack(side='top')
        
        # 제거 버튼
        remove_button = ctk.CTkButton(
            control_frame,
            text="×",
            width=20,
            height=20,
            font=('Arial', 12),
            command=lambda: self._remove_folder_item(folder_info['path'])
        )
        remove_button.pack(side='bottom', pady=(2, 0))
    
    def _remove_folder_item(self, folder_path: Path):
        """폴더 아이템 제거"""
        self.remove_watch_folder(folder_path)
    
    def _update_watch_status(self):
        """폴더 감시 상태 업데이트"""
        # 모든 폴더의 활성화 상태 업데이트
        for folder in self.parent.folders:
            folder['active'] = self.watch_enabled
        
        # UI 업데이트
        self._update_folder_list()
        
        # 상태 메시지
        if self.watch_enabled:
            print("폴더 감시가 활성화되었습니다.")
        else:
            print("폴더 감시가 비활성화되었습니다.")
    
    def update_folder_status(self, path: Path, active: bool):
        """특정 폴더 상태 업데이트"""
        for folder in self.parent.folders:
            if folder['path'] == path:
                folder['active'] = active
                break
        
        self._update_folder_list()
    
    def update_folder_file_count(self, path: Path, count: int):
        """폴더의 처리된 파일 수 업데이트"""
        for folder in self.parent.folders:
            if folder['path'] == path:
                folder['file_count'] = count
                folder['last_processed'] = datetime.now()
                break
    
    def get_active_folders(self) -> List[Dict[str, Any]]:
        """활성화된 폴더 목록 반환"""
        return [f for f in self.parent.folders if f['active']]
    
    def get_folder_info(self, path: Path) -> Optional[Dict[str, Any]]:
        """특정 폴더 정보 조회"""
        for folder in self.parent.folders:
            if folder['path'] == path:
                return folder
        return None
    
    def is_watch_enabled(self) -> bool:
        """폴더 감시 활성화 상태 확인"""
        return self.watch_enabled
    
    def set_watch_enabled(self, enabled: bool):
        """폴더 감시 활성화 상태 설정"""
        self.watch_enabled = enabled
        
        # UI 토글 스위치 업데이트
        toggle_switch = self.parent.widgets.get('watch_toggle')
        if toggle_switch:
            toggle_switch.select() if enabled else toggle_switch.deselect()
        
        # 상태 업데이트
        self._update_watch_status()
    
    def get_folders_summary(self) -> Dict[str, Any]:
        """폴더 감시 요약 정보"""
        total_folders = len(self.parent.folders)
        active_folders = len(self.get_active_folders())
        total_files = sum(f.get('file_count', 0) for f in self.parent.folders)
        
        return {
            'total_folders': total_folders,
            'active_folders': active_folders,
            'total_files_processed': total_files,
            'watch_enabled': self.watch_enabled
        }