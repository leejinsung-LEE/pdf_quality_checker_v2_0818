# src/core/analyzers/metadata_analyzer.py
"""
PDF 메타데이터 분석기

PDF 파일의 기본 정보와 메타데이터를 추출합니다.
"""

from typing import Dict, Any
from pathlib import Path
import pikepdf
from datetime import datetime

from .base_analyzer import BaseAnalyzer
from ..models import PDFDocument


class MetadataAnalyzer(BaseAnalyzer):
    """
    PDF 메타데이터 분석기
    
    PDF 파일의 다음 정보를 추출합니다:
    - PDF 버전
    - 페이지 수
    - 암호화 상태
    - 선형화(웹 최적화) 상태
    - 문서 메타데이터 (제목, 저자, 생성일 등)
    """
    
    def __init__(self):
        """메타데이터 분석기 초기화"""
        super().__init__("MetadataAnalyzer")
    
    def analyze(self, document: PDFDocument, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF 메타데이터 분석
        
        Args:
            document: PDF 문서 모델 객체
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: 메타데이터 분석 결과
        """
        # 메타데이터 분석 중
        
        result = {}
        
        try:
            # pikepdf로 PDF 열기
            with pikepdf.open(pdf_path) as pdf:
                # 기본 정보 추출
                result['page_count'] = len(pdf.pages)
                result['pdf_version'] = str(pdf.pdf_version) if pdf.pdf_version else ''
                result['is_encrypted'] = pdf.is_encrypted
                result['is_linearized'] = getattr(pdf, 'is_linearized', False)
                
                # 파일 크기 정보
                result['file_size'] = document.file_size
                result['file_size_mb'] = round(document.file_size / (1024 * 1024), 2)
                
                # 메타데이터 추출
                metadata = self._extract_metadata(pdf)
                result['metadata'] = metadata
                
                # 문서 모델 업데이트
                document.page_count = result['page_count']
                document.pdf_version = result['pdf_version']
                document.is_encrypted = result['is_encrypted']
                document.metadata = metadata
                
                # 메타데이터 분석 완료
                
        except Exception as e:
            # 메타데이터 분석 중 오류 발생
            raise
        
        return result
    
    def _extract_metadata(self, pdf_obj: pikepdf.Pdf) -> Dict[str, str]:
        """
        PDF 문서 메타데이터 추출
        
        Args:
            pdf_obj: pikepdf PDF 객체
            
        Returns:
            Dict[str, str]: 메타데이터 정보
        """
        metadata = {
            'title': '',
            'author': '',
            'subject': '',
            'keywords': '',
            'creator': '',      # 원본 문서를 만든 프로그램
            'producer': '',     # PDF를 생성한 프로그램
            'creation_date': '',
            'modification_date': ''
        }
        
        if not pdf_obj.docinfo:
            return metadata
        
        # 메타데이터 필드 매핑
        field_mapping = {
            '/Title': 'title',
            '/Author': 'author',
            '/Subject': 'subject',
            '/Keywords': 'keywords',
            '/Creator': 'creator',
            '/Producer': 'producer'
        }
        
        # 텍스트 필드 추출
        for pdf_key, metadata_key in field_mapping.items():
            if pdf_key in pdf_obj.docinfo:
                try:
                    value = pdf_obj.docinfo[pdf_key]
                    # pikepdf String 객체를 문자열로 변환
                    if hasattr(value, '__str__'):
                        metadata[metadata_key] = str(value)
                except Exception:
                    # 변환 실패 시 빈 문자열 유지
                    pass
        
        # 날짜 필드 추출
        date_fields = {
            '/CreationDate': 'creation_date',
            '/ModDate': 'modification_date'
        }
        
        for pdf_key, metadata_key in date_fields.items():
            if pdf_key in pdf_obj.docinfo:
                try:
                    date_value = pdf_obj.docinfo[pdf_key]
                    # PDF 날짜 형식 처리
                    if hasattr(date_value, '__str__'):
                        date_str = str(date_value)
                        # PDF 날짜 형식 파싱 시도
                        metadata[metadata_key] = self._parse_pdf_date(date_str)
                except Exception:
                    # 날짜 파싱 실패 시 원본 유지
                    metadata[metadata_key] = str(date_value) if date_value else ''
        
        return metadata
    
    def _parse_pdf_date(self, date_str: str) -> str:
        """
        PDF 날짜 형식 파싱
        
        PDF 날짜 형식: D:YYYYMMDDHHmmSS[+/-]HH'mm'
        
        Args:
            date_str: PDF 날짜 문자열
            
        Returns:
            str: 파싱된 날짜 문자열
        """
        if not date_str:
            return ''
        
        # D: 접두사 제거
        if date_str.startswith('D:'):
            date_str = date_str[2:]
        
        try:
            # 기본 날짜 부분 추출 (YYYYMMDDHHmmSS)
            if len(date_str) >= 14:
                year = int(date_str[0:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                hour = int(date_str[8:10])
                minute = int(date_str[10:12])
                second = int(date_str[12:14])
                
                dt = datetime(year, month, day, hour, minute, second)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            elif len(date_str) >= 8:
                # 날짜만 있는 경우
                year = int(date_str[0:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                
                dt = datetime(year, month, day)
                return dt.strftime('%Y-%m-%d')
        except (ValueError, IndexError):
            # 파싱 실패 시 원본 반환
            pass
        
        return date_str
    
    def can_analyze(self, document: PDFDocument) -> bool:
        """
        이 분석기가 주어진 문서를 분석할 수 있는지 확인
        
        메타데이터 분석은 모든 PDF에 대해 가능합니다.
        
        Args:
            document: PDF 문서 모델 객체
            
        Returns:
            bool: 항상 True
        """
        return True
    
    def get_dependencies(self) -> Dict[str, bool]:
        """
        분석기의 의존성 상태 확인
        
        Returns:
            Dict[str, bool]: pikepdf 사용 가능 여부
        """
        try:
            import pikepdf
            return {'pikepdf': True}
        except ImportError:
            return {'pikepdf': False}