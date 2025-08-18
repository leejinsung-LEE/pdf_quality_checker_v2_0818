"""
PDFDocument 모델 단위 테스트

PDFDocument와 관련 클래스들(PageInfo, PageSize, Rectangle, BleedInfo)의
동작을 검증하는 테스트입니다.
"""

import pytest
from pathlib import Path
import tempfile
import os
from datetime import datetime

# 테스트할 모듈들을 임포트
# 실제 프로젝트에서는 경로 설정이 필요할 수 있습니다
from src.core.models.pdf_document import (
    PDFDocument, PageInfo, PageSize, Rectangle, BleedInfo, PaperSize
)


class TestRectangle:
    """Rectangle 클래스 테스트"""
    
    def test_rectangle_creation(self):
        """Rectangle 객체 생성 테스트"""
        rect = Rectangle(10, 20, 100, 200)
        assert rect.x == 10
        assert rect.y == 20
        assert rect.width == 100
        assert rect.height == 200
        assert rect.area == 20000
    
    def test_rectangle_contains(self):
        """Rectangle 포함 관계 테스트"""
        outer = Rectangle(0, 0, 100, 100)
        inner = Rectangle(10, 10, 50, 50)
        outside = Rectangle(200, 200, 50, 50)
        
        assert outer.contains(inner) is True
        assert inner.contains(outer) is False
        assert outer.contains(outside) is False
    
    def test_rectangle_intersects(self):
        """Rectangle 교차 테스트"""
        rect1 = Rectangle(0, 0, 100, 100)
        rect2 = Rectangle(50, 50, 100, 100)  # 일부 겹침
        rect3 = Rectangle(200, 200, 50, 50)  # 겹치지 않음
        
        assert rect1.intersects(rect2) is True
        assert rect2.intersects(rect1) is True
        assert rect1.intersects(rect3) is False


class TestPageSize:
    """PageSize 클래스 테스트"""
    
    def test_page_size_creation(self):
        """PageSize 객체 생성 테스트"""
        # A4 크기로 생성
        page_size = PageSize(210.0, 297.0)
        assert page_size.width_mm == 210.0
        assert page_size.height_mm == 297.0
        assert page_size.name == "A4"  # 자동으로 판별되어야 함
        assert page_size.orientation == "portrait"
    
    def test_page_size_landscape(self):
        """가로 방향 페이지 테스트"""
        page_size = PageSize(297.0, 210.0)
        assert page_size.name == "A4"
        assert page_size.orientation == "landscape"
    
    def test_page_size_custom(self):
        """사용자 정의 크기 테스트"""
        page_size = PageSize(123.4, 567.8)
        assert page_size.name == "Custom"
        assert page_size.width_mm == 123.4
        assert page_size.height_mm == 567.8
    
    def test_page_size_equality(self):
        """PageSize 동등성 테스트 (1mm 오차 허용)"""
        size1 = PageSize(210.0, 297.0)
        size2 = PageSize(210.5, 297.3)  # 1mm 이내 차이
        size3 = PageSize(215.0, 297.0)  # 1mm 초과 차이
        
        assert size1 == size2
        assert size1 != size3
    
    def test_page_size_rotation(self):
        """페이지 회전 테스트"""
        original = PageSize(210.0, 297.0)
        rotated = original.rotated()
        
        assert rotated.width_mm == 297.0
        assert rotated.height_mm == 210.0
        assert rotated.name == original.name


class TestBleedInfo:
    """BleedInfo 클래스 테스트"""
    
    def test_bleed_info_creation(self):
        """BleedInfo 객체 생성 테스트"""
        bleed = BleedInfo(top=3.0, bottom=3.0, left=3.0, right=3.0)
        assert bleed.top == 3.0
        assert bleed.has_proper_bleed is True
        assert bleed.is_uniform is True
        assert bleed.minimum == 3.0
        assert bleed.average == 3.0
    
    def test_bleed_info_insufficient(self):
        """불충분한 재단선 테스트"""
        bleed = BleedInfo(top=2.0, bottom=3.0, left=3.0, right=3.0)
        assert bleed.has_proper_bleed is False
        assert bleed.is_uniform is False
        assert bleed.minimum == 2.0
        assert bleed.average == 2.75
    
    def test_bleed_info_string_representation(self):
        """BleedInfo 문자열 표현 테스트"""
        uniform_bleed = BleedInfo(3.0, 3.0, 3.0, 3.0)
        assert "3.0mm (uniform)" in str(uniform_bleed)
        
        varied_bleed = BleedInfo(3.0, 3.5, 2.5, 3.0)
        bleed_str = str(varied_bleed)
        assert "T:3.0" in bleed_str
        assert "B:3.5" in bleed_str


class TestPageInfo:
    """PageInfo 클래스 테스트"""
    
    def test_page_info_creation(self):
        """PageInfo 객체 생성 테스트"""
        page = PageInfo(
            page_number=1,
            width_mm=210.0,
            height_mm=297.0,
            rotation=0,
            has_transparency=False,
            has_overprint=False
        )
        
        assert page.page_number == 1
        assert page.paper_size == "A4"
        assert page.orientation == "portrait"
        assert page.effective_rotation == 0
    
    def test_page_info_with_rotation(self):
        """회전된 페이지 정보 테스트"""
        page = PageInfo(
            page_number=1,
            width_mm=210.0,
            height_mm=297.0,
            rotation=90
        )
        
        rotated_size = page.get_rotated_size()
        assert rotated_size == (297.0, 210.0)
        
        # 270도 회전
        page.rotation = 270
        assert page.get_rotated_size() == (297.0, 210.0)
        
        # 180도 회전
        page.rotation = 180
        assert page.get_rotated_size() == (210.0, 297.0)
    
    def test_page_info_with_bleed(self):
        """재단선 정보가 있는 페이지 테스트"""
        bleed = BleedInfo(3.0, 3.0, 3.0, 3.0)
        page = PageInfo(
            page_number=1,
            width_mm=210.0,
            height_mm=297.0,
            bleed_info=bleed
        )
        
        assert page.bleed_info is not None
        assert page.bleed_info.has_proper_bleed is True


class TestPDFDocument:
    """PDFDocument 클래스 테스트"""
    
    @pytest.fixture
    def temp_pdf_file(self):
        """테스트용 임시 PDF 파일 생성"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            # 간단한 PDF 헤더만 작성 (실제 PDF는 아니지만 테스트용으로 충분)
            f.write(b'%PDF-1.4\n')
            f.write(b'Test content for hash calculation\n')
            temp_path = f.name
        
        yield Path(temp_path)
        
        # 테스트 후 정리
        try:
            os.unlink(temp_path)
        except:
            pass
    
    def test_pdf_document_creation_from_path(self, temp_pdf_file):
        """파일 경로로부터 PDFDocument 생성 테스트"""
        doc = PDFDocument.from_path(temp_pdf_file)
        
        assert doc.path == temp_pdf_file
        assert doc.file_size > 0
        assert len(doc.file_hash) == 64  # SHA256 해시 길이
        assert isinstance(doc.created_at, datetime)
        assert doc.filename == temp_pdf_file.stem
        assert doc.full_filename == temp_pdf_file.name
    
    def test_pdf_document_validation(self):
        """PDFDocument 유효성 검증 테스트"""
        # 존재하지 않는 파일
        with pytest.raises(ValueError, match="PDF 파일이 존재하지 않습니다"):
            PDFDocument(
                path=Path("nonexistent.pdf"),
                file_hash="dummy",
                file_size=0,
                created_at=datetime.now()
            )
        
        # PDF가 아닌 파일
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            txt_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="PDF 파일이 아닙니다"):
                PDFDocument(
                    path=txt_path,
                    file_hash="dummy",
                    file_size=0,
                    created_at=datetime.now()
                )
        finally:
            os.unlink(txt_path)
    
    def test_pdf_document_page_management(self, temp_pdf_file):
        """페이지 정보 관리 테스트"""
        doc = PDFDocument.from_path(temp_pdf_file)
        
        # 초기 상태
        assert doc.page_count == 0
        assert len(doc.pages) == 0
        assert doc.is_uniform_size is True
        
        # 첫 번째 페이지 추가 (A4)
        page1 = PageInfo(1, 210.0, 297.0)
        doc.add_page_info(page1)
        
        assert doc.page_count == 1
        assert doc.is_uniform_size is True
        assert doc.dominant_page_size is not None
        assert doc.dominant_page_size.name == "A4"
        
        # 같은 크기의 페이지 추가
        page2 = PageInfo(2, 210.5, 297.3)  # 약간의 오차
        doc.add_page_info(page2)
        
        assert doc.page_count == 2
        assert doc.is_uniform_size is True
        
        # 다른 크기의 페이지 추가 (A3)
        page3 = PageInfo(3, 297.0, 420.0)
        doc.add_page_info(page3)
        
        assert doc.page_count == 3
        assert doc.is_uniform_size is False
        assert len(doc.size_variations) == 2
        assert doc.dominant_page_size.name == "A4"  # 여전히 A4가 더 많음
    
    def test_pdf_document_mixed_orientations(self, temp_pdf_file):
        """혼합된 페이지 방향 테스트"""
        doc = PDFDocument.from_path(temp_pdf_file)
        
        # 세로 방향 페이지
        doc.add_page_info(PageInfo(1, 210.0, 297.0))
        assert doc.has_mixed_orientations is False
        
        # 가로 방향 페이지 추가
        doc.add_page_info(PageInfo(2, 297.0, 210.0))
        assert doc.has_mixed_orientations is True
    
    def test_pdf_document_bleed_check(self, temp_pdf_file):
        """재단선 확인 테스트"""
        doc = PDFDocument.from_path(temp_pdf_file)
        
        # 재단선이 있는 페이지
        page1 = PageInfo(1, 210.0, 297.0)
        page1.bleed_info = BleedInfo(3.0, 3.0, 3.0, 3.0)
        doc.add_page_info(page1)
        
        assert doc.has_proper_bleed_all_pages is True
        
        # 재단선이 없는 페이지 추가
        page2 = PageInfo(2, 210.0, 297.0)
        page2.bleed_info = BleedInfo(0.0, 0.0, 0.0, 0.0)
        doc.add_page_info(page2)
        
        assert doc.has_proper_bleed_all_pages is False
    
    def test_pdf_document_string_representation(self, temp_pdf_file):
        """문자열 표현 테스트"""
        doc = PDFDocument.from_path(temp_pdf_file)
        doc.add_page_info(PageInfo(1, 210.0, 297.0))
        doc.page_count = 10  # 직접 설정
        doc.file_size = 1024 * 1024 * 5  # 5MB
        
        str_repr = str(doc)
        assert temp_pdf_file.name in str_repr
        assert "10 pages" in str_repr
        assert "5.0MB" in str_repr
        assert "A4" in str_repr


class TestPaperSize:
    """PaperSize Enum 테스트"""
    
    def test_paper_size_from_dimensions(self):
        """크기로부터 용지 규격 판별 테스트"""
        # 정확한 A4 크기
        assert PaperSize.from_dimensions(210.0, 297.0) == PaperSize.A4
        
        # 약간의 오차가 있는 A4
        assert PaperSize.from_dimensions(211.0, 296.0) == PaperSize.A4
        
        # 회전된 A4 (가로)
        assert PaperSize.from_dimensions(297.0, 210.0) == PaperSize.A4
        
        # Letter 크기
        assert PaperSize.from_dimensions(215.9, 279.4) == PaperSize.LETTER
        
        # 사용자 정의 크기
        assert PaperSize.from_dimensions(123.0, 456.0) == PaperSize.CUSTOM
    
    def test_paper_size_tolerance(self):
        """용지 크기 판별 시 허용 오차 테스트"""
        # 2mm 오차는 허용 (기본값)
        assert PaperSize.from_dimensions(212.0, 297.0) == PaperSize.A4
        
        # 3mm 오차는 허용되지 않음
        assert PaperSize.from_dimensions(213.0, 297.0) == PaperSize.CUSTOM
        
        # 허용 오차를 늘려서 테스트
        assert PaperSize.from_dimensions(213.0, 297.0, tolerance=3.0) == PaperSize.A4


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"])