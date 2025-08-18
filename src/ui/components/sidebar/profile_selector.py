# src/ui/components/sidebar/profile_selector.py
"""
프로파일 선택 관리

프로파일 선택, 업데이트, 변경 이벤트 처리를 담당합니다.
"""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import SidebarBase


class ProfileSelector:
    """프로파일 선택 관리 클래스"""
    
    def __init__(self, parent: 'SidebarBase'):
        self.parent = parent
        self.current_profile = "default"
    
    def _on_profile_select(self, profile_name: str):
        """프로파일 선택 이벤트 처리"""
        try:
            self.current_profile = profile_name
            
            # 프로파일 컨트롤러에 변경 알림
            self.parent.profile_controller.set_current_profile(profile_name)
            
            # 콜백 호출
            if self.parent.on_profile_change:
                self.parent.on_profile_change(profile_name)
                
        except Exception as e:
            print(f"프로파일 선택 오류: {e}")
    
    def get_profile_list(self) -> List[str]:
        """사용 가능한 프로파일 목록 조회"""
        try:
            profiles = self.parent.profile_controller.get_profile_list()
            # ProfileInfo 객체를 문자열로 변환
            if profiles:
                if hasattr(profiles[0], 'name'):
                    # ProfileInfo 객체인 경우
                    return [p.name for p in profiles]
                else:
                    # 이미 문자열인 경우
                    return profiles
            return ["default"]
        except Exception:
            return ["default"]
    
    def get_current_profile(self) -> str:
        """현재 선택된 프로파일 조회"""
        try:
            current_profile = self.parent.profile_controller.get_current_profile()[0]
            self.current_profile = current_profile
            return current_profile
        except Exception:
            return "default"
    
    def update_profile_dropdown(self):
        """프로파일 드롭다운 업데이트"""
        profile_dropdown = self.parent.widgets.get('profile_dropdown')
        if not profile_dropdown:
            return
        
        try:
            # 현재 프로파일 목록 가져오기
            profiles = self.get_profile_list()
            current_profile = self.get_current_profile()
            
            # 드롭다운 값 업데이트
            profile_dropdown.configure(values=profiles)
            
            # 현재 프로파일이 목록에 있으면 선택
            if current_profile in profiles:
                profile_dropdown.set(current_profile)
            elif profiles:
                profile_dropdown.set(profiles[0])
                self._on_profile_select(profiles[0])
                
        except Exception as e:
            print(f"프로파일 드롭다운 업데이트 오류: {e}")
    
    def set_profile(self, profile_name: str) -> bool:
        """프로파일 설정"""
        try:
            profiles = self.get_profile_list()
            
            if profile_name not in profiles:
                print(f"프로파일 '{profile_name}'을 찾을 수 없습니다.")
                return False
            
            self.current_profile = profile_name
            
            # 프로파일 컨트롤러에 설정
            self.parent.profile_controller.set_current_profile(profile_name)
            
            # UI 업데이트
            profile_dropdown = self.parent.widgets.get('profile_dropdown')
            if profile_dropdown:
                profile_dropdown.set(profile_name)
            
            # 콜백 호출
            if self.parent.on_profile_change:
                self.parent.on_profile_change(profile_name)
            
            return True
            
        except Exception as e:
            print(f"프로파일 설정 오류: {e}")
            return False
    
    def refresh_profiles(self):
        """프로파일 목록 새로고침"""
        try:
            # 프로파일 컨트롤러에서 최신 목록 가져오기
            self.parent.profile_controller.refresh_profiles()
            
            # UI 업데이트
            self.update_profile_dropdown()
            
        except Exception as e:
            print(f"프로파일 새로고침 오류: {e}")
    
    def get_profile_info(self, profile_name: Optional[str] = None) -> dict:
        """프로파일 정보 조회"""
        try:
            if profile_name is None:
                profile_name = self.current_profile
            
            profile_info = self.parent.profile_controller.get_profile_info(profile_name)
            return profile_info if profile_info else {}
            
        except Exception as e:
            print(f"프로파일 정보 조회 오류: {e}")
            return {}
    
    def create_profile_status_display(self) -> Optional[str]:
        """현재 프로파일 상태 표시용 텍스트 생성"""
        try:
            profile_info = self.get_profile_info()
            
            if not profile_info:
                return f"프로파일: {self.current_profile}"
            
            # 프로파일 설정 요약
            settings_count = len(profile_info.get('settings', {}))
            rules_count = len(profile_info.get('rules', []))
            
            return f"프로파일: {self.current_profile} ({settings_count}설정, {rules_count}규칙)"
            
        except Exception:
            return f"프로파일: {self.current_profile}"
    
    def validate_current_profile(self) -> bool:
        """현재 프로파일 유효성 검사"""
        try:
            profiles = self.get_profile_list()
            
            if self.current_profile not in profiles:
                # 현재 프로파일이 없으면 기본값으로 변경
                if profiles:
                    self.set_profile(profiles[0])
                else:
                    self.set_profile("default")
                return False
            
            return True
            
        except Exception:
            return False