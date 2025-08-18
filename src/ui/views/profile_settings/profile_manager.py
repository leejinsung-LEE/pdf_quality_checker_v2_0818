"""
프로파일 관리 헬퍼
기능: 프로파일 생성, 복제, 삭제, 가져오기/내보내기
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from pathlib import Path
from typing import TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import ProfileSettingsView


class ProfileManagerHelper:
    """프로파일 관리 헬퍼 클래스"""
    
    def __init__(self, view: 'ProfileSettingsView'):
        self.view = view
        
    def load_profile_list(self):
        """프로파일 목록 로드"""
        if 'profile_listbox' not in self.view.widgets:
            return
            
        listbox = self.view.widgets['profile_listbox']
        listbox.delete(0, tk.END)
        
        profiles = self.view.profile_manager.get_profile_list()
        for profile in profiles:
            display_name = profile['name']
            if profile['is_builtin']:
                display_name += " (기본)"
            if profile['is_current']:
                display_name += " ✓"
            listbox.insert(tk.END, display_name)
            
        # 부모 프로파일 옵션 업데이트
        if 'parent_menu' in self.view.widgets:
            profile_names = ["없음"] + [p['name'] for p in profiles]
            self.view.widgets['parent_menu'].configure(values=profile_names)
            
    def create_new_profile(self):
        """새 프로파일 생성"""
        name = simpledialog.askstring("새 프로파일", "프로파일 이름을 입력하세요:")
        if not name:
            return
            
        # 기본 프로파일 기반으로 생성
        success = self.view.profile_manager.create_profile(name, base_profile="default")
        
        if success:
            self.view.profile_manager.save_profiles()
            self.load_profile_list()
            
            # 새 프로파일 선택
            if 'profile_listbox' in self.view.widgets:
                listbox = self.view.widgets['profile_listbox']
                for i in range(listbox.size()):
                    if listbox.get(i).startswith(name):
                        listbox.selection_clear(0, tk.END)
                        listbox.selection_set(i)
                        self.view.load_profile_settings(name)
                        break
                        
            messagebox.showinfo("성공", f"프로파일 '{name}'이 생성되었습니다.")
        else:
            messagebox.showerror("오류", "이미 존재하는 프로파일 이름입니다.")
            
    def clone_profile(self):
        """프로파일 복제"""
        if not self.view.current_profile_name:
            messagebox.showwarning("경고", "복제할 프로파일을 선택하세요.")
            return
            
        new_name = simpledialog.askstring(
            "프로파일 복제",
            f"'{self.view.current_profile_name}'의 복제본 이름:"
        )
        
        if not new_name:
            return
            
        success = self.view.profile_manager.create_profile(
            new_name,
            base_profile=self.view.current_profile_name
        )
        
        if success:
            self.view.profile_manager.save_profiles()
            self.load_profile_list()
            messagebox.showinfo("성공", f"프로파일이 복제되었습니다: {new_name}")
        else:
            messagebox.showerror("오류", "프로파일 복제에 실패했습니다.")
            
    def delete_profile(self):
        """프로파일 삭제"""
        if not self.view.current_profile_name:
            messagebox.showwarning("경고", "삭제할 프로파일을 선택하세요.")
            return
            
        profile = self.view.profile_manager.get_profile(self.view.current_profile_name)
        if profile and profile.is_builtin:
            messagebox.showerror("오류", "기본 제공 프로파일은 삭제할 수 없습니다.")
            return
            
        if messagebox.askyesno(
            "확인",
            f"프로파일 '{self.view.current_profile_name}'을 삭제하시겠습니까?"
        ):
            success = self.view.profile_manager.delete_profile(self.view.current_profile_name)
            
            if success:
                self.view.profile_manager.save_profiles()
                self.load_profile_list()
                self.view.current_profile_name = None
                
                if 'settings_title' in self.view.widgets:
                    self.view.widgets['settings_title'].configure(text="프로파일 설정")
                    
                messagebox.showinfo("성공", "프로파일이 삭제되었습니다.")
            else:
                messagebox.showerror("오류", "프로파일 삭제에 실패했습니다.")
                
    def import_profile(self):
        """프로파일 가져오기"""
        file_path = filedialog.askopenfilename(
            title="프로파일 가져오기",
            filetypes=[
                ("JSON 파일", "*.json"),
                ("모든 파일", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        success = self.view.profile_manager.import_profile(Path(file_path))
        
        if success:
            self.view.profile_manager.save_profiles()
            self.load_profile_list()
            messagebox.showinfo("성공", "프로파일을 가져왔습니다.")
        else:
            messagebox.showerror("오류", "프로파일 가져오기에 실패했습니다.")
            
    def export_profile(self):
        """프로파일 내보내기"""
        if not self.view.current_profile_name:
            messagebox.showwarning("경고", "내보낼 프로파일을 선택하세요.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="프로파일 내보내기",
            defaultextension=".json",
            initialfile=f"{self.view.current_profile_name}.json",
            filetypes=[
                ("JSON 파일", "*.json"),
                ("모든 파일", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        success = self.view.profile_manager.export_profile(
            self.view.current_profile_name,
            Path(file_path)
        )
        
        if success:
            messagebox.showinfo("성공", f"프로파일을 내보냈습니다:\n{file_path}")
        else:
            messagebox.showerror("오류", "프로파일 내보내기에 실패했습니다.")