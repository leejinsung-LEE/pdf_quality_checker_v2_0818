# src/config/ui_config.py
"""
UI 모드 설정 관리

Classic(CustomTkinter)과 Modern(Flet) UI 모드를 관리합니다.
"""

import json
import os
import sys
from pathlib import Path
from typing import Literal, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

UIMode = Literal["classic", "modern"]

@dataclass
class UIConfig:
    """UI 설정 데이터 클래스"""
    mode: UIMode = "classic"  # 기본값은 안정적인 classic
    allow_switch: bool = True  # UI 전환 허용 여부
    remember_choice: bool = True  # 선택 기억
    show_selector_on_start: bool = False  # 시작 시 선택 창 표시
    auto_fallback: bool = True  # 오류 시 자동 폴백
    
    # UI별 특수 설정
    classic_settings: dict = None
    modern_settings: dict = None
    
    def __post_init__(self):
        if self.classic_settings is None:
            self.classic_settings = {}
        if self.modern_settings is None:
            self.modern_settings = {}


class UIConfigManager:
    """UI 설정 관리자"""
    
    CONFIG_FILE = "data/ui_config.json"
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> UIConfig:
        """설정 파일 로드"""
        config_path = Path(self.CONFIG_FILE)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return UIConfig(**data)
            except Exception as e:
                logger.warning(f"UI 설정 로드 실패: {e}")
        
        # 기본 설정 반환
        return UIConfig()
    
    def save_config(self):
        """설정 파일 저장"""
        config_path = Path(self.CONFIG_FILE)
        config_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.__dict__, f, indent=2, ensure_ascii=False)
            logger.info(f"UI 설정 저장: {self.config.mode}")
        except Exception as e:
            logger.error(f"UI 설정 저장 실패: {e}")
    
    def get_ui_mode(self) -> UIMode:
        """현재 UI 모드 반환"""
        # 1. 환경 변수 확인 (최우선)
        env_mode = os.environ.get('PDF_CHECKER_UI')
        if env_mode in ['classic', 'modern']:
            logger.info(f"환경 변수로 UI 모드 설정: {env_mode}")
            return env_mode
        
        # 2. 커맨드라인 인자 확인
        import sys
        for i, arg in enumerate(sys.argv):
            if arg == '--ui' and i + 1 < len(sys.argv):
                mode = sys.argv[i + 1]
                if mode in ['classic', 'modern']:
                    logger.info(f"커맨드라인으로 UI 모드 설정: {mode}")
                    if self.config.remember_choice:
                        self.config.mode = mode
                        self.save_config()
                    return mode
        
        # 3. 설정 파일의 값 사용
        return self.config.mode
    
    def set_ui_mode(self, mode: UIMode):
        """UI 모드 설정"""
        if mode in ['classic', 'modern']:
            self.config.mode = mode
            if self.config.remember_choice:
                self.save_config()
            logger.info(f"UI 모드 변경: {mode}")
    
    def should_show_selector(self) -> bool:
        """시작 시 선택 창 표시 여부"""
        # --select 인자가 있으면 무조건 표시
        if '--select' in sys.argv:
            return True
        
        return self.config.show_selector_on_start
    
    def is_mode_available(self, mode: UIMode) -> bool:
        """특정 UI 모드 사용 가능 여부 확인"""
        if mode == "classic":
            try:
                import customtkinter
                import tkinterdnd2
                return True
            except ImportError:
                return False
        
        elif mode == "modern":
            try:
                import flet
                return True
            except ImportError:
                return False
        
        return False
    
    def get_available_modes(self) -> list[UIMode]:
        """사용 가능한 UI 모드 목록"""
        modes = []
        if self.is_mode_available("classic"):
            modes.append("classic")
        if self.is_mode_available("modern"):
            modes.append("modern")
        return modes
    
    def get_fallback_mode(self) -> Optional[UIMode]:
        """폴백 UI 모드 반환"""
        current = self.get_ui_mode()
        
        # 현재 모드가 사용 불가능하면 다른 모드로
        if not self.is_mode_available(current):
            available = self.get_available_modes()
            if available:
                fallback = available[0]
                logger.warning(f"UI 모드 폴백: {current} -> {fallback}")
                return fallback
        
        return None


# 싱글톤 인스턴스
_ui_config_manager = None

def get_ui_config_manager() -> UIConfigManager:
    """UI 설정 관리자 싱글톤 인스턴스 반환"""
    global _ui_config_manager
    if _ui_config_manager is None:
        _ui_config_manager = UIConfigManager()
    return _ui_config_manager