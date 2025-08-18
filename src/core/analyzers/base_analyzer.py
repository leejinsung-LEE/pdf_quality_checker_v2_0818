# src/core/analyzers/base_analyzer.py
"""
기본 분석기 추상 클래스

모든 PDF 분석기가 상속받아야 하는 기본 클래스입니다.
각 분석기는 PDF의 특정 측면을 담당합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from ..models import PDFDocument


class BaseAnalyzer(ABC):
    """
    PDF 분석기 추상 베이스 클래스
    
    모든 분석기는 이 클래스를 상속받아 구현해야 합니다.
    각 분석기는 독립적으로 동작하며, 오류 발생 시에도
    다른 분석기에 영향을 주지 않습니다.
    """
    
    def __init__(self, name: str):
        """
        분석기 초기화
        
        Args:
            name: 분석기 이름 (로깅 및 디버깅용)
        """
        self.name = name
        self._is_initialized = False
    
    @abstractmethod
    def analyze(self, document: PDFDocument, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF 분석 수행
        
        Args:
            document: PDF 문서 모델 객체
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: 분석 결과
            
        Raises:
            AnalysisError: 분석 중 오류 발생 시
        """
        pass
    
    @abstractmethod
    def can_analyze(self, document: PDFDocument) -> bool:
        """
        이 분석기가 주어진 문서를 분석할 수 있는지 확인
        
        Args:
            document: PDF 문서 모델 객체
            
        Returns:
            bool: 분석 가능 여부
        """
        pass
    
    def initialize(self) -> bool:
        """
        분석기 초기화
        
        필요한 리소스나 외부 도구를 준비합니다.
        
        Returns:
            bool: 초기화 성공 여부
        """
        self._is_initialized = True
        return True
    
    def cleanup(self):
        """
        분석기 정리
        
        사용한 리소스를 해제합니다.
        """
        self._is_initialized = False
    
    def is_ready(self) -> bool:
        """
        분석기 준비 상태 확인
        
        Returns:
            bool: 분석 준비 완료 여부
        """
        return self._is_initialized
    
    def get_dependencies(self) -> Dict[str, bool]:
        """
        분석기의 의존성 상태 확인
        
        Returns:
            Dict[str, bool]: 의존성 이름과 사용 가능 여부
        """
        return {}
    
    def _safe_analyze(self, document: PDFDocument, pdf_path: Path) -> Dict[str, Any]:
        """
        안전한 분석 수행 (예외 처리 포함)
        
        Args:
            document: PDF 문서 모델 객체
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: 분석 결과 또는 오류 정보
        """
        try:
            # 초기화 확인
            if not self.is_ready():
                if not self.initialize():
                    return {
                        'error': f'{self.name} 초기화 실패',
                        'status': 'initialization_failed'
                    }
            
            # 분석 가능 여부 확인
            if not self.can_analyze(document):
                return {
                    'error': f'{self.name}이(가) 이 문서를 분석할 수 없습니다',
                    'status': 'cannot_analyze'
                }
            
            # 실제 분석 수행
            result = self.analyze(document, pdf_path)
            result['status'] = 'success'
            result['analyzer'] = self.name
            return result
            
        except Exception as e:
            # 오류 발생 시 안전하게 처리
            return {
                'error': str(e),
                'status': 'error',
                'analyzer': self.name,
                'exception_type': type(e).__name__
            }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"{self.name} Analyzer"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return f"{self.__class__.__name__}(name='{self.name}')"


class AnalysisError(Exception):
    """분석 중 발생하는 오류"""
    
    def __init__(self, message: str, analyzer_name: str = None, details: Dict[str, Any] = None):
        """
        분석 오류 초기화
        
        Args:
            message: 오류 메시지
            analyzer_name: 오류가 발생한 분석기 이름
            details: 추가 오류 정보
        """
        super().__init__(message)
        self.analyzer_name = analyzer_name
        self.details = details or {}