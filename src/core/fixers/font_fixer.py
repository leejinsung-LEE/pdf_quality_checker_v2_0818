# src/core/fixers/font_fixer.py
"""
폰트 자동 수정 모듈

임베딩되지 않은 폰트를 아웃라인(경로)으로 변환합니다.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
import subprocess
import tempfile

from .base_fixer import BaseFixer, FixResult, FixContext
from ..models import PDFDocument, QualityIssue
from ...external import get_tool_manager


class FontFixer(BaseFixer):
    """
    폰트 수정기
    
    임베딩되지 않은 폰트가 있을 경우 모든 텍스트를 아웃라인으로 변환합니다.
    """
    
    def __init__(self):
        """폰트 수정기 초기화"""
        super().__init__("FontFixer")
        self.tool_manager = get_tool_manager()
        
        # Ghostscript 폰트 아웃라인 설정
        self.gs_outline_settings = {
            'NoOutputFonts': 'true',  # 폰트 출력 안함 (아웃라인으로 변환)
            'PreserveOverprintSettings': 'true',
            'PreserveHalftoneInfo': 'true',
            'TransferFunctionInfo': '/Preserve',
            'UCRandBGInfo': '/Preserve'
        }
    
    def can_fix(self, document: PDFDocument, issues: List[QualityIssue]) -> bool:
        """
        폰트 수정 가능 여부 확인
        
        임베딩되지 않은 폰트 문제가 있고 Ghostscript가 사용 가능하면 수정 가능
        """
        # Ghostscript 사용 가능 확인
        if not self.tool_manager.is_available('ghostscript'):
            return False
        
        # 폰트 임베딩 문제 확인
        has_font_issues = any(
            issue.category == 'font' and 
            ('임베딩' in issue.message or 'embedded' in issue.message.lower())
            for issue in issues
        )
        
        return has_font_issues
    
    def fix(self, context: FixContext) -> FixResult:
        """
        모든 텍스트를 아웃라인으로 변환
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            FixResult: 수정 결과
        """
        if context.dry_run:
            return FixResult(
                success=True,
                message="[시뮬레이션] 폰트 아웃라인 변환 가능",
                fixes_applied=["Font outline conversion"]
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
            # 폰트 임베딩 상태 확인
            font_status = self._check_font_embedding(context.input_path)
            
            if font_status['all_embedded'] and not context.options.get('force_outline', False):
                # 모든 폰트가 이미 임베딩되어 있음
                return FixResult(
                    success=True,
                    message="모든 폰트가 이미 임베딩되어 있습니다",
                    output_path=context.input_path
                )
            
            # 아웃라인 변환 실행
            self.logger.info(f"폰트 아웃라인 변환 시작: {context.input_path}")
            self.logger.info(f"임베딩되지 않은 폰트: {font_status['non_embedded_fonts']}")
            
            # Ghostscript 명령 구성
            cmd = self._build_outline_command(
                gs_path,
                context.input_path,
                context.output_path,
                context.options
            )
            
            # 명령 실행
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
                    # 변환 후 폰트 상태 확인
                    new_font_status = self._check_font_embedding(context.output_path)
                    
                    return FixResult(
                        success=True,
                        message=f"폰트 아웃라인 변환 완료 (변환된 폰트: {len(font_status['non_embedded_fonts'])}개)",
                        output_path=context.output_path,
                        fixes_applied=[
                            "Font outline conversion",
                            f"Converted {len(font_status['non_embedded_fonts'])} fonts to outlines"
                        ]
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
                    message="폰트 아웃라인 변환 실패",
                    error=error_msg
                )
                
        except subprocess.TimeoutExpired:
            return FixResult(
                success=False,
                message="변환 시간 초과",
                error="Conversion timeout (5 minutes)"
            )
        except Exception as e:
            self.logger.error(f"폰트 변환 오류: {e}")
            return FixResult(
                success=False,
                message="폰트 변환 중 오류 발생",
                error=str(e)
            )
    
    def _check_font_embedding(self, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF의 폰트 임베딩 상태 확인
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict: 폰트 상태 정보
        """
        font_status = {
            'all_embedded': True,
            'non_embedded_fonts': [],
            'embedded_fonts': [],
            'total_fonts': 0
        }
        
        # pdffonts 도구 사용
        pdffonts_path = self.tool_manager.get_tool_path('pdffonts')
        if not pdffonts_path:
            # pdffonts가 없으면 기본값 반환
            return font_status
        
        try:
            cmd = [str(pdffonts_path), str(pdf_path)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                # 헤더 건너뛰기
                for line in lines[2:]:  # 첫 2줄은 헤더
                    if not line.strip():
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 5:
                        font_name = parts[0]
                        embedded = parts[4].lower()
                        
                        font_status['total_fonts'] += 1
                        
                        if embedded in ['yes', 'subset']:
                            font_status['embedded_fonts'].append(font_name)
                        else:
                            font_status['non_embedded_fonts'].append(font_name)
                            font_status['all_embedded'] = False
                            
        except Exception as e:
            self.logger.warning(f"폰트 상태 확인 실패: {e}")
        
        return font_status
    
    def _build_outline_command(self,
                              gs_path: Path,
                              input_path: Path,
                              output_path: Path,
                              options: Dict[str, Any]) -> List[str]:
        """
        폰트 아웃라인 변환용 Ghostscript 명령 구성
        
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
            '-dPDFSETTINGS=/prepress',
            '-dCompatibilityLevel=1.4',
            f'-sOutputFile={output_path}'
        ]
        
        # 폰트 아웃라인 설정
        for key, value in self.gs_outline_settings.items():
            if value == 'true' or value == 'false':
                cmd.append(f'-d{key}={value}')
            else:
                cmd.append(f'-s{key}={value}')
        
        # 품질 설정 (아웃라인은 해상도가 중요)
        resolution = options.get('resolution', 300)
        cmd.append(f'-r{resolution}')
        
        # 이미지 압축 설정
        if not options.get('compress_images', True):
            cmd.append('-dAutoFilterColorImages=false')
            cmd.append('-dAutoFilterGrayImages=false')
            cmd.append('-dColorImageFilter=/FlateEncode')
            cmd.append('-dGrayImageFilter=/FlateEncode')
        
        # 색상 보존
        if options.get('preserve_colors', True):
            cmd.append('-dColorConversionStrategy=/LeaveColorUnchanged')
            cmd.append('-dConvertCMYKImagesToRGB=false')
            cmd.append('-dConvertRGBImagesToCMYK=false')
        
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
        
        # 오류 패턴 확인
        if 'Error:' in stderr:
            lines = stderr.strip().split('\n')
            for line in lines:
                if 'Error:' in line:
                    return line.strip()
        
        # 마지막 라인 반환
        lines = stderr.strip().split('\n')
        return lines[-1].strip() if lines else "변환 실패"
    
    def embed_fonts(self, context: FixContext) -> FixResult:
        """
        폰트 임베딩 시도 (가능한 경우)
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            FixResult: 수정 결과
        """
        # 폰트 임베딩 시도
        gs_path = self.tool_manager.get_tool_path('ghostscript')
        if not gs_path:
            return FixResult(
                success=False,
                message="Ghostscript를 찾을 수 없습니다",
                error="Ghostscript not found"
            )
        
        cmd = [
            str(gs_path),
            '-sDEVICE=pdfwrite',
            '-dNOPAUSE',
            '-dBATCH',
            '-dSAFER',
            '-dEmbedAllFonts=true',
            '-dSubsetFonts=true',
            '-dCompressFonts=true',
            f'-sOutputFile={context.output_path}',
            str(context.input_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0 and context.output_path.exists():
                return FixResult(
                    success=True,
                    message="폰트 임베딩 완료",
                    output_path=context.output_path,
                    fixes_applied=["Font embedding"]
                )
            else:
                # 임베딩 실패시 아웃라인으로 대체
                self.logger.warning("폰트 임베딩 실패, 아웃라인 변환으로 대체")
                return self.fix(context)
                
        except Exception as e:
            # 오류 발생시 아웃라인으로 대체
            self.logger.warning(f"폰트 임베딩 오류: {e}, 아웃라인 변환으로 대체")
            return self.fix(context)