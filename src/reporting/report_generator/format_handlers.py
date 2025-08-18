# src/reporting/report_generator/format_handlers.py
"""
보고서 형식별 빌더 관리
"""

from typing import Dict, Type, Optional
import logging

from .base import ReportBuilder

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


class FormatHandlerManager:
    """형식별 보고서 빌더 관리자"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 빌더 레지스트리
        self.builders: Dict[str, Type[ReportBuilder]] = {}
        
        # 기본 빌더 등록
        self._register_default_builders()
    
    def _register_default_builders(self):
        """기본 빌더 등록"""
        # HTML 빌더
        try:
            from ..html_builder import HTMLReportBuilder
            self.register_builder('html', HTMLReportBuilder)
            self.logger.debug("HTML 보고서 빌더 등록됨")
        except ImportError:
            self.logger.warning("HTML 보고서 빌더를 찾을 수 없습니다")
        
        # 텍스트 빌더
        try:
            from ..base_builder import TextReportBuilder
            self.register_builder('text', TextReportBuilder)
            self.logger.debug("텍스트 보고서 빌더 등록됨")
        except ImportError:
            self.logger.warning("텍스트 보고서 빌더를 찾을 수 없습니다")
        
        # JSON 빌더
        try:
            from ..json_builder import JSONReportBuilder
            self.register_builder('json', JSONReportBuilder)
            self.logger.debug("JSON 보고서 빌더 등록됨")
        except ImportError:
            self.logger.warning("JSON 보고서 빌더를 찾을 수 없습니다")
        
        # PDF 빌더 (선택적)
        try:
            from ..pdf_builder import PDFReportBuilder
            self.register_builder('pdf', PDFReportBuilder)
            self.logger.debug("PDF 보고서 빌더 등록됨")
        except ImportError:
            self.logger.debug("PDF 보고서 빌더는 사용할 수 없습니다")
        
        # Excel 빌더 (선택적)
        try:
            from ..excel_builder import ExcelReportBuilder
            self.register_builder('excel', ExcelReportBuilder)
            self.logger.debug("Excel 보고서 빌더 등록됨")
        except ImportError:
            self.logger.debug("Excel 보고서 빌더는 사용할 수 없습니다")
    
    def register_builder(self, format_type: str, builder_class: Type[ReportBuilder]):
        """
        보고서 빌더 등록
        
        Args:
            format_type: 형식 이름
            builder_class: 빌더 클래스
        """
        if not issubclass(builder_class, ReportBuilder):
            raise TypeError(f"{builder_class}는 ReportBuilder를 상속해야 합니다")
        
        self.builders[format_type] = builder_class
        self.logger.info(f"보고서 빌더 등록: {format_type}")
    
    def unregister_builder(self, format_type: str) -> bool:
        """
        보고서 빌더 등록 해제
        
        Args:
            format_type: 형식 이름
            
        Returns:
            성공 여부
        """
        if format_type in self.builders:
            del self.builders[format_type]
            self.logger.info(f"보고서 빌더 등록 해제: {format_type}")
            return True
        return False
    
    def get_builder_class(self, format_type: str) -> Optional[Type[ReportBuilder]]:
        """
        빌더 클래스 반환
        
        Args:
            format_type: 형식 이름
            
        Returns:
            빌더 클래스 또는 None
        """
        return self.builders.get(format_type)
    
    def is_format_supported(self, format_type: str) -> bool:
        """
        형식 지원 여부 확인
        
        Args:
            format_type: 형식 이름
            
        Returns:
            지원 여부
        """
        return format_type in self.builders
    
    def get_supported_formats(self) -> list:
        """
        지원되는 형식 목록 반환
        
        Returns:
            형식 목록
        """
        return list(self.builders.keys())
    
    def get_format_info(self, format_type: str) -> Dict[str, str]:
        """
        형식 정보 반환
        
        Args:
            format_type: 형식 이름
            
        Returns:
            형식 정보
        """
        if format_type not in self.builders:
            return {}
        
        builder_class = self.builders[format_type]
        
        # 임시 인스턴스 생성하여 정보 추출
        from .base import ReportOptions
        temp_instance = builder_class(ReportOptions())
        
        return {
            'name': format_type,
            'extension': temp_instance.get_file_extension(),
            'class_name': builder_class.__name__,
            'module': builder_class.__module__
        }
    
    def validate_builder(self, format_type: str) -> bool:
        """
        빌더 유효성 검증
        
        Args:
            format_type: 형식 이름
            
        Returns:
            유효 여부
        """
        if format_type not in self.builders:
            return False
        
        builder_class = self.builders[format_type]
        
        # 필수 메서드 확인
        required_methods = ['build', 'get_file_extension']
        for method in required_methods:
            if not hasattr(builder_class, method):
                self.logger.error(f"{builder_class.__name__}에 {method} 메서드가 없습니다")
                return False
        
        return True