# src/reporting/report_generator/generator.py
"""
메인 보고서 생성기
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import logging

from .base import ReportOptions
from .data_processor import DataProcessor
from .format_handlers import FormatHandlerManager
from .utils import ReportUtils

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.quality_checker import QualityCheckResult
    from ...config import Config


class ReportGenerator:
    """
    보고서 생성기
    
    다양한 형식의 보고서를 생성하고 저장합니다.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        보고서 생성기 초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 구성요소 초기화
        self.format_manager = FormatHandlerManager(self.logger)
        self.data_processor = DataProcessor(self.logger)
        self.utils = ReportUtils()
    
    def generate(self,
                quality_result: 'QualityCheckResult',
                format_type: str = 'html',
                output_folder: Optional[Path] = None,
                options: Optional[ReportOptions] = None) -> Optional[Path]:
        """
        보고서 생성
        
        Args:
            quality_result: 품질 검사 결과
            format_type: 보고서 형식
            output_folder: 출력 폴더
            options: 보고서 옵션
            
        Returns:
            Path: 생성된 보고서 경로
        """
        # 형식 지원 확인
        if not self.format_manager.is_format_supported(format_type):
            self.logger.error(f"지원하지 않는 보고서 형식: {format_type}")
            self.logger.info(f"지원 형식: {', '.join(self.format_manager.get_supported_formats())}")
            return None
        
        # 옵션 설정
        if options is None:
            options = ReportOptions()
        
        try:
            # 빌더 클래스 가져오기
            builder_class = self.format_manager.get_builder_class(format_type)
            if not builder_class:
                self.logger.error(f"빌더를 찾을 수 없습니다: {format_type}")
                return None
            
            # 빌더 인스턴스 생성
            builder = builder_class(options)
            
            # 추가 데이터 준비
            additional_data = self.data_processor.prepare_additional_data(quality_result, options)
            
            # 보고서 생성
            self.logger.info(f"{format_type.upper()} 보고서 생성 중...")
            content = builder.build(quality_result, additional_data)
            
            # 파일 저장
            report_path = self._save_report(
                content,
                quality_result.analysis_result.document.filename,
                format_type,
                builder.get_file_extension(),
                output_folder
            )
            
            if report_path:
                self.logger.info(f"보고서 생성 완료: {report_path.name}")
            
            return report_path
            
        except Exception as e:
            self.logger.error(f"보고서 생성 실패: {e}", exc_info=True)
            return None
    
    def generate_multiple(self,
                         quality_result: 'QualityCheckResult',
                         formats: List[str],
                         output_folder: Optional[Path] = None,
                         options: Optional[ReportOptions] = None) -> Dict[str, Path]:
        """
        여러 형식의 보고서 생성
        
        Args:
            quality_result: 품질 검사 결과
            formats: 보고서 형식 목록
            output_folder: 출력 폴더
            options: 보고서 옵션
            
        Returns:
            Dict[str, Path]: 형식별 보고서 경로
        """
        results = {}
        
        self.logger.info(f"{len(formats)}개 형식으로 보고서 생성 시작")
        
        for format_type in formats:
            path = self.generate(quality_result, format_type, output_folder, options)
            if path:
                results[format_type] = path
            else:
                self.logger.warning(f"{format_type} 보고서 생성 실패")
        
        self.logger.info(f"보고서 생성 완료: {len(results)}/{len(formats)} 성공")
        
        return results
    
    def _save_report(self,
                    content: str,
                    filename: str,
                    format_type: str,
                    extension: str,
                    output_folder: Optional[Path] = None) -> Path:
        """
        보고서 파일 저장
        
        Args:
            content: 보고서 내용
            filename: 원본 파일명
            format_type: 보고서 형식
            extension: 파일 확장자
            output_folder: 출력 폴더
            
        Returns:
            저장된 파일 경로
        """
        # 출력 폴더 결정
        if output_folder is None:
            # Config에서 기본 폴더 가져오기
            try:
                from ...config import Config
                output_folder = Path(Config.REPORTS_FOLDER)
            except:
                output_folder = Path("reports")
        
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # 파일명 생성
        report_filename = self.utils.generate_report_filename(
            filename, format_type, extension
        )
        
        # 파일 저장
        report_path = output_folder / report_filename
        
        # 이진 형식 처리 (PDF, Excel 등)
        if format_type in ['pdf', 'excel', 'xlsx']:
            if isinstance(content, bytes):
                report_path.write_bytes(content)
            else:
                report_path.write_text(content, encoding='utf-8')
        else:
            report_path.write_text(content, encoding='utf-8')
        
        self.logger.debug(f"보고서 저장: {report_path}")
        
        return report_path
    
    def register_custom_builder(self, format_type: str, builder_class: type):
        """
        사용자 정의 빌더 등록
        
        Args:
            format_type: 형식 이름
            builder_class: 빌더 클래스
        """
        self.format_manager.register_builder(format_type, builder_class)
    
    def get_supported_formats(self) -> List[str]:
        """
        지원되는 형식 목록 반환
        
        Returns:
            형식 목록
        """
        return self.format_manager.get_supported_formats()
    
    def get_format_info(self, format_type: str) -> Dict[str, str]:
        """
        형식 정보 반환
        
        Args:
            format_type: 형식 이름
            
        Returns:
            형식 정보
        """
        return self.format_manager.get_format_info(format_type)