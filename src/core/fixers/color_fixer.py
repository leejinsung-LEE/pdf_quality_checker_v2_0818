# src/core/fixers/color_fixer.py
"""
색상 자동 수정 모듈

RGB를 CMYK로 변환하고 색상 관련 문제를 수정합니다.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
import subprocess
import tempfile

from .base_fixer import BaseFixer, FixResult, FixContext
from ..models import PDFDocument, QualityIssue
from ...external import get_tool_manager


class ColorFixer(BaseFixer):
    """
    색상 수정기
    
    RGB를 CMYK로 변환하고 색상 프로파일을 적용합니다.
    """
    
    def __init__(self):
        """색상 수정기 초기화"""
        super().__init__("ColorFixer")
        self.tool_manager = get_tool_manager()
        
        # 기본 CMYK 프로파일 (Coated FOGRA39)
        self.default_cmyk_profile = "CoatedFOGRA39"
        
        # Ghostscript 색상 변환 설정
        self.gs_color_settings = {
            'ColorConversionStrategy': '/CMYK',
            'ProcessColorModel': '/DeviceCMYK',
            'ColorImageDownsampleType': '/None',
            'GrayImageDownsampleType': '/None',
            'MonoImageDownsampleType': '/None',
            'UCRandBGInfo': '/Preserve',
            'PreserveOverprintSettings': 'true',
            'PreserveHalftoneInfo': 'true'
        }
    
    def can_fix(self, document: PDFDocument, issues: List[QualityIssue]) -> bool:
        """
        색상 수정 가능 여부 확인
        
        RGB 색상 문제가 있고 Ghostscript가 사용 가능하면 수정 가능
        """
        # Ghostscript 사용 가능 확인
        if not self.tool_manager.is_available('ghostscript'):
            return False
        
        # RGB 색상 문제 확인
        has_rgb_issues = any(
            issue.category == 'color' and 'RGB' in issue.message
            for issue in issues
        )
        
        return has_rgb_issues
    
    def fix(self, context: FixContext) -> FixResult:
        """
        RGB를 CMYK로 변환
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            FixResult: 수정 결과
        """
        if context.dry_run:
            return FixResult(
                success=True,
                message="[시뮬레이션] RGB→CMYK 변환 가능",
                fixes_applied=["RGB to CMYK conversion"]
            )
        
        # Ghostscript 경로
        gs_path = self.tool_manager.get_tool_path('ghostscript')
        if not gs_path:
            return FixResult(
                success=False,
                message="Ghostscript를 찾을 수 없습니다",
                error="Ghostscript not found"
            )
        
        try:
            # Ghostscript 명령 구성
            cmd = self._build_gs_command(
                gs_path,
                context.input_path,
                context.output_path,
                context.options
            )
            
            # 명령 실행
            self.logger.info(f"RGB→CMYK 변환 시작: {context.input_path}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            
            # 결과 확인
            if result.returncode == 0:
                # 출력 파일 확인
                if context.output_path.exists():
                    return FixResult(
                        success=True,
                        message="RGB→CMYK 변환 완료",
                        output_path=context.output_path,
                        fixes_applied=["RGB to CMYK conversion"]
                    )
                else:
                    return FixResult(
                        success=False,
                        message="변환된 파일이 생성되지 않았습니다",
                        error="Output file not created"
                    )
            else:
                # 오류 메시지 파싱
                error_msg = self._parse_gs_error(result.stderr)
                return FixResult(
                    success=False,
                    message="RGB→CMYK 변환 실패",
                    error=error_msg
                )
                
        except subprocess.TimeoutExpired:
            return FixResult(
                success=False,
                message="변환 시간 초과",
                error="Conversion timeout (5 minutes)"
            )
        except Exception as e:
            self.logger.error(f"색상 변환 오류: {e}")
            return FixResult(
                success=False,
                message="색상 변환 중 오류 발생",
                error=str(e)
            )
    
    def _build_gs_command(self, 
                         gs_path: Path,
                         input_path: Path,
                         output_path: Path,
                         options: Dict[str, Any]) -> List[str]:
        """
        Ghostscript 명령 구성
        
        Args:
            gs_path: Ghostscript 실행 파일 경로
            input_path: 입력 PDF
            output_path: 출력 PDF
            options: 추가 옵션
            
        Returns:
            List[str]: 명령 인자 리스트
        """
        cmd = [
            str(gs_path),
            '-sDEVICE=pdfwrite',
            '-dNOPAUSE',
            '-dBATCH',
            '-dSAFER',
            '-dPDFSETTINGS=/prepress',  # 인쇄용 설정
            '-dCompatibilityLevel=1.4',
            f'-sOutputFile={output_path}'
        ]
        
        # 색상 변환 설정 추가
        for key, value in self.gs_color_settings.items():
            if value.startswith('/'):
                cmd.append(f'-s{key}={value}')
            else:
                cmd.append(f'-d{key}={value}')
        
        # 사용자 옵션 추가
        if options.get('compress', True):
            cmd.append('-dCompressFonts=true')
            cmd.append('-dCompressPages=true')
        
        if options.get('embed_fonts', True):
            cmd.append('-dEmbedAllFonts=true')
            cmd.append('-dSubsetFonts=true')
        
        # 품질 설정
        quality = options.get('quality', 'high')
        if quality == 'high':
            cmd.append('-dColorImageResolution=300')
            cmd.append('-dGrayImageResolution=300')
            cmd.append('-dMonoImageResolution=1200')
        elif quality == 'medium':
            cmd.append('-dColorImageResolution=200')
            cmd.append('-dGrayImageResolution=200')
            cmd.append('-dMonoImageResolution=600')
        else:  # low
            cmd.append('-dColorImageResolution=150')
            cmd.append('-dGrayImageResolution=150')
            cmd.append('-dMonoImageResolution=300')
        
        # CMYK 프로파일 (옵션)
        cmyk_profile = options.get('cmyk_profile', self.default_cmyk_profile)
        if cmyk_profile:
            # 프로파일 파일이 있는 경우 사용
            profile_path = Path(__file__).parent / 'profiles' / f'{cmyk_profile}.icc'
            if profile_path.exists():
                cmd.append(f'-sOutputICCProfile={profile_path}')
        
        # 입력 파일
        cmd.append(str(input_path))
        
        return cmd
    
    def _parse_gs_error(self, stderr: str) -> str:
        """
        Ghostscript 오류 메시지 파싱
        
        Args:
            stderr: 표준 오류 출력
            
        Returns:
            str: 파싱된 오류 메시지
        """
        if not stderr:
            return "알 수 없는 오류"
        
        # 주요 오류 패턴 확인
        error_patterns = {
            'Error: /undefined': '정의되지 않은 명령',
            'Error: /syntaxerror': '문법 오류',
            'Error: /rangecheck': '범위 초과',
            'Error: /typecheck': '타입 오류',
            'Error: /VMerror': '메모리 부족',
            'Error: /invalidfileaccess': '파일 접근 오류',
            'Error: /ioerror': '입출력 오류'
        }
        
        for pattern, message in error_patterns.items():
            if pattern in stderr:
                return f"Ghostscript {message}"
        
        # 첫 번째 오류 라인 반환
        lines = stderr.strip().split('\n')
        for line in lines:
            if 'Error:' in line or 'ERROR:' in line:
                return line.strip()
        
        # 마지막 라인 반환
        return lines[-1].strip() if lines else "변환 실패"
    
    def convert_spot_colors(self, context: FixContext) -> FixResult:
        """
        별색을 CMYK로 변환
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            FixResult: 수정 결과
        """
        # Ghostscript로 별색 변환
        context.options['convert_spot_colors'] = True
        return self.fix(context)
    
    def apply_color_profile(self, 
                           context: FixContext,
                           profile_name: str) -> FixResult:
        """
        색상 프로파일 적용
        
        Args:
            context: 수정 컨텍스트
            profile_name: 프로파일 이름 (예: 'CoatedFOGRA39')
            
        Returns:
            FixResult: 수정 결과
        """
        context.options['cmyk_profile'] = profile_name
        return self.fix(context)