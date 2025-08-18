# src/ui/views/profile_manager/handlers.py
"""
프로파일 관리 뷰 - 이벤트 핸들러
모든 CRUD 작업과 이벤트 처리 로직을 담당

AI 친화적 문서화:
- 프로파일 생성, 수정, 삭제, 복제 처리
- Import/Export 기능 구현
- 선택/더블클릭 이벤트 처리
- 데이터 유효성 검증 및 저장
- 에러 처리 및 사용자 피드백
"""

from tkinter import filedialog
import customtkinter as ctk
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from pathlib import Path

from .dialogs import (
    ProfileCreateDialog, ProfileImportNameDialog, ProfileDuplicateNameDialog,
    ConfirmDialog, MessageDialog
)

if TYPE_CHECKING:
    from .base import ProfileManagerView


class ProfileEventHandler:
    """
    프로파일 이벤트 핸들러 클래스
    
    역할:
    - 모든 프로파일 관련 이벤트 처리
    - CRUD 작업 로직 구현
    - 사용자 상호작용 처리
    - 데이터 검증 및 저장
    - 오류 처리 및 메시지 표시
    
    아키텍처:
    - 이벤트 위임 패턴
    - 단일 책임 원칙 적용
    - 비즈니스 로직과 UI 분리
    """
    
    def __init__(self, view: 'ProfileManagerView'):
        """
        이벤트 핸들러 초기화
        
        Args:
            view: ProfileManagerView 인스턴스
        """
        self.view = view
        self.profile_controller = view.profile_controller
        
        # 헬퍼 참조
        self.info_helper = view.info_tab_helper
        self.standards_helper = view.standards_tab_helper
        self.rules_helper = view.rules_tab_helper
        self.color_helper = view.color_tab_helper
    
    def on_profile_select(self, profile_name: str):
        """
        프로파일 선택 이벤트 처리
        
        Args:
            profile_name: 선택된 프로파일 이름
        """
        self.view.set_selected_profile(profile_name)
        self.view.load_profile_details(profile_name)
    
    def on_profile_double_click(self, profile_name: str):
        """
        프로파일 더블클릭 이벤트 처리 (현재 프로파일로 설정)
        
        Args:
            profile_name: 더블클릭된 프로파일 이름
        """
        self.set_as_current_profile(profile_name)
    
    def on_save_profile(self):
        """프로파일 저장 이벤트 처리"""
        selected_profile = self.view.get_selected_profile()
        
        if not selected_profile:
            MessageDialog.show_warning("경고", "선택된 프로파일이 없습니다.")
            return
        
        profile = self.profile_controller.get_profile(selected_profile)
        if not profile or profile.is_builtin:
            MessageDialog.show_warning("경고", "내장 프로파일은 수정할 수 없습니다.")
            return
        
        # 데이터 검증
        if not self._validate_all_data():
            return
        
        try:
            self._save_profile_data(selected_profile, profile)
            MessageDialog.show_success("성공", "프로파일이 저장되었습니다.")
            self.view.refresh_profile_list()
            
        except Exception as e:
            MessageDialog.show_error("오류", f"프로파일 저장 중 오류 발생:\n{e}")
    
    def create_profile(self):
        """새 프로파일 생성"""
        dialog = ProfileCreateDialog(self.view)
        self.view.wait_window(dialog)
        
        if dialog.result:
            name = dialog.result['name']
            base = dialog.result['base']
            description = dialog.result['description']
            
            try:
                success = self.profile_controller.create_profile(name, base, description)
                if success:
                    MessageDialog.show_success("성공", f"프로파일 '{name}'이 생성되었습니다.")
                    self.view.refresh_profile_list()
                else:
                    MessageDialog.show_error("오류", "프로파일 생성에 실패했습니다.")
            except Exception as e:
                MessageDialog.show_error("오류", f"프로파일 생성 중 오류 발생:\n{e}")
    
    def duplicate_profile(self):
        """프로파일 복제"""
        selected_profile = self.view.get_selected_profile()
        
        if not selected_profile:
            MessageDialog.show_warning("경고", "복제할 프로파일을 선택하세요.")
            return
        
        # 새 이름 입력 받기
        dialog = ProfileDuplicateNameDialog(selected_profile)
        new_name = dialog.get_input()
        
        if new_name:
            try:
                success = self.profile_controller.duplicate_profile(selected_profile, new_name)
                if success:
                    MessageDialog.show_success("성공", f"프로파일이 복제되었습니다: {new_name}")
                    self.view.refresh_profile_list()
                else:
                    MessageDialog.show_error("오류", "프로파일 복제에 실패했습니다.")
            except Exception as e:
                MessageDialog.show_error("오류", f"프로파일 복제 중 오류 발생:\n{e}")
    
    def delete_profile(self):
        """프로파일 삭제"""
        selected_profile = self.view.get_selected_profile()
        
        if not selected_profile:
            MessageDialog.show_warning("경고", "삭제할 프로파일을 선택하세요.")
            return
        
        profile = self.profile_controller.get_profile(selected_profile)
        if profile and profile.is_builtin:
            MessageDialog.show_warning("경고", "내장 프로파일은 삭제할 수 없습니다.")
            return
        
        # 삭제 확인
        if not ConfirmDialog.confirm_delete(selected_profile):
            return
        
        try:
            success = self.profile_controller.delete_profile(selected_profile)
            if success:
                MessageDialog.show_success("성공", "프로파일이 삭제되었습니다.")
                self.view.set_selected_profile(None)
                self.view.refresh_profile_list()
            else:
                MessageDialog.show_error("오류", "프로파일 삭제에 실패했습니다.")
        except Exception as e:
            MessageDialog.show_error("오류", f"프로파일 삭제 중 오류 발생:\n{e}")
    
    def import_profile(self):
        """프로파일 가져오기"""
        file_path = filedialog.askopenfilename(
            title="프로파일 파일 선택",
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
        )
        
        if not file_path:
            return
        
        # 새 이름 입력 받기
        default_name = Path(file_path).stem
        dialog = ProfileImportNameDialog(default_name)
        new_name = dialog.get_input()
        
        try:
            success = self.profile_controller.import_profile(
                Path(file_path), 
                new_name or None
            )
            if success:
                MessageDialog.show_success("성공", "프로파일을 가져왔습니다.")
                self.view.refresh_profile_list()
            else:
                MessageDialog.show_error("오류", "프로파일 가져오기에 실패했습니다.")
        except Exception as e:
            MessageDialog.show_error("오류", f"프로파일 가져오기 중 오류 발생:\n{e}")
    
    def export_profile(self):
        """프로파일 내보내기"""
        selected_profile = self.view.get_selected_profile()
        
        if not selected_profile:
            MessageDialog.show_warning("경고", "내보낼 프로파일을 선택하세요.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="프로파일 저장",
            defaultextension=".json",
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")],
            initialfile=f"{selected_profile}.json"
        )
        
        if not file_path:
            return
        
        try:
            success = self.profile_controller.export_profile(
                selected_profile, 
                Path(file_path)
            )
            if success:
                MessageDialog.show_success("성공", f"프로파일을 내보냈습니다:\n{file_path}")
            else:
                MessageDialog.show_error("오류", "프로파일 내보내기에 실패했습니다.")
        except Exception as e:
            MessageDialog.show_error("오류", f"프로파일 내보내기 중 오류 발생:\n{e}")
    
    def set_as_current_profile(self, profile_name: Optional[str] = None):
        """현재 프로파일로 설정"""
        target_profile = profile_name or self.view.get_selected_profile()
        
        if not target_profile:
            MessageDialog.show_warning("경고", "프로파일을 선택하세요.")
            return
        
        try:
            success = self.profile_controller.set_current_profile(target_profile)
            if success:
                self.view.current_profile_name = target_profile
                MessageDialog.show_success(
                    "성공", 
                    f"'{target_profile}'을 기본 프로파일로 설정했습니다."
                )
                self.view.refresh_profile_list()
            else:
                MessageDialog.show_error("오류", "프로파일 설정에 실패했습니다.")
        except Exception as e:
            MessageDialog.show_error("오류", f"프로파일 설정 중 오류 발생:\n{e}")
    
    def _validate_all_data(self) -> bool:
        """모든 탭 데이터 검증"""
        # 품질 기준 탭 검증
        if self.standards_helper:
            valid, message = self.standards_helper.validate_data()
            if not valid:
                MessageDialog.show_warning("품질 기준 오류", message)
                return False
        
        # 검사 규칙 탭 검증
        if self.rules_helper:
            valid, message = self.rules_helper.validate_data()
            if not valid:
                MessageDialog.show_warning("검사 규칙 오류", message)
                return False
        
        # 색상 설정 탭 검증
        if self.color_helper:
            valid, message = self.color_helper.validate_data()
            if not valid:
                MessageDialog.show_warning("색상 설정 오류", message)
                return False
        
        return True
    
    def _save_profile_data(self, profile_name: str, profile: Any):
        """프로파일 데이터 저장"""
        # 설명 업데이트
        if self.info_helper:
            description = self.info_helper.get_description()
            self.profile_controller.update_profile_description(profile_name, description)
        
        # 품질 기준 업데이트
        if self.standards_helper:
            standards = self.standards_helper.get_standards_data()
            self.profile_controller.update_quality_standards(profile_name, standards)
        
        # 색상 옵션 업데이트
        if self.color_helper:
            color_options = self.color_helper.get_color_options()
            profile.data['check_options'] = color_options
        
        # 검사 규칙 업데이트
        if self.rules_helper:
            enabled_rules, rule_severities = self.rules_helper.get_rules_data()
            profile.data['enabled_rules'] = enabled_rules
            profile.data['rule_severities'] = rule_severities
        
        # 프로파일 업데이트
        success = self.profile_controller.update_profile(profile_name, profile.data)
        if not success:
            raise Exception("프로파일 컨트롤러 업데이트 실패")
    
    def reset_current_profile_to_defaults(self):
        """현재 프로파일을 기본값으로 초기화"""
        selected_profile = self.view.get_selected_profile()
        
        if not selected_profile:
            MessageDialog.show_warning("경고", "초기화할 프로파일을 선택하세요.")
            return
        
        profile = self.profile_controller.get_profile(selected_profile)
        if profile and profile.is_builtin:
            MessageDialog.show_warning("경고", "내장 프로파일은 초기화할 수 없습니다.")
            return
        
        # 확인 대화상자
        if not self.view.ask_yes_no(
            "프로파일 초기화", 
            f"프로파일 '{selected_profile}'을 기본값으로 초기화하시겠습니까?\n"
            "현재 설정이 모두 사라집니다."
        ):
            return
        
        try:
            # 각 헬퍼의 기본값 재설정 메서드 호출
            if self.standards_helper:
                self.standards_helper.reset_to_defaults()
            
            if self.color_helper:
                self.color_helper.reset_to_defaults()
            
            if self.rules_helper:
                self.rules_helper.select_all_rules()  # 모든 규칙 활성화
            
            MessageDialog.show_success("성공", "프로파일이 기본값으로 초기화되었습니다.")
            
        except Exception as e:
            MessageDialog.show_error("오류", f"프로파일 초기화 중 오류 발생:\n{e}")
    
    def copy_settings_from_profile(self):
        """다른 프로파일에서 설정 복사"""
        selected_profile = self.view.get_selected_profile()
        
        if not selected_profile:
            MessageDialog.show_warning("경고", "설정을 복사받을 프로파일을 선택하세요.")
            return
        
        # 복사할 소스 프로파일 선택 대화상자
        profiles = self.profile_controller.get_profile_list()
        profile_names = [p.name for p in profiles if p.name != selected_profile]
        
        if not profile_names:
            MessageDialog.show_warning("경고", "복사할 수 있는 다른 프로파일이 없습니다.")
            return
        
        # 간단한 선택 대화상자 (CTkComboBox를 사용한 선택창 구현 필요 시)
        # 현재는 첫 번째 프로파일을 기본으로 설정
        source_profile = profile_names[0]  # 실제로는 사용자 선택 받아야 함
        
        try:
            source_data = self.profile_controller.get_profile(source_profile)
            if source_data:
                # 현재 프로파일에 소스 프로파일 설정 적용
                self.view.load_profile_details(source_profile)
                MessageDialog.show_success(
                    "성공", 
                    f"'{source_profile}'의 설정을 복사했습니다.\n저장하려면 '저장' 버튼을 클릭하세요."
                )
            
        except Exception as e:
            MessageDialog.show_error("오류", f"설정 복사 중 오류 발생:\n{e}")