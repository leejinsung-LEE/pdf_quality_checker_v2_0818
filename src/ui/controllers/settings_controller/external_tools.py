# src/ui/controllers/settings_controller/external_tools.py
"""
외부 도구 관리 모듈

외부 도구의 상태 조회, 경로 설정, 버전 관리 등을 담당합니다.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from .base import SettingsControllerBase


@dataclass
class ToolInfo:
    """외부 도구 정보"""
    name: str
    available: bool = False
    path: Optional[str] = None
    version: Optional[str] = None
    description: str = ""
    required: bool = False
    status_message: str = ""


class ExternalToolsManager(SettingsControllerBase):
    """외부 도구 관리자
    
    Ghostscript, pdffonts 등 외부 도구의 상태를 관리합니다.
    """
    
    def __init__(self, settings_file: Optional[Path] = None, 
                 logger: Optional[logging.Logger] = None):
        """외부 도구 관리자 초기화
        
        Args:
            settings_file: 설정 파일 경로
            logger: 로거 인스턴스
        """
        super().__init__(settings_file, logger)
        
        # 외부 도구 관리자 인스턴스
        self._tool_manager = None
        self._initialize_tool_manager()
        
        # 지원하는 도구 목록
        self._supported_tools = {
            'ghostscript': ToolInfo(
                name='ghostscript',
                description='PDF 최적화 및 변환을 위한 도구',
                required=False
            ),
            'pdffonts': ToolInfo(
                name='pdffonts',
                description='PDF 폰트 정보 분석을 위한 도구 (poppler 패키지)',
                required=False
            )
        }
    
    def _initialize_tool_manager(self) -> None:
        """도구 관리자 초기화"""
        try:
            from ....external import get_tool_manager
            self._tool_manager = get_tool_manager()
        except Exception as e:
            self.logger.error(f"외부 도구 관리자 초기화 실패: {e}")
            self._tool_manager = None
    
    def get_external_tools_status(self) -> Dict[str, ToolInfo]:
        """외부 도구 상태 조회
        
        Returns:
            Dict[str, ToolInfo]: 도구별 상태 정보
        """
        status = {}
        
        # tool_manager 가져오기
        tool_manager = None
        if hasattr(self, '_tool_manager'):
            tool_manager = self._tool_manager
        elif hasattr(self, 'tool_manager'):
            tool_manager = self.tool_manager
        else:
            try:
                from ....external import get_tool_manager
                tool_manager = get_tool_manager()
            except:
                pass
        
        if tool_manager is None:
            # 도구 관리자가 없는 경우 기본 상태 반환
            supported_tools = getattr(self, '_supported_tools', {
                'ghostscript': ToolInfo(
                    name='ghostscript',
                    description='PDF 최적화 및 변환을 위한 도구',
                    required=False
                ),
                'pdffonts': ToolInfo(
                    name='pdffonts',
                    description='PDF 폰트 정보 분석을 위한 도구 (poppler 패키지)',
                    required=False
                )
            })
            for tool_name, tool_info in supported_tools.items():
                tool_info = ToolInfo(
                    name=tool_name,
                    available=False,
                    description=tool_info.description,
                    status_message="도구 관리자를 사용할 수 없습니다"
                )
                status[tool_name] = tool_info
            return status
        
        # 각 도구의 상태 확인
        supported_tools = getattr(self, '_supported_tools', {
            'ghostscript': ToolInfo(
                name='ghostscript',
                description='PDF 최적화 및 변환을 위한 도구',
                required=False
            ),
            'pdffonts': ToolInfo(
                name='pdffonts',
                description='PDF 폰트 정보 분석을 위한 도구 (poppler 패키지)',
                required=False
            )
        })
        for tool_name, base_info in supported_tools.items():
            tool_info = ToolInfo(
                name=tool_name,
                description=base_info.description,
                required=base_info.required
            )
            
            try:
                # 도구 가용성 확인
                tool_info.available = tool_manager.is_tool_available(tool_name)
                
                if tool_info.available:
                    # 경로 조회
                    tool_path = tool_manager.get_tool_path(tool_name)
                    if tool_path:
                        tool_info.path = str(tool_path)
                        
                        # 경로 유효성 확인
                        if not Path(tool_path).exists():
                            tool_info.available = False
                            tool_info.status_message = f"경로가 유효하지 않음: {tool_path}"
                        else:
                            # 버전 정보 조회
                            version = tool_manager.get_tool_version(tool_name)
                            if version:
                                tool_info.version = version
                                tool_info.status_message = f"사용 가능 (버전: {version})"
                            else:
                                tool_info.status_message = "사용 가능 (버전 정보 없음)"
                    else:
                        tool_info.available = False
                        tool_info.status_message = "경로를 찾을 수 없음"
                else:
                    tool_info.status_message = "사용할 수 없음"
                    
            except Exception as e:
                tool_info.available = False
                tool_info.status_message = f"상태 확인 실패: {e}"
                self.logger.error(f"도구 '{tool_name}' 상태 확인 실패: {e}")
            
            status[tool_name] = tool_info
        
        return status
    
    def get_tool_status(self, tool_name: str) -> Optional[ToolInfo]:
        """특정 도구의 상태 조회
        
        Args:
            tool_name: 도구 이름
            
        Returns:
            Optional[ToolInfo]: 도구 정보
        """
        if tool_name not in self._supported_tools:
            return None
        
        all_status = self.get_external_tools_status()
        return all_status.get(tool_name)
    
    def configure_external_tool(self, tool_name: str, tool_path: Path) -> bool:
        """외부 도구 경로 설정
        
        Args:
            tool_name: 도구 이름
            tool_path: 도구 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            if tool_name not in self._supported_tools:
                self.logger.error(f"지원하지 않는 도구: {tool_name}")
                return False
            
            if self._tool_manager is None:
                self.logger.error("도구 관리자를 사용할 수 없습니다")
                return False
            
            # 경로 유효성 확인
            if not tool_path.exists():
                self.logger.error(f"도구 경로가 존재하지 않음: {tool_path}")
                return False
            
            if not tool_path.is_file():
                self.logger.error(f"도구 경로가 파일이 아님: {tool_path}")
                return False
            
            # 도구 관리자에 경로 설정
            if self._tool_manager.set_tool_path(tool_name, tool_path):
                # Config에도 저장
                try:
                    from ....config import Config
                    Config.EXTERNAL_TOOLS[tool_name] = str(tool_path)
                    Config.save_user_settings()
                    
                    self.logger.info(f"외부 도구 경로 설정 완료: {tool_name} -> {tool_path}")
                    
                    # 설정 변경 알림
                    self._notify_tool_configured(tool_name, str(tool_path))
                    
                    return True
                except Exception as e:
                    self.logger.error(f"Config 저장 실패: {e}")
                    return False
            else:
                self.logger.error(f"도구 관리자에서 경로 설정 실패: {tool_name}")
                return False
            
        except Exception as e:
            self.logger.error(f"외부 도구 설정 실패: {tool_name} - {e}")
            return False
    
    def auto_detect_tools(self) -> Dict[str, bool]:
        """도구 자동 탐지
        
        Returns:
            Dict[str, bool]: 도구별 탐지 성공 여부
        """
        results = {}
        
        if self._tool_manager is None:
            for tool_name in self._supported_tools:
                results[tool_name] = False
            return results
        
        for tool_name in self._supported_tools:
            try:
                # 자동 탐지 시도
                detected = self._tool_manager.auto_detect_tool(tool_name)
                results[tool_name] = detected
                
                if detected:
                    self.logger.info(f"도구 자동 탐지 성공: {tool_name}")
                else:
                    self.logger.debug(f"도구 자동 탐지 실패: {tool_name}")
                    
            except Exception as e:
                self.logger.error(f"도구 자동 탐지 중 오류: {tool_name} - {e}")
                results[tool_name] = False
        
        return results
    
    def validate_tool_installation(self, tool_name: str) -> Tuple[bool, List[str]]:
        """도구 설치 상태 검증
        
        Args:
            tool_name: 도구 이름
            
        Returns:
            Tuple[bool, List[str]]: (유효성, 문제점 목록)
        """
        issues = []
        
        if tool_name not in self._supported_tools:
            issues.append(f"지원하지 않는 도구: {tool_name}")
            return False, issues
        
        if self._tool_manager is None:
            issues.append("도구 관리자를 사용할 수 없습니다")
            return False, issues
        
        try:
            # 기본 가용성 확인
            if not self._tool_manager.is_tool_available(tool_name):
                issues.append(f"{tool_name}를 찾을 수 없습니다")
                return False, issues
            
            # 경로 확인
            tool_path = self._tool_manager.get_tool_path(tool_name)
            if not tool_path:
                issues.append(f"{tool_name}의 경로를 찾을 수 없습니다")
                return False, issues
            
            path_obj = Path(tool_path)
            if not path_obj.exists():
                issues.append(f"{tool_name} 경로가 존재하지 않습니다: {tool_path}")
                return False, issues
            
            if not path_obj.is_file():
                issues.append(f"{tool_name} 경로가 파일이 아닙니다: {tool_path}")
                return False, issues
            
            # 실행 권한 확인 (Unix 계열)
            import os
            if not os.access(path_obj, os.X_OK):
                issues.append(f"{tool_name}에 실행 권한이 없습니다: {tool_path}")
            
            # 버전 확인
            version = self._tool_manager.get_tool_version(tool_name)
            if not version:
                issues.append(f"{tool_name}의 버전 정보를 확인할 수 없습니다")
            
            # 기능 테스트
            if not self._test_tool_functionality(tool_name):
                issues.append(f"{tool_name}의 기능 테스트에 실패했습니다")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"검증 중 오류 발생: {e}")
            return False, issues
    
    def _test_tool_functionality(self, tool_name: str) -> bool:
        """도구 기능 테스트
        
        Args:
            tool_name: 도구 이름
            
        Returns:
            bool: 테스트 성공 여부
        """
        try:
            if self._tool_manager is None:
                return False
            
            # 간단한 도구 실행 테스트
            if tool_name == 'ghostscript':
                # Ghostscript 버전 명령 테스트
                result = self._tool_manager.run_tool(tool_name, ['--version'])
                return result.returncode == 0
            
            elif tool_name == 'pdffonts':
                # pdffonts 도움말 명령 테스트
                result = self._tool_manager.run_tool(tool_name, ['-h'])
                # pdffonts는 도움말 출력 후 non-zero exit code를 반환할 수 있음
                return True  # 실행만 되면 OK
            
            return True
            
        except Exception as e:
            self.logger.debug(f"도구 기능 테스트 실패: {tool_name} - {e}")
            return False
    
    def get_tool_requirements(self) -> Dict[str, Dict[str, Any]]:
        """도구별 요구사항 정보
        
        Returns:
            Dict[str, Dict[str, Any]]: 도구별 요구사항
        """
        return {
            'ghostscript': {
                'description': 'PDF 최적화 및 변환',
                'required': False,
                'features': ['PDF 크기 최적화', 'PDF/A 변환', '이미지 압축'],
                'download_url': 'https://www.ghostscript.com/download/gsdnld.html',
                'installation_notes': [
                    'Windows: 설치 후 PATH에 gswin64c.exe 추가',
                    'macOS: brew install ghostscript',
                    'Linux: apt-get install ghostscript 또는 yum install ghostscript'
                ]
            },
            'pdffonts': {
                'description': 'PDF 폰트 정보 분석',
                'required': False,
                'features': ['폰트 목록 조회', '임베딩 상태 확인', '폰트 타입 분석'],
                'download_url': 'https://poppler.freedesktop.org/',
                'installation_notes': [
                    'Windows: poppler-utils 설치',
                    'macOS: brew install poppler',
                    'Linux: apt-get install poppler-utils 또는 yum install poppler-utils'
                ]
            }
        }
    
    def _notify_tool_configured(self, tool_name: str, tool_path: str) -> None:
        """도구 설정 변경 알림
        
        Args:
            tool_name: 도구 이름
            tool_path: 설정된 경로
        """
        try:
            # 설정 변경 이벤트 발생
            if self.on_settings_changed:
                self.on_settings_changed(f'external_tool_{tool_name}', tool_path)
            
            # 커스텀 이벤트 발생
            for listener in self._change_listeners:
                try:
                    from .base import SettingsChangeEvent
                    event = SettingsChangeEvent(
                        f'external_tool_{tool_name}', 
                        None, 
                        tool_path, 
                        'external_tools'
                    )
                    listener(event)
                except Exception as e:
                    self.logger.error(f"도구 설정 알림 실패: {e}")
                    
        except Exception as e:
            self.logger.error(f"도구 설정 알림 실패: {e}")
    
    # 추상 메서드 임시 구현
    def load_settings(self) -> bool:
        """설정 로드 - 다른 모듈에서 구현"""
        return True
    
    def save_settings(self) -> bool:
        """설정 저장 - 다른 모듈에서 구현"""
        return True
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """설정 조회 - 다른 모듈에서 구현"""
        return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any, save: bool = True) -> bool:
        """설정 변경 - 다른 모듈에서 구현"""
        return True
    
    def reset_settings(self, category: Optional[str] = None) -> bool:
        """설정 초기화 - 다른 모듈에서 구현"""
        return True