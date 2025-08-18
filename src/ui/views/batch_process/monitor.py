"""
일괄 처리 진행 상황 모니터
기능: 처리 진행 상황 모니터링 및 UI 업데이트
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING, Dict, Any
from pathlib import Path

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import BatchProcessView


class ProgressMonitor:
    """진행 상황 모니터링 헬퍼 클래스"""
    
    def __init__(self, view: 'BatchProcessView'):
        self.view = view
        
    def start_monitoring(self):
        """큐 모니터링 시작"""
        self._monitor_queue()
    
    def _monitor_queue(self):
        """메시지 큐 모니터링"""
        try:
            while not self.view.message_queue.empty():
                msg_type, data = self.view.message_queue.get_nowait()
                
                if msg_type == 'processing':
                    self._on_file_processing(data)
                elif msg_type == 'file_complete':
                    self._on_file_complete(data)
                elif msg_type == 'file_error':
                    self._on_file_error(data)
                elif msg_type == 'complete':
                    self._on_process_complete(data)
                elif msg_type == 'cancelled':
                    self._on_process_cancelled()
                elif msg_type == 'error':
                    self._on_process_error(data)
                    
        except:
            pass
        
        # 다음 체크 스케줄
        self.view.after(100, self._monitor_queue)
    
    def _on_file_processing(self, data: Dict[str, Any]):
        """파일 처리 중 이벤트"""
        file_path = data['file']
        index = data['index']
        total = data['total']
        
        # 상태 레이블 업데이트
        if 'status_label' in self.view.widgets:
            self.view.widgets['status_label'].configure(
                text=f"처리 중: {file_path.name} ({index + 1}/{total})"
            )
        
        # 진행률 바 업데이트
        if 'progress_bar' in self.view.widgets:
            progress = index / total
            self.view.widgets['progress_bar'].set(progress)
        
        # 파일 상태 업데이트
        if hasattr(self.view, 'file_manager'):
            self.view.file_manager.update_file_status(file_path, "처리 중")
    
    def _on_file_complete(self, data: Dict[str, Any]):
        """파일 처리 완료 이벤트"""
        file_path = data['file']
        processed = data['processed']
        total = data['total']
        
        # 파일 상태 업데이트
        if hasattr(self.view, 'file_manager'):
            self.view.file_manager.update_file_status(file_path, "완료")
        
        # 진행률 바 업데이트
        if 'progress_bar' in self.view.widgets:
            progress = processed / total
            self.view.widgets['progress_bar'].set(progress)
    
    def _on_file_error(self, data: Dict[str, Any]):
        """파일 처리 오류 이벤트"""
        file_path = data['file']
        error = data['error']
        
        # 파일 상태 업데이트
        if hasattr(self.view, 'file_manager'):
            self.view.file_manager.update_file_status(file_path, "오류")
        
        # 오류 로그 (선택적으로 표시)
        print(f"Error processing {file_path.name}: {error}")
    
    def _on_process_complete(self, data: Dict[str, Any]):
        """전체 처리 완료 이벤트"""
        processed = data['processed']
        total = data['total']
        
        # 상태 레이블 업데이트
        if 'status_label' in self.view.widgets:
            self.view.widgets['status_label'].configure(
                text=f"완료: {processed}/{total}개 파일 처리됨",
                text_color="green"
            )
        
        # 진행률 바 완료
        if 'progress_bar' in self.view.widgets:
            self.view.widgets['progress_bar'].set(1.0)
        
        # UI 상태 리셋
        self._reset_ui()
        
        # 완료 메시지
        messagebox.showinfo(
            "처리 완료",
            f"{processed}개 파일 중 {processed}개 처리 완료"
        )
    
    def _on_process_cancelled(self):
        """처리 취소 이벤트"""
        # 상태 레이블 업데이트
        if 'status_label' in self.view.widgets:
            self.view.widgets['status_label'].configure(
                text="취소됨",
                text_color="orange"
            )
        
        # UI 상태 리셋
        self._reset_ui()
        
        messagebox.showinfo("알림", "처리가 취소되었습니다.")
    
    def _on_process_error(self, error: str):
        """처리 오류 이벤트"""
        # 상태 레이블 업데이트
        if 'status_label' in self.view.widgets:
            self.view.widgets['status_label'].configure(
                text="오류 발생",
                text_color="red"
            )
        
        # UI 상태 리셋
        self._reset_ui()
        
        messagebox.showerror("오류", f"처리 중 오류가 발생했습니다:\n{error}")
    
    def _reset_ui(self):
        """UI 상태 리셋"""
        self.view.is_processing = False
        
        # 버튼 상태 복원
        if hasattr(self.view, 'process_handler'):
            self.view.process_handler._set_processing_state(False)
        
        # 진행률 바 리셋
        if 'progress_bar' in self.view.widgets:
            self.view.widgets['progress_bar'].set(0)