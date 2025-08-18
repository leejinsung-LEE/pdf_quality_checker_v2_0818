# -*- coding: utf-8 -*-
"""
외부 도구 연동 모듈

pdffonts 등 외부 PDF 분석 도구와 연동합니다.
"""

import subprocess
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import time

from .models import PDFFontsResult
from ....external.tool_manager import get_tool_manager


class ExternalToolsManager:
    """외부 도구 관리자"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        self._pdffonts_available = None
        self.tool_manager = get_tool_manager()
        
    def check_pdffonts_availability(self) -> bool:
        """
        pdffonts 도구 사용 가능 여부 확인
        
        Returns:
            bool: 사용 가능 여부
        """
        if self._pdffonts_available is not None:
            return self._pdffonts_available
            
        # tool_manager를 통해 확인
        self._pdffonts_available = self.tool_manager.has_tool('pdffonts')
        
        if self._pdffonts_available:
            tool_path = self.tool_manager.get_tool_path('pdffonts')
            self.logger.info(f"pdffonts 도구를 사용할 수 있습니다: {tool_path}")
        else:
            self.logger.warning("pdffonts 도구를 찾을 수 없습니다. poppler 폴더를 확인하세요.")
            
        return self._pdffonts_available
        
    def analyze_with_pdffonts(self, pdf_path: Path, timeout: int = 30) -> PDFFontsResult:
        """
        pdffonts 도구를 사용한 폰트 분석
        
        Args:
            pdf_path: PDF 파일 경로
            timeout: 실행 제한 시간 (초)
            
        Returns:
            PDFFontsResult: 분석 결과
        """
        start_time = time.time()
        
        if not self.check_pdffonts_availability():
            return PDFFontsResult(
                fonts={},
                error_message="pdffonts 도구를 사용할 수 없습니다"
            )
            
        try:
            # tool_manager를 통해 pdffonts 실행
            result = self.tool_manager.run_tool(
                'pdffonts',
                [str(pdf_path)],
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode != 0:
                return PDFFontsResult(
                    fonts={},
                    raw_output=result.stdout,
                    error_message=f"pdffonts 실행 실패 (코드: {result.returncode}): {result.stderr}",
                    execution_time=execution_time
                )
                
            # 출력 파싱
            fonts = self._parse_pdffonts_output(result.stdout)
            
            return PDFFontsResult(
                fonts=fonts,
                raw_output=result.stdout,
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired:
            return PDFFontsResult(
                fonts={},
                error_message=f"pdffonts 실행 시간 초과 ({timeout}초)",
                execution_time=timeout
            )
        except Exception as e:
            return PDFFontsResult(
                fonts={},
                error_message=f"pdffonts 실행 중 오류: {str(e)}",
                execution_time=time.time() - start_time
            )
            
    def _parse_pdffonts_output(self, output: str) -> Dict[str, Dict[str, Any]]:
        """
        pdffonts 출력 파싱
        
        Args:
            output: pdffonts 출력 텍스트
            
        Returns:
            Dict[str, Dict[str, Any]]: 폰트 정보
        """
        fonts = {}
        lines = output.strip().split('\n')
        
        # 헤더 찾기 및 컬럼 위치 파악
        header_line = None
        separator_line = None
        
        for i, line in enumerate(lines):
            if 'name' in line.lower() and 'type' in line.lower():
                header_line = i
                if i + 1 < len(lines) and '---' in lines[i + 1]:
                    separator_line = i + 1
                    break
                    
        if header_line is None or separator_line is None:
            self.logger.warning("pdffonts 출력 헤더를 찾을 수 없습니다")
            return fonts
            
        # 데이터 라인 파싱
        for line in lines[separator_line + 1:]:
            if line.strip():
                font_info = self._parse_pdffonts_line(line)
                if font_info:
                    fonts[font_info['name']] = font_info
                    
        self.logger.debug(f"pdffonts에서 {len(fonts)}개 폰트 발견")
        return fonts
        
    def _parse_pdffonts_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        pdffonts 출력 라인 파싱
        
        pdffonts 출력 형식:
        name                                 type              encoding         emb sub uni object ID
        ------------------------------------ ----------------- ---------------- --- --- --- ---------
        ABCDEE+TimesNewRoman                 TrueType          WinAnsi          yes yes yes      7  0
        
        Args:
            line: pdffonts 출력 라인
            
        Returns:
            Dict[str, Any]: 폰트 정보 또는 None
        """
        if not line.strip() or line.startswith('-'):
            return None
            
        # 고정폭 컬럼 파싱 (하드코딩하지 않고 일반적인 pdffonts 형식 사용)
        # 대부분의 pdffonts 출력은 이 형식을 따름
        try:
            # 최소 길이 확인
            if len(line) < 80:
                # 짧은 라인은 split으로 파싱 시도 (fallback)
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 7:
                    # Type이 공백 포함 여부 확인 (예: "Type 1C")
                    if len(parts) >= 8 and parts[1] == "Type" and parts[2] in ["1", "1C", "3"]:
                        # Type 1, Type 1C, Type 3 처리
                        font_info = {
                            'name': parts[0],
                            'type': f"{parts[1]} {parts[2]}",
                            'encoding': parts[3],
                            'embedded': parts[4].lower() == 'yes',
                            'subset': parts[5].lower() == 'yes',
                            'unicode': parts[6].lower() == 'yes',
                            'object_id': f"{parts[7]} {parts[8]}" if len(parts) > 8 else parts[7]
                        }
                    else:
                        font_info = {
                            'name': parts[0],
                            'type': parts[1],
                            'encoding': parts[2],
                            'embedded': parts[3].lower() == 'yes',
                            'subset': parts[4].lower() == 'yes',
                            'unicode': parts[5].lower() == 'yes',
                            'object_id': f"{parts[6]} {parts[7]}" if len(parts) > 7 else parts[6]
                        }
                    return font_info
                return None
            
            # 일반적인 pdffonts 컬럼 위치로 파싱
            font_name = line[0:36].strip()
            font_type = line[37:54].strip() if len(line) > 37 else ''
            encoding = line[55:71].strip() if len(line) > 55 else ''
            emb_str = line[72:75].strip().lower() if len(line) > 72 else ''
            sub_str = line[76:79].strip().lower() if len(line) > 76 else ''
            uni_str = line[80:83].strip().lower() if len(line) > 80 else ''
            
            # object ID는 나머지 부분
            obj_id = line[84:].strip() if len(line) > 84 else ''
            
            font_info = {
                'name': font_name,
                'type': font_type,
                'encoding': encoding,
                'embedded': emb_str == 'yes',
                'subset': sub_str == 'yes',
                'unicode': uni_str == 'yes',
                'object_id': obj_id
            }
            
            # 유효성 검증
            if font_info['name'] and font_info['type']:
                return font_info
            
            return None
            
        except (IndexError, ValueError) as e:
            self.logger.debug(f"라인 파싱 오류: {line} - {e}")
            return None
            
    def get_font_details_with_mutool(self, pdf_path: Path, font_name: str) -> Optional[Dict[str, Any]]:
        """
        mutool을 사용한 폰트 상세 정보 추출 (선택적)
        
        Args:
            pdf_path: PDF 파일 경로
            font_name: 폰트 이름
            
        Returns:
            Dict[str, Any]: 폰트 상세 정보 또는 None
        """
        try:
            # mutool info 실행
            result = subprocess.run(
                ['mutool', 'info', '-F', str(pdf_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 폰트 정보 파싱
                return self._parse_mutool_font_info(result.stdout, font_name)
                
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
        return None
        
    def _parse_mutool_font_info(self, output: str, font_name: str) -> Optional[Dict[str, Any]]:
        """
        mutool 출력에서 특정 폰트 정보 파싱
        
        Args:
            output: mutool 출력
            font_name: 찾을 폰트 이름
            
        Returns:
            Dict[str, Any]: 폰트 정보 또는 None
        """
        # 간단한 파싱 로직
        info = {}
        in_font_section = False
        
        for line in output.split('\n'):
            if font_name in line:
                in_font_section = True
            elif in_font_section and line.strip() == '':
                break
            elif in_font_section:
                # 키-값 쌍 추출
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip().lower()] = value.strip()
                    
        return info if info else None
        
    def check_available_tools(self) -> Dict[str, bool]:
        """
        사용 가능한 외부 도구 확인
        
        Returns:
            Dict[str, bool]: 도구별 사용 가능 여부
        """
        tools = {
            'pdffonts': False,
            'mutool': False,
            'pdfinfo': False
        }
        
        # pdffonts 확인
        tools['pdffonts'] = self.check_pdffonts_availability()
        
        # mutool 확인
        try:
            result = subprocess.run(
                ['mutool', '-v'],
                capture_output=True,
                timeout=5
            )
            tools['mutool'] = result.returncode == 0
        except:
            pass
            
        # pdfinfo 확인
        try:
            result = subprocess.run(
                ['pdfinfo', '-v'],
                capture_output=True,
                timeout=5
            )
            tools['pdfinfo'] = result.returncode == 0
        except:
            pass
            
        return tools