"""
일괄 처리 프로세스 핸들러
기능: 파일 처리 프로세스 관리
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any
import threading
import time
from datetime import datetime

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import BatchProcessView


class ProcessHandler:
    """처리 프로세스 관리 헬퍼 클래스"""
    
    def __init__(self, view: 'BatchProcessView'):
        self.view = view
        
    def start_process(self):
        """처리 시작"""
        if not self.view.file_list:
            messagebox.showwarning("경고", "처리할 파일을 선택해주세요.")
            return
        
        if self.view.is_processing:
            return
        
        # UI 상태 변경
        self._set_processing_state(True)
        
        # 처리 스레드 시작
        self.view.cancel_event.clear()
        self.view.process_thread = threading.Thread(
            target=self._process_files,
            daemon=True
        )
        self.view.process_thread.start()
    
    def cancel_process(self):
        """처리 취소"""
        if self.view.is_processing:
            self.view.cancel_event.set()
            if 'status_label' in self.view.widgets:
                self.view.widgets['status_label'].configure(text="취소 중...")
    
    def _process_files(self):
        """파일 처리 (백그라운드 스레드)"""
        try:
            # 설정 가져오기
            settings = self._get_process_settings()
            
            # 초기화
            self.view.processed_count = 0
            self.view.total_count = len(self.view.file_list)
            
            # 출력 폴더 생성
            output_dir = Path(settings['output_folder'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 각 파일 처리
            for i, file_path in enumerate(self.view.file_list):
                if self.view.cancel_event.is_set():
                    self.view.message_queue.put(('cancelled', None))
                    break
                
                # 상태 업데이트
                self.view.message_queue.put(('processing', {
                    'file': file_path,
                    'index': i,
                    'total': self.view.total_count
                }))
                
                # 파일 처리
                try:
                    result = self._process_single_file(file_path, settings, output_dir)
                    
                    self.view.processed_count += 1
                    
                    # 결과 전송
                    self.view.message_queue.put(('file_complete', {
                        'file': file_path,
                        'result': result,
                        'processed': self.view.processed_count,
                        'total': self.view.total_count
                    }))
                    
                except Exception as e:
                    # 오류 처리
                    self.view.message_queue.put(('file_error', {
                        'file': file_path,
                        'error': str(e)
                    }))
                    
                    if settings.get('stop_on_error'):
                        break
            
            # 처리 완료
            if not self.view.cancel_event.is_set():
                self.view.message_queue.put(('complete', {
                    'processed': self.view.processed_count,
                    'total': self.view.total_count
                }))
                
        except Exception as e:
            self.view.message_queue.put(('error', str(e)))
    
    def _process_single_file(self, file_path: Path, settings: Dict, output_dir: Path) -> Dict[str, Any]:
        """단일 파일 처리"""
        # 프로파일 가져오기
        profile_name = settings.get('profile', 'default')
        profile, _ = self.view.profile_controller.get_profile(profile_name)
        
        # 출력 경로 결정
        if settings.get('keep_structure'):
            # 원본 구조 유지
            relative_path = file_path.relative_to(file_path.parent.parent)
            output_path = output_dir / relative_path.parent
        else:
            output_path = output_dir
        
        if settings.get('create_subfolders'):
            # 파일별 하위 폴더
            output_path = output_path / file_path.stem
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 파일 처리 (실제 처리 로직)
        result = self.view.batch_processor.process_file(
            file_path,
            output_path,
            profile,
            auto_fix=settings.get('auto_fix', False),
            generate_report=settings.get('generate_report', True)
        )
        
        return result
    
    def _get_process_settings(self) -> Dict[str, Any]:
        """처리 설정 가져오기"""
        settings = {}
        
        # 프로파일
        if 'profile_combo' in self.view.widgets:
            settings['profile'] = self.view.widgets['profile_combo'].get()
        
        # 출력 폴더
        if 'output_entry' in self.view.widgets:
            settings['output_folder'] = self.view.widgets['output_entry'].get()
        
        # 옵션들
        if 'keep_structure' in self.view.widgets:
            settings['keep_structure'] = self.view.widgets['keep_structure'].get()
        
        if 'create_subfolders' in self.view.widgets:
            settings['create_subfolders'] = self.view.widgets['create_subfolders'].get()
        
        if 'auto_fix' in self.view.widgets:
            settings['auto_fix'] = self.view.widgets['auto_fix'].get()
        
        if 'generate_report' in self.view.widgets:
            settings['generate_report'] = self.view.widgets['generate_report'].get()
        
        if 'stop_on_error' in self.view.widgets:
            settings['stop_on_error'] = self.view.widgets['stop_on_error'].get()
        
        return settings
    
    def _set_processing_state(self, is_processing: bool):
        """처리 상태 UI 업데이트"""
        self.view.is_processing = is_processing
        
        # 버튼 상태 변경
        if 'start_btn' in self.view.widgets:
            self.view.widgets['start_btn'].configure(
                state='disabled' if is_processing else 'normal'
            )
        
        if 'cancel_btn' in self.view.widgets:
            self.view.widgets['cancel_btn'].configure(
                state='normal' if is_processing else 'disabled'
            )
        
        # 파일 추가 버튼들 비활성화
        for btn_name in ['add_files_btn', 'add_folder_btn', 'clear_btn']:
            if btn_name in self.view.widgets:
                self.view.widgets[btn_name].configure(
                    state='disabled' if is_processing else 'normal'
                )