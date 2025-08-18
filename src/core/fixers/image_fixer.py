# src/core/fixers/image_fixer.py
"""
이미지 자동 수정 모듈

이미지 해상도 최적화와 압축을 수행합니다.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
import subprocess

from .base_fixer import BaseFixer, FixResult, FixContext
from ..models import PDFDocument, QualityIssue
from ...external import get_tool_manager


class ImageFixer(BaseFixer):
    """
    이미지 수정기
    
    이미지 해상도를 최적화하고 압축을 수행합니다.
    """
    
    def __init__(self):
        """이미지 수정기 초기화"""
        super().__init__("ImageFixer")
        self.tool_manager = get_tool_manager()
        
        # 기본 이미지 설정
        self.default_settings = {
            'target_dpi': 300,  # 목표 해상도
            'min_dpi': 200,     # 최소 해상도
            'max_dpi': 600,     # 최대 해상도
            'jpeg_quality': 85,  # JPEG 품질 (1-100)
            'compress': True    # 압축 여부
        }
    
    def can_fix(self, document: PDFDocument, issues: List[QualityIssue]) -> bool:
        """
        이미지 수정 가능 여부 확인
        
        이미지 해상도 문제가 있고 Ghostscript가 사용 가능하면 수정 가능
        """
        # Ghostscript 사용 가능 확인
        if not self.tool_manager.is_available('ghostscript'):
            return False
        
        # 이미지 관련 문제 확인
        has_image_issues = any(
            issue.category == 'image' and 
            ('해상도' in issue.message or 'resolution' in issue.message.lower() or
             '압축' in issue.message or 'compression' in issue.message.lower())
            for issue in issues
        )
        
        return has_image_issues
    
    def fix(self, context: FixContext) -> FixResult:
        """
        이미지 최적화 실행
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            FixResult: 수정 결과
        """
        if context.dry_run:
            return FixResult(
                success=True,
                message="[시뮬레이션] 이미지 최적화 가능",
                fixes_applied=["Image optimization"]
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
            # 설정 병합
            settings = {**self.default_settings, **context.options}
            
            # Ghostscript 명령 구성
            cmd = self._build_optimization_command(
                gs_path,
                context.input_path,
                context.output_path,
                settings
            )
            
            # 명령 실행
            self.logger.info(f"이미지 최적화 시작: {context.input_path}")
            self.logger.info(f"목표 해상도: {settings['target_dpi']} DPI")
            
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
                    # 파일 크기 비교
                    original_size = context.input_path.stat().st_size
                    optimized_size = context.output_path.stat().st_size
                    size_reduction = (1 - optimized_size / original_size) * 100
                    
                    return FixResult(
                        success=True,
                        message=f"이미지 최적화 완료 (크기 {size_reduction:.1f}% 감소)",
                        output_path=context.output_path,
                        fixes_applied=[
                            "Image optimization",
                            f"Resolution adjusted to {settings['target_dpi']} DPI",
                            f"File size reduced by {size_reduction:.1f}%"
                        ]
                    )
                else:
                    return FixResult(
                        success=False,
                        message="최적화된 파일이 생성되지 않았습니다",
                        error="Output file not created"
                    )
            else:
                # 오류 메시지 파싱
                error_msg = self._parse_gs_error(result.stderr)
                return FixResult(
                    success=False,
                    message="이미지 최적화 실패",
                    error=error_msg
                )
                
        except subprocess.TimeoutExpired:
            return FixResult(
                success=False,
                message="최적화 시간 초과",
                error="Optimization timeout (5 minutes)"
            )
        except Exception as e:
            self.logger.error(f"이미지 최적화 오류: {e}")
            return FixResult(
                success=False,
                message="이미지 최적화 중 오류 발생",
                error=str(e)
            )
    
    def _build_optimization_command(self,
                                   gs_path: Path,
                                   input_path: Path,
                                   output_path: Path,
                                   settings: Dict[str, Any]) -> List[str]:
        """
        이미지 최적화용 Ghostscript 명령 구성
        
        Args:
            gs_path: Ghostscript 실행 파일 경로
            input_path: 입력 PDF
            output_path: 출력 PDF
            settings: 최적화 설정
            
        Returns:
            List[str]: 명령 인자 리스트
        """
        cmd = [
            str(gs_path),
            '-sDEVICE=pdfwrite',
            '-dNOPAUSE',
            '-dBATCH',
            '-dSAFER',
            '-dCompatibilityLevel=1.4',
            f'-sOutputFile={output_path}'
        ]
        
        # PDF 설정 (품질 수준)
        quality_level = settings.get('quality_level', 'print')
        if quality_level == 'print':
            cmd.append('-dPDFSETTINGS=/prepress')
        elif quality_level == 'ebook':
            cmd.append('-dPDFSETTINGS=/ebook')
        elif quality_level == 'screen':
            cmd.append('-dPDFSETTINGS=/screen')
        else:
            cmd.append('-dPDFSETTINGS=/default')
        
        # 해상도 설정
        target_dpi = settings['target_dpi']
        
        # 컬러 이미지
        cmd.append(f'-dColorImageResolution={target_dpi}')
        if target_dpi > 150:
            cmd.append('-dColorImageDownsampleType=/Bicubic')
        else:
            cmd.append('-dColorImageDownsampleType=/Average')
        
        # 그레이스케일 이미지
        cmd.append(f'-dGrayImageResolution={target_dpi}')
        if target_dpi > 150:
            cmd.append('-dGrayImageDownsampleType=/Bicubic')
        else:
            cmd.append('-dGrayImageDownsampleType=/Average')
        
        # 흑백 이미지
        mono_dpi = min(target_dpi * 4, 1200)  # 흑백은 더 높은 해상도
        cmd.append(f'-dMonoImageResolution={mono_dpi}')
        cmd.append('-dMonoImageDownsampleType=/Bicubic')
        
        # 압축 설정
        if settings['compress']:
            # JPEG 압축
            cmd.append('-dAutoFilterColorImages=false')
            cmd.append('-dColorImageFilter=/DCTEncode')
            cmd.append('-dAutoFilterGrayImages=false')
            cmd.append('-dGrayImageFilter=/DCTEncode')
            
            # JPEG 품질
            jpeg_quality = settings['jpeg_quality']
            if jpeg_quality >= 90:
                cmd.append('-dJPEGQ=0.95')
            elif jpeg_quality >= 75:
                cmd.append('-dJPEGQ=0.85')
            elif jpeg_quality >= 50:
                cmd.append('-dJPEGQ=0.75')
            else:
                cmd.append('-dJPEGQ=0.60')
        else:
            # 무손실 압축
            cmd.append('-dAutoFilterColorImages=false')
            cmd.append('-dColorImageFilter=/FlateEncode')
            cmd.append('-dAutoFilterGrayImages=false')
            cmd.append('-dGrayImageFilter=/FlateEncode')
        
        # 다운샘플링 임계값
        cmd.append('-dColorImageDownsampleThreshold=1.0')
        cmd.append('-dGrayImageDownsampleThreshold=1.0')
        cmd.append('-dMonoImageDownsampleThreshold=1.0')
        
        # 폰트 설정 (보존)
        cmd.append('-dEmbedAllFonts=true')
        cmd.append('-dSubsetFonts=true')
        
        # 색상 설정 (보존)
        if settings.get('preserve_colors', True):
            cmd.append('-dColorConversionStrategy=/LeaveColorUnchanged')
        
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
        return lines[-1].strip() if lines else "최적화 실패"
    
    def upscale_images(self, context: FixContext, target_dpi: int = 300) -> FixResult:
        """
        저해상도 이미지 업스케일링
        
        Args:
            context: 수정 컨텍스트
            target_dpi: 목표 해상도
            
        Returns:
            FixResult: 수정 결과
        """
        context.options['target_dpi'] = target_dpi
        context.options['compress'] = False  # 업스케일링시 무손실
        return self.fix(context)
    
    def compress_images(self, context: FixContext, quality: int = 85) -> FixResult:
        """
        이미지 압축만 수행
        
        Args:
            context: 수정 컨텍스트
            quality: JPEG 품질 (1-100)
            
        Returns:
            FixResult: 수정 결과
        """
        # 현재 해상도 유지하면서 압축만
        context.options['compress'] = True
        context.options['jpeg_quality'] = quality
        context.options['target_dpi'] = 0  # 해상도 변경 안함
        return self.fix(context)