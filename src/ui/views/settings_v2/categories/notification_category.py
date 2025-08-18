# src/ui/views/settings_v2/categories/notification_category.py
"""
알림 설정 카테고리

알림 조건, 소리 설정, 조용한 시간대 등 알림 관련 설정 관리
"""

import customtkinter as ctk
from typing import Dict, Any
from ..base_category import BaseCategory


class NotificationCategory(BaseCategory):
    """
    알림 설정 카테고리
    
    - 알림 조건별 설정
    - 소리 설정
    - 조용한 시간대
    - 알림 히스토리
    """
    
    def _on_widget_change(self, widget_id: str, value: Any):
        """위젯 값 변경 이벤트 - 개선된 alarm_settings 처리"""
        # original_values 추적 (BaseCategory 기능 유지)
        if widget_id not in self.original_values:
            self.original_values[widget_id] = value
        
        # 개별 설정 업데이트 (다른 카테고리와 통일)
        if self.on_setting_change:
            # alarm 관련 설정인지 확인
            if widget_id.startswith(('alarm_', 'condition_', 'sound_', 'quiet_', 
                                    'notification_method_', 'keep_notification_',
                                    'max_history_', 'cooldown_', 'max_notifications_')):
                # alarm_settings 전체를 재구성하여 업데이트
                self._update_alarm_settings()
            else:
                # 일반 설정은 개별 업데이트
                self.on_setting_change(widget_id, value)
    
    def _update_alarm_settings(self):
        """alarm_settings 전체를 재구성하여 업데이트"""
        settings_dict = self.get_settings()
        if "alarm_settings" in settings_dict:
            try:
                from src.config.alarm_config import AlarmSettings
                alarm_obj = AlarmSettings.from_dict(settings_dict["alarm_settings"])
                self.on_setting_change("alarm_settings", alarm_obj)
            except Exception as e:
                # 오류 발생 시 로깅 (실제 구현 시 로거 사용)
                print(f"알람 설정 업데이트 오류: {e}")
    
    def _create_ui(self):
        """UI 생성"""
        # 알림 활성화 섹션
        self._create_enable_section()
        
        # 알림 조건 섹션
        self._create_conditions_section()
        
        # 소리 설정 섹션
        self._create_sound_section()
        
        # 조용한 시간대 섹션
        self._create_quiet_hours_section()
        
        # 알림 히스토리 섹션
        self._create_history_section()
    
    def _create_enable_section(self):
        """알림 활성화 섹션"""
        section = self.create_section("알림 설정", "🔔")
        
        # 마스터 스위치
        master_frame = ctk.CTkFrame(section, fg_color="transparent")
        master_frame.pack(fill='x', pady=5)
        
        self.master_switch = ctk.CTkSwitch(
            master_frame,
            text="알림 시스템 활성화",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._on_master_switch_change()
        )
        self.master_switch.pack(side='left')
        self.widgets['alarm_enabled'] = self.master_switch
        
        # 알림 방법 선택
        method_frame = ctk.CTkFrame(section, fg_color="transparent")
        method_frame.pack(fill='x', pady=(15, 5))
        
        ctk.CTkLabel(
            method_frame,
            text="기본 알림 방법:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        # 체크박스들
        methods_container = ctk.CTkFrame(method_frame, fg_color="transparent")
        methods_container.pack(side='left')
        
        self.method_checkboxes = {}
        methods = [
            ("system", "시스템 알림"),
            ("sound", "소리"),
            ("tray", "트레이 아이콘"),
            ("log", "로그 기록")
        ]
        
        for method_id, method_name in methods:
            cb = ctk.CTkCheckBox(
                methods_container,
                text=method_name,
                width=100,
                command=lambda m=method_id: self._on_notification_method_change(m)
            )
            cb.pack(side='left', padx=5)
            self.method_checkboxes[method_id] = cb
            self.widgets[f'notification_method_{method_id}'] = cb
    
    def _create_conditions_section(self):
        """알림 조건 섹션"""
        section = self.create_section("알림 조건", "⚠️")
        
        # 조건별 설정
        conditions = [
            ("error_level", "심각한 오류 발생", "에러 레벨", 5),
            ("low_dpi", "낮은 이미지 해상도", "최소 DPI", 300),
            ("ink_coverage", "과도한 잉크 커버리지", "최대 %", 320),
            ("font_issue", "폰트 문제 발견", None, None),
            ("processing_complete", "처리 완료", None, None),
            ("processing_failed", "처리 실패", None, None),
            ("batch_complete", "일괄 처리 완료", None, None)
        ]
        
        for cond_id, cond_name, threshold_label, threshold_default in conditions:
            self._create_condition_row(section, cond_id, cond_name, threshold_label, threshold_default)
    
    def _create_condition_row(self, parent, cond_id: str, name: str, 
                             threshold_label: str = None, threshold_default: Any = None):
        """알림 조건 행 생성"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill='x', pady=3)
        
        # 활성화 체크박스
        checkbox = ctk.CTkCheckBox(
            row_frame,
            text=name,
            width=200,
            command=lambda: self._on_condition_change(cond_id)
        )
        checkbox.pack(side='left')
        self.widgets[f'condition_{cond_id}_enabled'] = checkbox
        
        # 임계값 입력 (있는 경우)
        if threshold_label:
            ctk.CTkLabel(
                row_frame,
                text=threshold_label + ":",
                width=80
            ).pack(side='left', padx=(20, 5))
            
            entry = ctk.CTkEntry(
                row_frame,
                width=60,
                height=28,
                placeholder_text=str(threshold_default)
            )
            entry.pack(side='left')
            entry.bind('<Return>', lambda e: self._on_threshold_change(cond_id, entry.get()))
            entry.bind('<FocusOut>', lambda e: self._on_threshold_change(cond_id, entry.get()))
            self.widgets[f'condition_{cond_id}_threshold'] = entry
    
    def _create_sound_section(self):
        """소리 설정 섹션"""
        section = self.create_section("소리 설정", "🔊")
        
        # 소리 활성화
        self.create_option_row(
            section,
            "알림음 재생:",
            "switch",
            "sound_enabled"
        )
        
        # 볼륨
        volume_frame = ctk.CTkFrame(section, fg_color="transparent")
        volume_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            volume_frame,
            text="볼륨:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        volume_container = ctk.CTkFrame(volume_frame, fg_color="transparent")
        volume_container.pack(side='left')
        
        self.volume_slider = ctk.CTkSlider(
            volume_container,
            from_=0,
            to=100,
            width=150,
            command=self._on_volume_change
        )
        self.volume_slider.pack(side='left')
        
        self.volume_label = ctk.CTkLabel(
            volume_container,
            text="50%",
            width=40
        )
        self.volume_label.pack(side='left', padx=(10, 0))
        
        self.widgets['sound_volume'] = self.volume_slider
        
        # 사운드 파일 선택
        sound_frame = ctk.CTkFrame(section, fg_color="transparent")
        sound_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            sound_frame,
            text="알림음:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.sound_combo = ctk.CTkComboBox(
            sound_frame,
            values=["기본", "차임벨", "알림", "경고", "사용자 지정..."],
            width=150,
            command=self._on_sound_select
        )
        self.sound_combo.pack(side='left')
        self.widgets['default_sound'] = self.sound_combo
        
        # 테스트 버튼
        test_btn = ctk.CTkButton(
            sound_frame,
            text="▶ 테스트",
            width=80,
            command=self._test_sound
        )
        test_btn.pack(side='left', padx=(10, 0))
    
    def _create_quiet_hours_section(self):
        """조용한 시간대 섹션"""
        section = self.create_section("조용한 시간", "🌙")
        
        # 조용한 시간 활성화
        self.create_option_row(
            section,
            "조용한 시간대 사용:",
            "switch",
            "quiet_hours_enabled"
        )
        
        # 시간 설정
        time_frame = ctk.CTkFrame(section, fg_color="transparent")
        time_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            time_frame,
            text="시작 시간:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.start_time_entry = ctk.CTkEntry(
            time_frame,
            width=80,
            placeholder_text="22:00"
        )
        self.start_time_entry.pack(side='left')
        self.widgets['quiet_hours_start'] = self.start_time_entry
        
        ctk.CTkLabel(
            time_frame,
            text="~",
            width=20
        ).pack(side='left', padx=10)
        
        self.end_time_entry = ctk.CTkEntry(
            time_frame,
            width=80,
            placeholder_text="07:00"
        )
        self.end_time_entry.pack(side='left')
        self.widgets['quiet_hours_end'] = self.end_time_entry
        
        # 조용한 시간 동안의 동작
        behavior_frame = ctk.CTkFrame(section, fg_color="transparent")
        behavior_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            behavior_frame,
            text="조용한 시간 동작:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.quiet_behavior = ctk.CTkComboBox(
            behavior_frame,
            values=["모든 알림 끄기", "소리만 끄기", "중요한 알림만"],
            width=150
        )
        self.quiet_behavior.pack(side='left')
        self.widgets['quiet_hours_behavior'] = self.quiet_behavior
    
    def _create_history_section(self):
        """알림 히스토리 섹션"""
        section = self.create_section("알림 기록", "📜")
        
        # 히스토리 저장
        self.create_option_row(
            section,
            "알림 기록 저장:",
            "switch",
            "keep_notification_history"
        )
        
        # 최대 저장 개수
        max_items_frame = ctk.CTkFrame(section, fg_color="transparent")
        max_items_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            max_items_frame,
            text="최대 저장 개수:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.max_items_entry = ctk.CTkEntry(
            max_items_frame,
            width=100,
            placeholder_text="1000"
        )
        self.max_items_entry.pack(side='left')
        self.widgets['max_history_items'] = self.max_items_entry
        
        # 쿨다운 설정
        cooldown_frame = ctk.CTkFrame(section, fg_color="transparent")
        cooldown_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            cooldown_frame,
            text="알림 쿨다운(초):",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.cooldown_entry = ctk.CTkEntry(
            cooldown_frame,
            width=100,
            placeholder_text="60"
        )
        self.cooldown_entry.pack(side='left')
        self.widgets['cooldown_seconds'] = self.cooldown_entry
        
        # 분당 최대 알림
        max_per_min_frame = ctk.CTkFrame(section, fg_color="transparent")
        max_per_min_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            max_per_min_frame,
            text="분당 최대 알림 수:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.max_per_min_entry = ctk.CTkEntry(
            max_per_min_frame,
            width=100,
            placeholder_text="10"
        )
        self.max_per_min_entry.pack(side='left')
        self.widgets['max_notifications_per_minute'] = self.max_per_min_entry
    
    def _on_master_switch_change(self):
        """마스터 스위치 변경"""
        enabled = self.master_switch.get()
        self._on_widget_change("alarm_enabled", enabled)
        
        # 다른 위젯들 활성화/비활성화
        # (구현 선택사항)
    
    def _on_notification_method_change(self, method_id: str):
        """알림 방법 변경"""
        # _on_widget_change가 처리함
        self._on_widget_change(f"notification_method_{method_id}", self.method_checkboxes[method_id].get())
    
    def _on_condition_change(self, cond_id: str):
        """알림 조건 변경"""
        enabled = self.widgets[f'condition_{cond_id}_enabled'].get()
        self._on_widget_change(f'condition_{cond_id}_enabled', enabled)
    
    def _on_threshold_change(self, cond_id: str, value: str):
        """임계값 변경"""
        try:
            threshold_value = int(value) if value else None
            self._on_widget_change(f'condition_{cond_id}_threshold', threshold_value)
        except ValueError:
            pass
    
    def _on_volume_change(self, value: float):
        """볼륨 변경"""
        volume = int(value)
        self.volume_label.configure(text=f"{volume}%")
        self._on_widget_change("sound_volume", volume)
    
    def _on_sound_select(self, sound: str):
        """알림음 선택"""
        if sound == "사용자 지정...":
            # 파일 선택 다이얼로그
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="알림음 선택",
                filetypes=[("Wave 파일", "*.wav"), ("모든 파일", "*.*")]
            )
            if file_path:
                self._on_widget_change("custom_sound", file_path)
        else:
            self._on_widget_change("default_sound", sound)
    
    def _test_sound(self):
        """알림음 테스트"""
        # 실제 구현 시 소리 재생
        from tkinter import messagebox
        messagebox.showinfo("테스트", "알림음이 재생됩니다.")
    
    def load_settings(self, settings):
        """설정 로드"""
        # 알림 설정
        if hasattr(settings, 'alarm_settings') and settings.alarm_settings:
            alarm = settings.alarm_settings
            
            # 마스터 스위치
            if hasattr(alarm, 'enabled'):
                if alarm.enabled:
                    self.master_switch.select()
                else:
                    self.master_switch.deselect()
            
            # 알림 방법
            if hasattr(alarm, 'default_notification_methods'):
                # NotificationMethod enum을 문자열로 변환
                methods = [m.value if hasattr(m, 'value') else m for m in alarm.default_notification_methods]
            else:
                methods = ['system']
            
            for method_id, checkbox in self.method_checkboxes.items():
                if method_id in methods:
                    checkbox.select()
                else:
                    checkbox.deselect()
            
            # 조건별 설정
            if hasattr(alarm, 'conditions'):
                # AlarmConditionType enum을 문자열로 변환하여 처리
                for condition_type, condition in alarm.conditions.items():
                    # enum의 value를 가져옴
                    cond_id = condition_type.value if hasattr(condition_type, 'value') else str(condition_type)
                    
                    # 활성화 상태
                    enabled_widget = self.widgets.get(f'condition_{cond_id}_enabled')
                    if enabled_widget and hasattr(condition, 'enabled'):
                        if condition.enabled:
                            enabled_widget.select()
                        else:
                            enabled_widget.deselect()
                    
                    # 임계값
                    threshold_widget = self.widgets.get(f'condition_{cond_id}_threshold')
                    if threshold_widget and hasattr(condition, 'threshold_value') and condition.threshold_value is not None:
                        threshold_widget.insert(0, str(condition.threshold_value))
            
            # 소리 설정
            if hasattr(alarm, 'sound_settings') and alarm.sound_settings:
                sound = alarm.sound_settings
                
                if hasattr(sound, 'enabled'):
                    if sound.enabled:
                        self.widgets['sound_enabled'].select()
                    else:
                        self.widgets['sound_enabled'].deselect()
                
                if hasattr(sound, 'volume'):
                    self.volume_slider.set(sound.volume)
                    self.volume_label.configure(text=f"{sound.volume}%")
                
                if hasattr(sound, 'default_sound') and sound.default_sound:
                    # 기본 사운드 파일명에 따라 콤보박스 설정
                    if sound.default_sound == 'default.wav':
                        self.sound_combo.set("기본")
                    else:
                        self.sound_combo.set("기본")
            
            # 조용한 시간
            if hasattr(alarm, 'quiet_hours_enabled'):
                if alarm.quiet_hours_enabled:
                    self.widgets['quiet_hours_enabled'].select()
                else:
                    self.widgets['quiet_hours_enabled'].deselect()
            
            if hasattr(alarm, 'quiet_hours_start') and alarm.quiet_hours_start:
                self.start_time_entry.insert(0, alarm.quiet_hours_start)
            
            if hasattr(alarm, 'quiet_hours_end') and alarm.quiet_hours_end:
                self.end_time_entry.insert(0, alarm.quiet_hours_end)
            
            # 히스토리
            if hasattr(alarm, 'keep_notification_history'):
                if alarm.keep_notification_history:
                    self.widgets['keep_notification_history'].select()
                else:
                    self.widgets['keep_notification_history'].deselect()
            
            if hasattr(alarm, 'max_history_items') and alarm.max_history_items:
                self.max_items_entry.insert(0, str(alarm.max_history_items))
            
            if hasattr(alarm, 'cooldown_seconds') and alarm.cooldown_seconds:
                self.cooldown_entry.insert(0, str(alarm.cooldown_seconds))
            
            if hasattr(alarm, 'max_notifications_per_minute') and alarm.max_notifications_per_minute:
                self.max_per_min_entry.insert(0, str(alarm.max_notifications_per_minute))
    
    def get_settings(self) -> Dict[str, Any]:
        """현재 설정 값 반환"""
        settings = {'alarm_settings': {}}
        alarm = settings['alarm_settings']
        
        # 마스터 스위치
        alarm['enabled'] = self.master_switch.get()
        
        # 알림 방법
        methods = []
        for method_id, checkbox in self.method_checkboxes.items():
            if checkbox.get():
                methods.append(method_id)
        alarm['default_notification_methods'] = methods
        
        # 조건별 설정
        conditions = {}
        condition_ids = ['error_level', 'low_dpi', 'ink_coverage', 'font_issue',
                        'processing_complete', 'processing_failed', 'batch_complete']
        
        for cond_id in condition_ids:
            cond_data = {}
            
            # 활성화 상태
            enabled_widget = self.widgets.get(f'condition_{cond_id}_enabled')
            if enabled_widget:
                cond_data['enabled'] = enabled_widget.get()
            
            # 임계값
            threshold_widget = self.widgets.get(f'condition_{cond_id}_threshold')
            if threshold_widget:
                value = threshold_widget.get()
                try:
                    cond_data['threshold_value'] = int(value) if value else None
                except ValueError:
                    cond_data['threshold_value'] = None
            
            conditions[cond_id] = cond_data
        
        alarm['conditions'] = conditions
        
        # 소리 설정
        alarm['sound_settings'] = {
            'enabled': self.widgets['sound_enabled'].get(),
            'volume': int(self.volume_slider.get()),
            'default_sound': self.sound_combo.get()
        }
        
        # 조용한 시간
        alarm['quiet_hours_enabled'] = self.widgets['quiet_hours_enabled'].get()
        alarm['quiet_hours_start'] = self.start_time_entry.get()
        alarm['quiet_hours_end'] = self.end_time_entry.get()
        
        # 히스토리
        alarm['keep_notification_history'] = self.widgets['keep_notification_history'].get()
        
        max_items = self.max_items_entry.get()
        alarm['max_history_items'] = int(max_items) if max_items else 1000
        
        cooldown = self.cooldown_entry.get()
        alarm['cooldown_seconds'] = int(cooldown) if cooldown else 60
        
        max_per_min = self.max_per_min_entry.get()
        alarm['max_notifications_per_minute'] = int(max_per_min) if max_per_min else 10
        
        return settings