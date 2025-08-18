"""
처리 이력 리스트 관리
기능: 트리뷰 테이블 생성 및 관리
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import HistoryView


class HistoryListManager:
    """이력 리스트 관리 헬퍼 클래스"""
    
    def __init__(self, view: 'HistoryView'):
        self.view = view
        
    def create_table(self, parent):
        """테이블 생성"""
        # Treeview 스타일
        style = ttk.Style()
        style.theme_use('default')
        
        # 색상 설정
        style.configure(
            "History.Treeview",
            background=self.view.colors['bg_secondary'],
            foreground=self.view.colors['text_primary'],
            fieldbackground=self.view.colors['bg_secondary'],
            borderwidth=0,
            font=('Arial', 10)
        )
        style.map('History.Treeview',
                 background=[('selected', self.view.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        style.configure(
            "History.Treeview.Heading",
            background=self.view.colors['bg_card'],
            foreground=self.view.colors['text_primary'],
            borderwidth=1,
            font=('Arial', 10, 'bold')
        )
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columns = (
            'filename', 'processed_at', 'profile', 'pages', 
            'quality_score', 'errors', 'warnings', 'time', 'status'
        )
        
        tree = ttk.Treeview(
            parent,
            columns=columns,
            show='tree headings',
            style="History.Treeview",
            yscrollcommand=scrollbar.set
        )
        
        scrollbar.config(command=tree.yview)
        
        # 컬럼 설정
        tree.heading('#0', text='✓', anchor='center')
        tree.column('#0', width=40, stretch=False)
        
        column_configs = [
            ('filename', '파일명', 250, 'w'),
            ('processed_at', '처리일시', 150, 'center'),
            ('profile', '프로파일', 100, 'center'),
            ('pages', '페이지', 70, 'center'),
            ('quality_score', '품질점수', 80, 'center'),
            ('errors', '오류', 60, 'center'),
            ('warnings', '경고', 60, 'center'),
            ('time', '처리시간', 80, 'center'),
            ('status', '상태', 80, 'center')
        ]
        
        for col_id, heading, width, anchor in column_configs:
            tree.heading(col_id, text=heading)
            tree.column(col_id, width=width, anchor=anchor)
        
        # 이벤트 바인딩
        tree.bind('<ButtonRelease-1>', self.on_tree_click)
        tree.bind('<Double-Button-1>', self.on_tree_double_click)
        
        # 태그 설정
        tree.tag_configure('completed', foreground=self.view.colors['success'])
        tree.tag_configure('error', foreground=self.view.colors['error'])
        tree.tag_configure('cancelled', foreground=self.view.colors['text_secondary'])
        
        tree.pack(fill='both', expand=True)
        
        # 위젯 저장
        self.view.widgets['tree'] = tree
        
    def update_table(self):
        """테이블 업데이트"""
        if 'tree' not in self.view.widgets:
            return
            
        tree = self.view.widgets['tree']
        
        # 기존 항목 삭제
        for item in tree.get_children():
            tree.delete(item)
        
        # 선택 초기화
        self.view.selected_ids.clear()
        
        if not self.view.current_entries:
            # 빈 상태 표시
            if 'empty_label' in self.view.widgets:
                self.view.widgets['empty_label'].pack(expand=True)
            return
        else:
            if 'empty_label' in self.view.widgets:
                self.view.widgets['empty_label'].pack_forget()
        
        # 이력 추가
        for entry in self.view.current_entries:
            # 태그 결정
            tag = ''
            if entry.status == 'completed':
                tag = 'completed'
            elif entry.status == 'error':
                tag = 'error'
            elif entry.status == 'cancelled':
                tag = 'cancelled'
            
            # 값 포맷팅
            values = (
                entry.filename,
                entry.processed_at.strftime('%Y-%m-%d %H:%M'),
                entry.profile_used,
                str(entry.page_count),
                f"{entry.quality_score:.1f}",
                str(entry.error_count),
                str(entry.warning_count),
                f"{entry.processing_time:.1f}s",
                self._get_status_text(entry.status)
            )
            
            # 트리에 추가
            item = tree.insert('', 'end', values=values, tags=(tag,))
            # ID 저장
            tree.set(item, 'id', entry.id)
    
    def update_ui_state(self):
        """UI 상태 업데이트"""
        # 페이지 정보
        total_pages = max(1, (self.view.total_items + self.view.items_per_page - 1) // self.view.items_per_page)
        
        if 'page_label' in self.view.widgets:
            self.view.widgets['page_label'].configure(text=f"{self.view.current_page} / {total_pages}")
        
        # 버튼 상태
        if 'prev_button' in self.view.widgets:
            self.view.widgets['prev_button'].configure(
                state='normal' if self.view.current_page > 1 else 'disabled'
            )
        if 'next_button' in self.view.widgets:
            self.view.widgets['next_button'].configure(
                state='normal' if self.view.current_page < total_pages else 'disabled'
            )
        
        # 정보 레이블
        if 'total_label' in self.view.widgets:
            self.view.widgets['total_label'].configure(text=f"전체: {self.view.total_items}개")
        
        self.update_selection_info()
    
    def update_selection_info(self):
        """선택 정보 업데이트"""
        count = len(self.view.selected_ids)
        
        if 'selection_label' in self.view.widgets:
            self.view.widgets['selection_label'].configure(text=f"선택: {count}개")
        
        if 'delete_button' in self.view.widgets:
            self.view.widgets['delete_button'].configure(
                state='normal' if count > 0 else 'disabled'
            )
    
    def on_tree_click(self, event):
        """트리 클릭 이벤트"""
        if 'tree' not in self.view.widgets:
            return
            
        tree = self.view.widgets['tree']
        
        # 체크박스 영역 클릭 확인
        region = tree.identify_region(event.x, event.y)
        if region == "tree":
            item = tree.identify_row(event.y)
            if item:
                # ID 가져오기
                entry_id = tree.set(item, 'id')
                if entry_id:
                    entry_id = int(entry_id)
                    
                    # 선택 토글
                    if entry_id in self.view.selected_ids:
                        self.view.selected_ids.remove(entry_id)
                        tree.item(item, text='')
                    else:
                        self.view.selected_ids.add(entry_id)
                        tree.item(item, text='✓')
                    
                    self.update_selection_info()
    
    def on_tree_double_click(self, event):
        """트리 더블클릭 이벤트"""
        if 'tree' not in self.view.widgets:
            return
            
        tree = self.view.widgets['tree']
        selection = tree.selection()
        
        if selection:
            item = selection[0]
            entry_id = int(tree.set(item, 'id'))
            
            # 해당 이력 찾기
            for entry in self.view.current_entries:
                if entry.id == entry_id:
                    self.view.show_details(entry)
                    break
    
    def _get_status_text(self, status: str) -> str:
        """상태 텍스트"""
        status_map = {
            'completed': '완료',
            'error': '오류',
            'cancelled': '취소',
            'processing': '처리중',
            'waiting': '대기'
        }
        return status_map.get(status, status)