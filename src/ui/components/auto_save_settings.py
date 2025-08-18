# -*- coding: utf-8 -*-
"""
자동 저장 설정 컴포넌트

설정 변경 시 자동으로 저장하는 향상된 설정 관리
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
import threading
import time
from pathlib import Path
import json


class AutoSaveSettings:
    """자동 저장 설정 관리자"""
    
    def __init__(self, 
                 settings_file: Path,
                 auto_save_delay: float = 1.0,
                 on_save: Optional[Callable] = None):
        """
        초기화
        
        Args:
            settings_file: 설정 파일 경로
            auto_save_delay: 자동 저장 지연 시간 (초)
            on_save: 저장 시 콜백
        """
        self.settings_file = settings_file
        self.auto_save_delay = auto_save_delay
        self.on_save = on_save
        
        # 설정 데이터
        self.settings: Dict[str, Any] = {}
        self.pending_changes: Dict[str, Any] = {}
        
        # 자동 저장 타이머
        self.save_timer: Optional[threading.Timer] = None
        self.save_lock = threading.Lock()
        
        # 변경 추적
        self.is_modified = False
        self.last_save_time = time.time()
        
        # 초기 로드
        self.load_settings()
        
    def load_settings(self) -> bool:
        """설정 파일 로드"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                return True
            else:
                self.settings = self._get_default_settings()
                self.save_settings()  # 기본 설정 저장
                return True
        except Exception as e:
            print(f"설정 로드 실패: {e}")
            self.settings = self._get_default_settings()
            return False
            
    def save_settings(self) -> bool:
        """설정 파일 저장"""
        try:
            with self.save_lock:
                # 디렉토리 생성
                self.settings_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 백업 생성
                if self.settings_file.exists():
                    backup_file = self.settings_file.with_suffix('.json.bak')
                    import shutil
                    shutil.copy2(self.settings_file, backup_file)
                
                # 저장
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, ensure_ascii=False, indent=2)
                
                self.is_modified = False
                self.last_save_time = time.time()
                
                # 콜백 호출
                if self.on_save:
                    self.on_save()
                    
                return True
                
        except Exception as e:
            print(f"설정 저장 실패: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """설정값 가져오기"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any, auto_save: bool = True):
        """
        설정값 변경
        
        Args:
            key: 설정 키 (점 표기법 지원)
            value: 설정값
            auto_save: 자동 저장 여부
        """
        keys = key.split('.')
        target = self.settings
        
        # 중첩된 딕셔너리 탐색
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
            
        # 값 설정
        old_value = target.get(keys[-1])
        if old_value != value:
            target[keys[-1]] = value
            self.is_modified = True
            
            # 자동 저장 예약
            if auto_save:
                self._schedule_auto_save()
                
    def update(self, updates: Dict[str, Any], auto_save: bool = True):
        """여러 설정 일괄 업데이트"""
        for key, value in updates.items():
            self.set(key, value, auto_save=False)
            
        if auto_save and self.is_modified:
            self._schedule_auto_save()
            
    def _schedule_auto_save(self):
        """자동 저장 예약"""
        # 기존 타이머 취소
        if self.save_timer:
            self.save_timer.cancel()
            
        # 새 타이머 시작
        self.save_timer = threading.Timer(
            self.auto_save_delay,
            self._auto_save
        )
        self.save_timer.daemon = True
        self.save_timer.start()
        
    def _auto_save(self):
        """자동 저장 실행"""
        if self.is_modified:
            self.save_settings()
            
    def _get_default_settings(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            'ui': {
                'theme': 'dark',
                'language': 'ko',
                'sidebar_width': 250,
                'window_geometry': None
            },
            'processing': {
                'default_profile': 'default',
                'auto_fix': False,
                'worker_count': 2,
                'timeout': 300
            },
            'paths': {
                'output': 'output',
                'reports': 'reports',
                'completed': 'completed'
            },
            'notifications': {
                'enabled': True,
                'sound': True
            }
        }
        
    def reset_to_default(self, key: Optional[str] = None):
        """기본값으로 초기화"""
        defaults = self._get_default_settings()
        
        if key:
            # 특정 키만 초기화
            keys = key.split('.')
            default_value = defaults
            for k in keys:
                if k in default_value:
                    default_value = default_value[k]
                else:
                    return
                    
            self.set(key, default_value)
        else:
            # 전체 초기화
            self.settings = defaults
            self.is_modified = True
            self._schedule_auto_save()


class AutoSaveSettingsWidget(ctk.CTkFrame):
    """자동 저장 설정 위젯"""
    
    def __init__(self, parent, settings_manager: AutoSaveSettings, **kwargs):
        """
        초기화
        
        Args:
            parent: 부모 위젯
            settings_manager: 설정 관리자
        """
        super().__init__(parent, **kwargs)
        
        self.settings = settings_manager
        
        # UI 구성
        self._setup_ui()
        
    def _setup_ui(self):
        """UI 구성"""
        # 상태 표시
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="⚫ 설정 자동 저장 활성화",
            font=('Arial', 10),
            anchor='w'
        )
        self.status_label.pack(side='left')
        
        # 저장 표시기
        self.save_indicator = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=('Arial', 10),
            text_color='green'
        )
        self.save_indicator.pack(side='right')
        
        # 설정 변경 시 콜백 등록
        self.settings.on_save = self._on_settings_saved
        
    def _on_settings_saved(self):
        """설정 저장 시 호출"""
        # 저장 애니메이션
        self.save_indicator.configure(text="✅ 저장됨")
        self.status_label.configure(text="🟢 설정 자동 저장 활성화")
        
        # 2초 후 원래대로
        self.after(2000, self._reset_indicator)
        
    def _reset_indicator(self):
        """표시기 초기화"""
        self.save_indicator.configure(text="")
        self.status_label.configure(text="⚫ 설정 자동 저장 활성화")
        
    def show_saving(self):
        """저장 중 표시"""
        self.save_indicator.configure(text="💾 저장 중...")
        
    def show_error(self, message: str):
        """에러 표시"""
        self.save_indicator.configure(
            text=f"❌ {message}",
            text_color='red'
        )
        self.after(3000, self._reset_indicator)