# src/external/tool_manager.py
"""
외부 도구 관리자

PDF 분석에 필요한 외부 도구들을 관리합니다.
실행 폴더의 gs와 poppler 폴더에서 도구를 찾습니다.
"""

import subprocess
import platform
import shutil
from typing import Dict, Optional, List
from pathlib import Path
import sys
import os


class ToolManager:
    """
    외부 도구 통합 관리자
    
    Ghostscript, Poppler 도구들(pdffonts, pdfinfo 등)의
    설치 상태를 확인하고 실행을 관리합니다.
    """
    
    def __init__(self):
        """도구 관리자 초기화"""
        self.tools = {
            'ghostscript': None,
            'pdffonts': None,
            'pdfinfo': None,
            'pdftoppm': None,
            'pdfimages': None
        }
        
        self.tool_executables = {
            'ghostscript': ['gs', 'gswin64c.exe', 'gswin32c.exe'],
            'pdffonts': ['pdffonts', 'pdffonts.exe'],
            'pdfinfo': ['pdfinfo', 'pdfinfo.exe'],
            'pdftoppm': ['pdftoppm', 'pdftoppm.exe'],
            'pdfimages': ['pdfimages', 'pdfimages.exe']
        }
        
        self._discover_tools()
    
    def _discover_tools(self):
        """시스템에서 사용 가능한 도구 자동 발견"""
        # Searching for external tools...
        
        # 실행 파일이 있는 디렉토리 찾기
        if getattr(sys, 'frozen', False):
            # 실행 파일로 패키징된 경우
            base_dir = Path(sys.executable).parent
        else:
            # 스크립트로 실행하는 경우
            base_dir = Path.cwd()
        
        # Base directory: {base_dir}
        
        # 상대경로에서 도구 찾기
        for tool_name, executables in self.tool_executables.items():
            found = False
            
            # 1. 먼저 실행 폴더의 gs/poppler 폴더에서 찾기
            if tool_name == 'ghostscript':
                gs_paths = [
                    base_dir / 'gs' / 'bin' / 'gswin64c.exe',
                    base_dir / 'gs' / 'bin' / 'gswin32c.exe',
                    base_dir / 'gs' / 'bin' / 'gs.exe',
                    base_dir / 'gs' / 'gs.exe',
                    base_dir / 'gs' / 'gswin64c.exe',
                    base_dir / 'gs' / 'gswin32c.exe',
                ]
                for gs_path in gs_paths:
                    if gs_path.exists() and gs_path.is_file():
                        self.tools[tool_name] = str(gs_path)
                        # [OK] {tool_name}: {gs_path} (relative path)
                        found = True
                        break
            
            elif tool_name in ['pdffonts', 'pdfinfo', 'pdftoppm', 'pdfimages']:
                poppler_paths = [
                    base_dir / 'poppler' / 'bin' / f'{tool_name}.exe',
                    base_dir / 'poppler' / f'{tool_name}.exe',
                    base_dir / 'poppler' / 'Library' / 'bin' / f'{tool_name}.exe',
                ]
                for poppler_path in poppler_paths:
                    if poppler_path.exists() and poppler_path.is_file():
                        self.tools[tool_name] = str(poppler_path)
                        # [OK] {tool_name}: {poppler_path} (relative path)
                        found = True
                        break
            
            # 2. 상대경로에서 못 찾으면 시스템 PATH에서 찾기
            if not found:
                for exe in executables:
                    path = self._find_executable(exe)
                    if path:
                        self.tools[tool_name] = path
                        # [OK] {tool_name}: {path} (system)
                        found = True
                        break
            
            if not found:
                # [NOT FOUND] {tool_name}: not found
                pass
    
    def _find_executable(self, name: str) -> Optional[str]:
        """
        실행 파일 찾기
        
        Args:
            name: 실행 파일 이름
            
        Returns:
            Optional[str]: 실행 파일 경로 또는 None
        """
        # PATH에서 찾기
        path = shutil.which(name)
        if path:
            return path
        
        # Windows의 일반적인 설치 경로 확인 (낮은 우선순위)
        if platform.system() == 'Windows':
            common_paths = [
                Path(r'C:\Program Files\gs'),
                Path(r'C:\Program Files (x86)\gs'),
                Path(r'C:\Program Files\Poppler'),
                Path(r'C:\Program Files (x86)\Poppler'),
            ]
            
            for base_path in common_paths:
                if not base_path.exists():
                    continue
                
                # 하위 디렉토리 검색
                for item in base_path.rglob(name):
                    if item.is_file():
                        return str(item)
        
        return None
    
    def has_tool(self, tool_name: str) -> bool:
        """
        특정 도구 사용 가능 여부 확인
        
        Args:
            tool_name: 도구 이름
            
        Returns:
            bool: 사용 가능 여부
        """
        return self.tools.get(tool_name) is not None
    
    def is_tool_available(self, tool_name: str) -> bool:
        """
        도구 사용 가능 여부 확인 (has_tool의 별칭)
        
        Args:
            tool_name: 도구 이름
            
        Returns:
            bool: 사용 가능 여부
        """
        return self.has_tool(tool_name)
    
    def get_tool_path(self, tool_name: str) -> Optional[str]:
        """
        도구 실행 파일 경로 가져오기
        
        Args:
            tool_name: 도구 이름
            
        Returns:
            Optional[str]: 실행 파일 경로
        """
        return self.tools.get(tool_name)
    
    def set_tool_path(self, tool_name: str, tool_path: Path) -> bool:
        """
        도구 실행 파일 경로 설정
        
        Args:
            tool_name: 도구 이름
            tool_path: 도구 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 경로가 존재하고 실행 가능한지 확인
            if tool_path.exists() and tool_path.is_file():
                self.tools[tool_name] = str(tool_path)
                return True
            return False
        except Exception:
            return False
    
    def run_tool(self, tool_name: str, args: List[str], 
                 timeout: int = 30) -> subprocess.CompletedProcess:
        """
        외부 도구 실행
        
        Args:
            tool_name: 도구 이름
            args: 명령줄 인자
            timeout: 제한 시간 (초)
            
        Returns:
            subprocess.CompletedProcess: 실행 결과
            
        Raises:
            ToolNotFoundError: 도구를 찾을 수 없음
            subprocess.TimeoutExpired: 시간 초과
        """
        tool_path = self.get_tool_path(tool_name)
        if not tool_path:
            raise ToolNotFoundError(f"{tool_name}을(를) 찾을 수 없습니다")
        
        cmd = [tool_path] + args
        
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    
    def get_tool_version(self, tool_name: str) -> Optional[str]:
        """
        특정 도구의 버전 정보 가져오기
        
        Args:
            tool_name: 도구 이름
            
        Returns:
            Optional[str]: 버전 정보 또는 None
        """
        tool_path = self.get_tool_path(tool_name)
        if not tool_path:
            return None
        
        try:
            if tool_name == 'ghostscript':
                result = self.run_tool(tool_name, ['--version'], timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip()
            elif tool_name in ['pdffonts', 'pdfinfo', 'pdftoppm', 'pdfimages']:
                result = self.run_tool(tool_name, ['-v'], timeout=5)
                if result.returncode == 0:
                    # stderr에 버전 정보가 출력됨
                    return result.stderr.strip()
        except Exception:
            # 버전 확인 실패는 무시
            pass
        
        return None
    
    def get_status_report(self) -> Dict[str, Dict[str, any]]:
        """
        모든 도구의 상태 보고서 생성
        
        Returns:
            Dict[str, Dict[str, any]]: 도구별 상태 정보
        """
        report = {}
        
        for tool_name, tool_path in self.tools.items():
            status = {
                'available': tool_path is not None,
                'path': tool_path,
                'version': None
            }
            
            # 버전 정보 가져오기 시도
            if tool_path:
                status['version'] = self.get_tool_version(tool_name)
            
            report[tool_name] = status
        
        return report
    
    def check_requirements(self, required_tools: List[str]) -> Dict[str, bool]:
        """
        필요한 도구들의 사용 가능 여부 확인
        
        Args:
            required_tools: 필요한 도구 이름 목록
            
        Returns:
            Dict[str, bool]: 도구별 사용 가능 여부
        """
        return {
            tool: self.has_tool(tool)
            for tool in required_tools
        }
    
    def get_missing_tools(self, required_tools: List[str]) -> List[str]:
        """
        누락된 도구 목록 가져오기
        
        Args:
            required_tools: 필요한 도구 이름 목록
            
        Returns:
            List[str]: 누락된 도구 이름 목록
        """
        return [
            tool for tool in required_tools
            if not self.has_tool(tool)
        ]


class ToolNotFoundError(Exception):
    """도구를 찾을 수 없을 때 발생하는 예외"""
    pass


# 전역 인스턴스
from functools import lru_cache


@lru_cache(maxsize=1)
def get_tool_manager() -> ToolManager:
    """
    도구 관리자 싱글톤 인스턴스 가져오기 (스레드 안전)
    
    LRU 캐시를 사용하여 싱글톤 패턴을 구현합니다.
    Python 내장 기능으로 스레드 안전성이 보장됩니다.
    
    Returns:
        ToolManager: 도구 관리자 인스턴스
    """
    return ToolManager()