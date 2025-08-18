# -*- coding: utf-8 -*-
"""
PDF 리소스 관리자

PDF 파일을 안전하게 열고 닫는 context manager를 제공합니다.
메모리 누수를 방지하기 위해 자동으로 리소스를 정리합니다.
"""

import gc
import logging
from pathlib import Path
from typing import Optional, Union
from contextlib import contextmanager

from ..models import PDFDocument


class PDFResourceManager:
    """PDF 리소스 관리자"""
    
    def __init__(self, pdf_path: Union[str, Path]):
        """
        초기화
        
        Args:
            pdf_path: PDF 파일 경로
        """
        self.pdf_path = Path(pdf_path)
        self.document: Optional[PDFDocument] = None
        self.logger = logging.getLogger(__name__)
        
    def __enter__(self):
        """컨텍스트 진입 - PDF 문서 열기"""
        try:
            self.document = PDFDocument.from_path(self.pdf_path)
            return self.document
        except Exception as e:
            self.logger.error(f"PDF 열기 실패: {e}")
            raise
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 종료 - 리소스 정리"""
        if self.document:
            try:
                # PDFDocument가 close 메서드를 가지고 있는지 확인
                if hasattr(self.document, 'close'):
                    self.document.close()
                    
                # pikepdf 문서인 경우
                if hasattr(self.document, '_pdf') and self.document._pdf:
                    if hasattr(self.document._pdf, 'close'):
                        self.document._pdf.close()
                        
                # PyMuPDF 문서인 경우  
                if hasattr(self.document, '_doc') and self.document._doc:
                    if hasattr(self.document._doc, 'close'):
                        self.document._doc.close()
                        
            except Exception as e:
                self.logger.warning(f"PDF 닫기 중 오류: {e}")
            finally:
                self.document = None
                
        # 가비지 컬렉션 강제 실행
        gc.collect()
        
        # 예외를 재발생시키지 않음 (False 반환)
        return False


@contextmanager
def open_pdf_safely(pdf_path: Union[str, Path]):
    """
    PDF를 안전하게 열고 닫는 컨텍스트 매니저
    
    사용 예:
        with open_pdf_safely('file.pdf') as document:
            # document 사용
            pass
        # 자동으로 리소스 정리됨
    
    Args:
        pdf_path: PDF 파일 경로
        
    Yields:
        PDFDocument: PDF 문서 객체
    """
    manager = PDFResourceManager(pdf_path)
    try:
        document = manager.__enter__()
        yield document
    finally:
        manager.__exit__(None, None, None)