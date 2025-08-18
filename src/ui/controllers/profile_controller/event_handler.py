# src/ui/controllers/profile_controller/event_handler.py
"""
프로파일 이벤트 처리

프로파일 관련 이벤트 처리 및 콜백 관리를 담당합니다.
"""

from typing import Optional, Callable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import ProfileControllerBase


class ProfileEventHandler:
    """프로파일 이벤트 처리 클래스"""
    
    def __init__(self, parent: 'ProfileControllerBase'):
        self.parent = parent
        
        # 이벤트 콜백들
        self.on_profile_created: Optional[Callable[[str], None]] = None
        self.on_profile_updated: Optional[Callable[[str], None]] = None
        self.on_profile_deleted: Optional[Callable[[str], None]] = None
        self.on_profile_imported: Optional[Callable[[str], None]] = None
        self.on_profile_exported: Optional[Callable[[str], None]] = None
        self.on_current_profile_changed: Optional[Callable[[str], None]] = None
        self.on_rules_updated: Optional[Callable[[str, list], None]] = None
        self.on_quality_standards_updated: Optional[Callable[[str, dict], None]] = None
    
    def set_event_callbacks(self,
                          on_created: Optional[Callable] = None,
                          on_updated: Optional[Callable] = None,
                          on_deleted: Optional[Callable] = None,
                          on_imported: Optional[Callable] = None,
                          on_exported: Optional[Callable] = None,
                          on_current_changed: Optional[Callable] = None,
                          on_rules_updated: Optional[Callable] = None,
                          on_quality_updated: Optional[Callable] = None):
        """이벤트 콜백 설정"""
        if on_created:
            self.on_profile_created = on_created
        if on_updated:
            self.on_profile_updated = on_updated
        if on_deleted:
            self.on_profile_deleted = on_deleted
        if on_imported:
            self.on_profile_imported = on_imported
        if on_exported:
            self.on_profile_exported = on_exported
        if on_current_changed:
            self.on_current_profile_changed = on_current_changed
        if on_rules_updated:
            self.on_rules_updated = on_rules_updated
        if on_quality_updated:
            self.on_quality_standards_updated = on_quality_updated
    
    def emit_profile_created(self, profile_name: str):
        """프로파일 생성 이벤트 발생"""
        try:
            if self.on_profile_created:
                self.on_profile_created(profile_name)
            self.parent.logger.debug(f"프로파일 생성 이벤트: {profile_name}")
        except Exception as e:
            self.parent.logger.error(f"프로파일 생성 이벤트 처리 실패: {e}")
    
    def emit_profile_updated(self, profile_name: str):
        """프로파일 업데이트 이벤트 발생"""
        try:
            if self.on_profile_updated:
                self.on_profile_updated(profile_name)
            self.parent.logger.debug(f"프로파일 업데이트 이벤트: {profile_name}")
        except Exception as e:
            self.parent.logger.error(f"프로파일 업데이트 이벤트 처리 실패: {e}")
    
    def emit_profile_deleted(self, profile_name: str):
        """프로파일 삭제 이벤트 발생"""
        try:
            if self.on_profile_deleted:
                self.on_profile_deleted(profile_name)
            self.parent.logger.debug(f"프로파일 삭제 이벤트: {profile_name}")
        except Exception as e:
            self.parent.logger.error(f"프로파일 삭제 이벤트 처리 실패: {e}")
    
    def emit_profile_imported(self, profile_name: str):
        """프로파일 가져오기 이벤트 발생"""
        try:
            if self.on_profile_imported:
                self.on_profile_imported(profile_name)
            self.parent.logger.debug(f"프로파일 가져오기 이벤트: {profile_name}")
        except Exception as e:
            self.parent.logger.error(f"프로파일 가져오기 이벤트 처리 실패: {e}")
    
    def emit_profile_exported(self, profile_name: str):
        """프로파일 내보내기 이벤트 발생"""
        try:
            if self.on_profile_exported:
                self.on_profile_exported(profile_name)
            self.parent.logger.debug(f"프로파일 내보내기 이벤트: {profile_name}")
        except Exception as e:
            self.parent.logger.error(f"프로파일 내보내기 이벤트 처리 실패: {e}")
    
    def emit_current_profile_changed(self, profile_name: str):
        """현재 프로파일 변경 이벤트 발생"""
        try:
            if self.on_current_profile_changed:
                self.on_current_profile_changed(profile_name)
            self.parent.logger.debug(f"현재 프로파일 변경 이벤트: {profile_name}")
        except Exception as e:
            self.parent.logger.error(f"현재 프로파일 변경 이벤트 처리 실패: {e}")
    
    def emit_rules_updated(self, profile_name: str, enabled_rules: list):
        """규칙 업데이트 이벤트 발생"""
        try:
            if self.on_rules_updated:
                self.on_rules_updated(profile_name, enabled_rules)
            self.parent.logger.debug(f"규칙 업데이트 이벤트: {profile_name}, {len(enabled_rules)}개 규칙")
        except Exception as e:
            self.parent.logger.error(f"규칙 업데이트 이벤트 처리 실패: {e}")
    
    def emit_quality_standards_updated(self, profile_name: str, standards: dict):
        """품질 기준 업데이트 이벤트 발생"""
        try:
            if self.on_quality_standards_updated:
                self.on_quality_standards_updated(profile_name, standards)
            self.parent.logger.debug(f"품질 기준 업데이트 이벤트: {profile_name}")
        except Exception as e:
            self.parent.logger.error(f"품질 기준 업데이트 이벤트 처리 실패: {e}")
    
    def handle_profile_operation_result(self, operation: str, profile_name: str, success: bool, error_message: str = ""):
        """프로파일 작업 결과 처리"""
        if success:
            # 성공한 작업에 따라 적절한 이벤트 발생
            if operation == "create":
                self.emit_profile_created(profile_name)
            elif operation == "update":
                self.emit_profile_updated(profile_name)
            elif operation == "delete":
                self.emit_profile_deleted(profile_name)
            elif operation == "import":
                self.emit_profile_imported(profile_name)
            elif operation == "export":
                self.emit_profile_exported(profile_name)
            elif operation == "set_current":
                self.emit_current_profile_changed(profile_name)
        else:
            # 실패한 경우 로그 기록
            self.parent.logger.error(f"프로파일 {operation} 실패: {profile_name} - {error_message}")
    
    def get_callback_status(self) -> dict:
        """콜백 설정 상태 조회"""
        return {
            'profile_created': self.on_profile_created is not None,
            'profile_updated': self.on_profile_updated is not None,
            'profile_deleted': self.on_profile_deleted is not None,
            'profile_imported': self.on_profile_imported is not None,
            'profile_exported': self.on_profile_exported is not None,
            'current_profile_changed': self.on_current_profile_changed is not None,
            'rules_updated': self.on_rules_updated is not None,
            'quality_standards_updated': self.on_quality_standards_updated is not None
        }
    
    def clear_all_callbacks(self):
        """모든 콜백 제거"""
        self.on_profile_created = None
        self.on_profile_updated = None
        self.on_profile_deleted = None
        self.on_profile_imported = None
        self.on_profile_exported = None
        self.on_current_profile_changed = None
        self.on_rules_updated = None
        self.on_quality_standards_updated = None
        
        self.parent.logger.debug("모든 프로파일 이벤트 콜백이 제거되었습니다.")
    
    def add_callback_wrapper(self, event_type: str, callback: Callable, wrapper_func: Optional[Callable] = None):
        """콜백 래퍼 추가 (에러 처리, 로깅 등을 위해)"""
        def wrapped_callback(*args, **kwargs):
            try:
                if wrapper_func:
                    wrapper_func(event_type, *args, **kwargs)
                result = callback(*args, **kwargs)
                return result
            except Exception as e:
                self.parent.logger.error(f"콜백 실행 실패 ({event_type}): {e}")
                raise
        
        # 이벤트 타입에 따라 적절한 콜백 설정
        if event_type == "created":
            self.on_profile_created = wrapped_callback
        elif event_type == "updated":
            self.on_profile_updated = wrapped_callback
        elif event_type == "deleted":
            self.on_profile_deleted = wrapped_callback
        # 필요한 경우 다른 이벤트 타입도 추가