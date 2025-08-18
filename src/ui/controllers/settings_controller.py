# src/ui/controllers/settings_controller.py
"""
설정 관리 컨트롤러 (호환성 래퍼)

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 settings_controller/ 모듈에 분산되어 있습니다.

모듈화된 구조:
- base.py: UserSettings, SettingsControllerBase
- settings_manager.py: 핵심 설정 관리 (get/set/update)
- persistence.py: 파일 I/O (load/save/export/import)  
- validator.py: 설정 검증 및 폴더 유효성 검사
- defaults.py: 기본값 관리 및 초기화
- external_tools.py: 외부 도구 관리
- __init__.py: 통합 및 호환성
"""

# 모든 기능을 settings_controller 모듈에서 임포트
from .settings_controller import (
    SettingsController,
    UserSettings,
    SettingsChangeEvent,
    ValidationResult,
    ToolInfo,
    get_settings_controller,
    reset_settings_controller
)

# 기존 임포트 패턴 유지
__all__ = [
    'SettingsController',
    'UserSettings', 
    'SettingsChangeEvent',
    'ValidationResult',
    'ToolInfo',
    'get_settings_controller',
    'reset_settings_controller'
]