# src/ui/views/settings/alarm_tab.py
"""
환경설정 뷰 - 알람 설정 탭

이 모듈은 알람 설정 탭의 UI 생성과 관련 기능을 담당합니다.
- 알람 기능 활성화/비활성화
- 오류 수준별 알람 설정
- 문제 유형별 알람 (DPI, 잉크 커버리지, 폰트, 재단선)
- 처리 상태 알람
- 알림 방식 설정 (시스템 알림, 소리, 팝업)
- 방해 금지 시간 설정

AI 친화적 설계:
- 가장 복잡한 탭을 체계적으로 분할
- 섹션별 UI 생성 함수
- 알람 테스트 기능 포함
"""

import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from tkinter import messagebox
from ....config.alarm_config import AlarmConditionType
from ....utils.alarm_manager import get_alarm_manager


class AlarmTabHelper:
    """알람 설정 탭 헬퍼 클래스"""
    
    @staticmethod
    def create_tab(parent: ctk.CTkFrame, widgets: Dict[str, Any]) -> ctk.CTkLabel:
        """
        알람 탭 생성
        
        Args:
            parent: 부모 프레임 (탭 프레임)
            widgets: 위젯 딕셔너리 (참조로 전달)
            
        Returns:
            volume_label: 볼륨 표시 레이블
        """
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 알람 활성화 섹션
        AlarmTabHelper._create_enable_section(scroll_frame, widgets)
        
        # 오류 수준별 알람 섹션
        AlarmTabHelper._create_error_level_section(scroll_frame, widgets)
        
        # 문제 유형별 알람 섹션
        AlarmTabHelper._create_issue_type_section(scroll_frame, widgets)
        
        # 처리 상태 알람 섹션
        AlarmTabHelper._create_processing_status_section(scroll_frame, widgets)
        
        # 알림 방식 섹션
        volume_label = AlarmTabHelper._create_notification_method_section(scroll_frame, widgets)
        
        # 방해 금지 시간 섹션
        AlarmTabHelper._create_quiet_hours_section(scroll_frame, widgets)
        
        # 테스트 버튼 섹션
        AlarmTabHelper._create_test_section(scroll_frame)
        
        return volume_label
    
    @staticmethod
    def _create_enable_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """알람 활성화 섹션 생성"""
        widgets['alarm_enabled'] = ctk.CTkCheckBox(
            parent,
            text="알람 기능 사용",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        widgets['alarm_enabled'].pack(fill='x', pady=(0, 20))
    
    @staticmethod
    def _create_error_level_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """오류 수준별 알람 섹션 생성"""
        # 제목
        error_label = ctk.CTkLabel(
            parent,
            text="오류 수준별 알람",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        error_label.pack(fill='x', pady=(0, 10))
        
        # 오류 수준별 체크박스들
        error_frame = ctk.CTkFrame(parent, fg_color="transparent")
        error_frame.pack(fill='x', pady=(0, 15))
        
        widgets['alarm_on_warning'] = ctk.CTkCheckBox(
            error_frame,
            text="경고(WARNING) 발생 시 알람"
        )
        widgets['alarm_on_warning'].pack(fill='x', pady=5)
        
        widgets['alarm_on_error'] = ctk.CTkCheckBox(
            error_frame,
            text="오류(ERROR) 발생 시 알람"
        )
        widgets['alarm_on_error'].pack(fill='x', pady=5)
        
        widgets['alarm_on_critical'] = ctk.CTkCheckBox(
            error_frame,
            text="심각(CRITICAL) 발생 시 알람"
        )
        widgets['alarm_on_critical'].pack(fill='x', pady=5)
    
    @staticmethod
    def _create_issue_type_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """문제 유형별 알람 섹션 생성"""
        # 제목
        issue_label = ctk.CTkLabel(
            parent,
            text="문제 유형별 알람",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        issue_label.pack(fill='x', pady=(20, 10))
        
        # DPI 알람 설정
        AlarmTabHelper._create_dpi_alarm_section(parent, widgets)
        
        # 잉크 커버리지 알람 설정
        AlarmTabHelper._create_ink_coverage_alarm_section(parent, widgets)
        
        # 기타 문제 알람
        widgets['alarm_font_issue'] = ctk.CTkCheckBox(
            parent,
            text="폰트 문제 알람 (임베딩되지 않은 폰트)"
        )
        widgets['alarm_font_issue'].pack(fill='x', pady=5)
        
        widgets['alarm_bleed_issue'] = ctk.CTkCheckBox(
            parent,
            text="재단선 문제 알람"
        )
        widgets['alarm_bleed_issue'].pack(fill='x', pady=5)
    
    @staticmethod
    def _create_dpi_alarm_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """DPI 알람 섹션 생성"""
        # DPI 알람 프레임
        dpi_frame = ctk.CTkFrame(parent)
        dpi_frame.pack(fill='x', pady=(0, 10))
        
        dpi_header = ctk.CTkFrame(dpi_frame, fg_color="transparent")
        dpi_header.pack(fill='x', padx=10, pady=(10, 5))
        
        widgets['alarm_low_dpi'] = ctk.CTkCheckBox(
            dpi_header,
            text="낮은 DPI 알람"
        )
        widgets['alarm_low_dpi'].pack(side='left')
        
        # DPI 임계값 설정
        dpi_threshold_frame = ctk.CTkFrame(dpi_frame, fg_color="transparent")
        dpi_threshold_frame.pack(fill='x', padx=30, pady=(0, 10))
        
        ctk.CTkLabel(dpi_threshold_frame, text="임계값(DPI):").pack(side='left')
        widgets['alarm_dpi_threshold'] = ctk.CTkEntry(
            dpi_threshold_frame,
            width=80,
            placeholder_text="300"
        )
        widgets['alarm_dpi_threshold'].pack(side='left', padx=(10, 0))
    
    @staticmethod
    def _create_ink_coverage_alarm_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """잉크 커버리지 알람 섹션 생성"""
        # 잉크 커버리지 알람 프레임
        ink_frame = ctk.CTkFrame(parent)
        ink_frame.pack(fill='x', pady=(0, 10))
        
        ink_header = ctk.CTkFrame(ink_frame, fg_color="transparent")
        ink_header.pack(fill='x', padx=10, pady=(10, 5))
        
        widgets['alarm_ink_coverage'] = ctk.CTkCheckBox(
            ink_header,
            text="잉크 커버리지 초과 알람"
        )
        widgets['alarm_ink_coverage'].pack(side='left')
        
        # 잉크 커버리지 임계값 설정
        ink_threshold_frame = ctk.CTkFrame(ink_frame, fg_color="transparent")
        ink_threshold_frame.pack(fill='x', padx=30, pady=(0, 10))
        
        ctk.CTkLabel(ink_threshold_frame, text="임계값(%):").pack(side='left')
        widgets['alarm_ink_threshold'] = ctk.CTkEntry(
            ink_threshold_frame,
            width=80,
            placeholder_text="320"
        )
        widgets['alarm_ink_threshold'].pack(side='left', padx=(10, 0))
    
    @staticmethod
    def _create_processing_status_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """처리 상태 알람 섹션 생성"""
        # 제목
        status_label = ctk.CTkLabel(
            parent,
            text="처리 상태 알람",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_label.pack(fill='x', pady=(20, 10))
        
        # 처리 상태별 체크박스들
        widgets['alarm_processing_complete'] = ctk.CTkCheckBox(
            parent,
            text="파일 처리 완료 시 알람"
        )
        widgets['alarm_processing_complete'].pack(fill='x', pady=5)
        
        widgets['alarm_processing_failed'] = ctk.CTkCheckBox(
            parent,
            text="파일 처리 실패 시 알람"
        )
        widgets['alarm_processing_failed'].pack(fill='x', pady=5)
        
        widgets['alarm_batch_complete'] = ctk.CTkCheckBox(
            parent,
            text="배치 처리 완료 시 알람"
        )
        widgets['alarm_batch_complete'].pack(fill='x', pady=5)
    
    @staticmethod
    def _create_notification_method_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> ctk.CTkLabel:
        """알림 방식 섹션 생성"""
        # 제목
        method_label = ctk.CTkLabel(
            parent,
            text="알림 방식",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        method_label.pack(fill='x', pady=(20, 10))
        
        # 알림 방식별 체크박스들
        widgets['notification_system'] = ctk.CTkCheckBox(
            parent,
            text="Windows 시스템 알림 사용"
        )
        widgets['notification_system'].pack(fill='x', pady=5)
        
        widgets['notification_sound'] = ctk.CTkCheckBox(
            parent,
            text="소리 알림 사용"
        )
        widgets['notification_sound'].pack(fill='x', pady=5)
        
        # 소리 볼륨 설정
        volume_frame = ctk.CTkFrame(parent, fg_color="transparent")
        volume_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(volume_frame, text="알림음 볼륨:", width=100).pack(side='left')
        widgets['alarm_volume'] = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            width=200
        )
        widgets['alarm_volume'].pack(side='left', padx=(0, 10))
        
        volume_label = ctk.CTkLabel(volume_frame, text="50%")
        volume_label.pack(side='left')
        
        widgets['alarm_volume'].configure(
            command=lambda v: volume_label.configure(text=f"{int(v)}%")
        )
        
        # 팝업 대화상자
        widgets['notification_popup'] = ctk.CTkCheckBox(
            parent,
            text="팝업 대화상자 사용"
        )
        widgets['notification_popup'].pack(fill='x', pady=5)
        
        return volume_label
    
    @staticmethod
    def _create_quiet_hours_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """방해 금지 시간 섹션 생성"""
        # 제목
        quiet_label = ctk.CTkLabel(
            parent,
            text="방해 금지 시간",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        quiet_label.pack(fill='x', pady=(20, 10))
        
        # 방해 금지 시간 사용
        widgets['quiet_hours_enabled'] = ctk.CTkCheckBox(
            parent,
            text="방해 금지 시간 사용"
        )
        widgets['quiet_hours_enabled'].pack(fill='x', pady=5)
        
        # 시간 설정
        quiet_time_frame = ctk.CTkFrame(parent, fg_color="transparent")
        quiet_time_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(quiet_time_frame, text="시작:").pack(side='left')
        widgets['quiet_hours_start'] = ctk.CTkEntry(
            quiet_time_frame,
            width=80,
            placeholder_text="22:00"
        )
        widgets['quiet_hours_start'].pack(side='left', padx=(5, 20))
        
        ctk.CTkLabel(quiet_time_frame, text="종료:").pack(side='left')
        widgets['quiet_hours_end'] = ctk.CTkEntry(
            quiet_time_frame,
            width=80,
            placeholder_text="07:00"
        )
        widgets['quiet_hours_end'].pack(side='left', padx=(5, 0))
    
    @staticmethod
    def _create_test_section(parent: ctk.CTkScrollableFrame) -> None:
        """테스트 버튼 섹션 생성"""
        # 테스트 프레임
        test_frame = ctk.CTkFrame(parent, fg_color="transparent")
        test_frame.pack(fill='x', pady=20)
        
        test_btn = ctk.CTkButton(
            test_frame,
            text="알람 테스트",
            command=AlarmTabHelper._test_alarm
        )
        test_btn.pack()
    
    @staticmethod
    def _test_alarm():
        """알람 테스트"""
        # 알람 매니저 가져오기
        alarm_manager = get_alarm_manager()
        
        # 테스트 알람 발송
        result = alarm_manager.test_notification(AlarmConditionType.PROCESSING_COMPLETE)
        
        if result:
            messagebox.showinfo("테스트", "알람 테스트가 성공적으로 발송되었습니다.")
        else:
            messagebox.showwarning("테스트", "알람이 비활성화되어 있거나 설정이 올바르지 않습니다.")
    
    @staticmethod
    def load_settings(widgets: Dict[str, Any], settings, volume_label: ctk.CTkLabel) -> None:
        """알람 설정 로드 - 기본적인 체크박스들만 처리"""
        # 여기서는 알람 관련 기본 설정만 로드
        # 실제 구현에서는 settings 객체의 알람 설정 속성들을 확인해야 함
        
        # 볼륨 설정 예시
        if hasattr(settings, 'alarm_volume'):
            widgets['alarm_volume'].set(settings.alarm_volume)
            volume_label.configure(text=f"{settings.alarm_volume}%")
        else:
            widgets['alarm_volume'].set(50)
            volume_label.configure(text="50%")
    
    @staticmethod
    def collect_settings(widgets: Dict[str, Any]) -> Dict[str, Any]:
        """알람 설정 수집"""
        settings = {}
        
        # 기본 알람 설정들
        alarm_keys = [
            'alarm_enabled', 'alarm_on_warning', 'alarm_on_error', 'alarm_on_critical',
            'alarm_low_dpi', 'alarm_ink_coverage', 'alarm_font_issue', 'alarm_bleed_issue',
            'alarm_processing_complete', 'alarm_processing_failed', 'alarm_batch_complete',
            'notification_system', 'notification_sound', 'notification_popup',
            'quiet_hours_enabled'
        ]
        
        for key in alarm_keys:
            if key in widgets:
                settings[key] = widgets[key].get()
        
        # 임계값들
        try:
            settings['alarm_dpi_threshold'] = int(widgets['alarm_dpi_threshold'].get()) if widgets['alarm_dpi_threshold'].get() else 300
        except:
            settings['alarm_dpi_threshold'] = 300
            
        try:
            settings['alarm_ink_threshold'] = int(widgets['alarm_ink_threshold'].get()) if widgets['alarm_ink_threshold'].get() else 320
        except:
            settings['alarm_ink_threshold'] = 320
        
        # 볼륨
        settings['alarm_volume'] = int(widgets['alarm_volume'].get())
        
        # 방해 금지 시간
        settings['quiet_hours_start'] = widgets['quiet_hours_start'].get() if widgets['quiet_hours_start'].get() else "22:00"
        settings['quiet_hours_end'] = widgets['quiet_hours_end'].get() if widgets['quiet_hours_end'].get() else "07:00"
        
        return settings