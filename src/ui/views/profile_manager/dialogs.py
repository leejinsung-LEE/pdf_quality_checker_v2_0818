# src/ui/views/profile_manager/dialogs.py
"""
프로파일 관리 뷰 - 대화상자 모듈
프로파일 생성 대화상자와 기타 모달 대화상자들을 관리

AI 친화적 문서화:
- 프로파일 생성을 위한 입력 대화상자
- 모달 창으로 사용자 입력 수집
- 유효성 검증 및 오류 처리
- 타입 힌트를 통한 명확한 인터페이스
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, List, Optional, Any
from pathlib import Path

from ...controllers import get_profile_controller, ProfileInfo


class ProfileCreateDialog(ctk.CTkToplevel):
    """
    프로파일 생성 대화상자
    
    역할:
    - 새 프로파일 생성을 위한 정보 입력
    - 프로파일 이름, 기반 프로파일, 설명 수집
    - 입력 데이터 검증
    - 결과를 parent로 전달
    
    아키텍처:
    - 모달 대화상자 패턴
    - 결과 객체를 통한 데이터 반환
    - 입력 검증 및 오류 처리
    """
    
    def __init__(self, parent):
        """
        프로파일 생성 대화상자 초기화
        
        Args:
            parent: 부모 윈도우
        """
        super().__init__(parent)
        
        self.result: Optional[Dict[str, str]] = None
        self.profile_controller = get_profile_controller()
        
        # 입력 위젯들
        self.name_entry: Optional[ctk.CTkEntry] = None
        self.base_combo: Optional[ctk.CTkComboBox] = None
        self.desc_text: Optional[ctk.CTkTextbox] = None
        
        # 창 설정
        self._setup_window()
        
        # UI 생성
        self._create_ui()
        
        # 포커스 설정
        if self.name_entry:
            self.name_entry.focus()
    
    def _setup_window(self):
        """창 기본 설정"""
        self.title("새 프로파일 생성")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # 모달 창 설정
        self.transient(self.master)
        self.grab_set()
    
    def _create_ui(self):
        """UI 생성"""
        # 제목
        self._create_title()
        
        # 입력 프레임
        self._create_input_frame()
        
        # 버튼 프레임
        self._create_button_frame()
    
    def _create_title(self):
        """제목 라벨 생성"""
        title_label = ctk.CTkLabel(
            self,
            text="새 프로파일 생성",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
    
    def _create_input_frame(self):
        """입력 프레임 생성"""
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # 프로파일 이름
        self._create_name_field(input_frame, 0)
        
        # 기반 프로파일
        self._create_base_field(input_frame, 1)
        
        # 설명
        self._create_description_field(input_frame, 2)
    
    def _create_name_field(self, parent: ctk.CTkFrame, row: int):
        """프로파일 이름 필드 생성"""
        name_label = ctk.CTkLabel(parent, text="프로파일 이름:")
        name_label.grid(row=row, column=0, sticky='w', padx=10, pady=10)
        
        self.name_entry = ctk.CTkEntry(parent, width=300)
        self.name_entry.grid(row=row, column=1, padx=10, pady=10)
    
    def _create_base_field(self, parent: ctk.CTkFrame, row: int):
        """기반 프로파일 필드 생성"""
        base_label = ctk.CTkLabel(parent, text="기반 프로파일:")
        base_label.grid(row=row, column=0, sticky='w', padx=10, pady=10)
        
        # 프로파일 목록 가져오기
        profiles = self.profile_controller.get_profile_list()
        profile_names = [p.name for p in profiles]
        
        self.base_combo = ctk.CTkComboBox(
            parent,
            values=profile_names,
            width=300
        )
        self.base_combo.grid(row=row, column=1, padx=10, pady=10)
        
        # 기본값 설정 (default 프로파일이 있으면 선택)
        if 'default' in profile_names:
            self.base_combo.set('default')
        elif profile_names:
            self.base_combo.set(profile_names[0])
    
    def _create_description_field(self, parent: ctk.CTkFrame, row: int):
        """설명 필드 생성"""
        desc_label = ctk.CTkLabel(parent, text="설명:")
        desc_label.grid(row=row, column=0, sticky='nw', padx=10, pady=10)
        
        self.desc_text = ctk.CTkTextbox(parent, width=300, height=150)
        self.desc_text.grid(row=row, column=1, padx=10, pady=10)
    
    def _create_button_frame(self):
        """버튼 프레임 생성"""
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="취소",
            command=self.destroy,
            width=100
        )
        cancel_btn.pack(side='right', padx=(5, 0))
        
        # 생성 버튼
        create_btn = ctk.CTkButton(
            button_frame,
            text="생성",
            command=self._create_profile,
            width=100
        )
        create_btn.pack(side='right')
    
    def _create_profile(self):
        """프로파일 생성 처리"""
        # 입력 검증
        if not self._validate_input():
            return
        
        # 결과 데이터 설정
        self.result = {
            'name': self.name_entry.get().strip(),
            'base': self.base_combo.get(),
            'description': self.desc_text.get('1.0', 'end-1c')
        }
        
        # 창 닫기
        self.destroy()
    
    def _validate_input(self) -> bool:
        """
        입력 데이터 검증
        
        Returns:
            검증 성공 여부
        """
        if not self.name_entry or not self.base_combo or not self.desc_text:
            messagebox.showerror("오류", "UI 초기화 오류가 발생했습니다.")
            return False
        
        # 프로파일 이름 검증
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("경고", "프로파일 이름을 입력하세요.")
            self.name_entry.focus()
            return False
        
        # 이름 길이 검증
        if len(name) > 50:
            messagebox.showwarning("경고", "프로파일 이름은 50자 이하여야 합니다.")
            self.name_entry.focus()
            return False
        
        # 특수문자 검증
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in name for char in invalid_chars):
            messagebox.showwarning(
                "경고", 
                f"프로파일 이름에는 다음 문자를 사용할 수 없습니다:\n{', '.join(invalid_chars)}"
            )
            self.name_entry.focus()
            return False
        
        # 중복 이름 검증
        existing_profiles = self.profile_controller.get_profile_list()
        existing_names = [p.name for p in existing_profiles]
        
        if name in existing_names:
            messagebox.showwarning("경고", f"'{name}' 프로파일이 이미 존재합니다.")
            self.name_entry.focus()
            return False
        
        # 기반 프로파일 검증
        base_profile = self.base_combo.get()
        if not base_profile:
            messagebox.showwarning("경고", "기반 프로파일을 선택하세요.")
            self.base_combo.focus()
            return False
        
        # 기반 프로파일 존재 여부 확인
        if base_profile not in existing_names:
            messagebox.showwarning("경고", "선택한 기반 프로파일이 존재하지 않습니다.")
            self.base_combo.focus()
            return False
        
        return True


class ProfileImportNameDialog(ctk.CTkInputDialog):
    """
    프로파일 가져오기 이름 입력 대화상자
    
    역할:
    - 가져올 프로파일의 새 이름 입력
    - 기본값으로 파일명 제시
    - 중복 이름 검증
    """
    
    def __init__(self, default_name: str = ""):
        """
        이름 입력 대화상자 초기화
        
        Args:
            default_name: 기본 이름
        """
        super().__init__(
            text="가져올 프로파일의 이름을 입력하세요 (비워두면 파일명 사용):",
            title="프로파일 가져오기"
        )
        
        # 기본값 설정
        if default_name:
            self._entry.delete(0, 'end')
            self._entry.insert(0, default_name)


class ProfileDuplicateNameDialog(ctk.CTkInputDialog):
    """
    프로파일 복제 이름 입력 대화상자
    
    역할:
    - 복제할 프로파일의 새 이름 입력
    - 기본값으로 "복사본" 제시
    - 중복 이름 검증
    """
    
    def __init__(self, original_name: str):
        """
        복제 이름 입력 대화상자 초기화
        
        Args:
            original_name: 원본 프로파일 이름
        """
        default_copy_name = f"{original_name}_복사본"
        
        super().__init__(
            text=f"'{original_name}'의 복사본 이름을 입력하세요:",
            title="프로파일 복제"
        )
        
        # 기본값 설정
        self._entry.delete(0, 'end')
        self._entry.insert(0, default_copy_name)


class ConfirmDialog:
    """
    확인 대화상자 유틸리티 클래스
    
    역할:
    - 삭제, 덮어쓰기 등 위험한 작업 확인
    - 표준 메시지박스를 래핑하여 일관성 제공
    """
    
    @staticmethod
    def confirm_delete(profile_name: str) -> bool:
        """
        프로파일 삭제 확인
        
        Args:
            profile_name: 삭제할 프로파일 이름
            
        Returns:
            사용자 확인 여부
        """
        return messagebox.askyesno(
            "프로파일 삭제 확인",
            f"프로파일 '{profile_name}'을 삭제하시겠습니까?\n\n"
            "이 작업은 되돌릴 수 없습니다."
        )
    
    @staticmethod
    def confirm_overwrite(profile_name: str) -> bool:
        """
        프로파일 덮어쓰기 확인
        
        Args:
            profile_name: 덮어쓸 프로파일 이름
            
        Returns:
            사용자 확인 여부
        """
        return messagebox.askyesno(
            "프로파일 덮어쓰기 확인",
            f"프로파일 '{profile_name}'이 이미 존재합니다.\n"
            "덮어쓰시겠습니까?"
        )
    
    @staticmethod
    def confirm_set_current(profile_name: str) -> bool:
        """
        현재 프로파일 설정 확인
        
        Args:
            profile_name: 기본으로 설정할 프로파일 이름
            
        Returns:
            사용자 확인 여부
        """
        return messagebox.askyesno(
            "기본 프로파일 설정",
            f"'{profile_name}'을 기본 프로파일로 설정하시겠습니까?"
        )


class MessageDialog:
    """
    메시지 대화상자 유틸리티 클래스
    
    역할:
    - 성공, 오류, 경고 메시지 표시
    - 일관된 메시지 스타일 제공
    """
    
    @staticmethod
    def show_success(title: str, message: str):
        """성공 메시지 표시"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_error(title: str, message: str):
        """오류 메시지 표시"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_warning(title: str, message: str):
        """경고 메시지 표시"""
        messagebox.showwarning(title, message)