# tests/unit/core/analyzers/test_page_analyzer.py
"""
PageAnalyzer 테스트
"""

import pytest
from pathlib import Path
import tempfile
import pikepdf

from src.core.models import PDFDocument, PageInfo
from src.core.analyzers import PageAnalyzer


class TestPageAnalyzer:
    """PageAnalyzer 테스트 클래스"""
    
    @pytest.fixture
    def analyzer(self):
        """PageAnalyzer 인스턴스 생성"""
        return PageAnalyzer()
    
    @pytest.fixture
    def sample_pdf_single_size(self):
        """단일 크기 페이지를 가진 PDF 생성"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            
            # A4 크기 페이지 3개 추가
            for _ in range(3):
                pdf.add_blank_page(page_size=(595, 842))  # A4 (210x297mm)
            
            pdf.save(tmp.name)
            yield Path(tmp.name)
            Path(tmp.name).unlink()
    
    @pytest.fixture
    def sample_pdf_mixed_sizes(self):
        """혼합 크기 페이지를 가진 PDF 생성"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            
            # 다양한 크기 페이지 추가
            pdf.add_blank_page(page_size=(595, 842))    # A4
            pdf.add_blank_page(page_size=(842, 595))    # A4 가로
            pdf.add_blank_page(page_size=(842, 1191))   # A3
            
            pdf.save(tmp.name)
            yield Path(tmp.name)
            Path(tmp.name).unlink()
    
    @pytest.fixture
    def sample_pdf_with_rotation(self):
        """회전된 페이지를 가진 PDF 생성"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            
            # 페이지 추가 및 회전
            page1 = pdf.add_blank_page(page_size=(595, 842))
            page2 = pdf.add_blank_page(page_size=(595, 842))
            page2.Rotate = 90  # 90도 회전
            
            pdf.save(tmp.name)
            yield Path(tmp.name)
            Path(tmp.name).unlink()
    
    def test_analyzer_initialization(self, analyzer):
        """분석기 초기화 테스트"""
        assert analyzer.name == "PageAnalyzer"
        assert analyzer.can_analyze(None) is True
    
    def test_analyze_single_size_pages(self, analyzer, sample_pdf_single_size):
        """단일 크기 페이지 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf_single_size)
        result = analyzer.analyze(document, sample_pdf_single_size)
        
        # 결과 확인
        assert result['total_pages'] == 3
        assert result['has_mixed_sizes'] is False
        assert result['has_mixed_orientations'] is False
        assert len(result['pages']) == 3
        
        # 페이지 크기 확인
        assert len(result['page_sizes']) == 1
        assert '210x297mm' in list(result['page_sizes'].keys())[0]
    
    def test_analyze_mixed_size_pages(self, analyzer, sample_pdf_mixed_sizes):
        """혼합 크기 페이지 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf_mixed_sizes)
        result = analyzer.analyze(document, sample_pdf_mixed_sizes)
        
        # 결과 확인
        assert result['total_pages'] == 3
        assert result['has_mixed_sizes'] is True
        assert result['has_mixed_orientations'] is True
        assert len(result['page_sizes']) > 1
    
    def test_analyze_page_rotation(self, analyzer, sample_pdf_with_rotation):
        """페이지 회전 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf_with_rotation)
        result = analyzer.analyze(document, sample_pdf_with_rotation)
        
        # 회전 정보 확인
        assert result['pages'][0]['rotation'] == 0
        assert result['pages'][1]['rotation'] == 90
    
    def test_paper_size_detection(self, analyzer):
        """용지 크기 감지 테스트"""
        test_cases = [
            (210, 297, 'A4'),
            (297, 210, 'A4 (Landscape)'),
            (297, 420, 'A3'),
            (216, 279, 'Letter'),
            (200, 200, 'Custom')
        ]
        
        for width, height, expected in test_cases:
            result = analyzer._detect_paper_size(width, height)
            assert result == expected
    
    def test_bleed_analysis(self, analyzer):
        """재단선 분석 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            
            # TrimBox가 있는 페이지 생성
            page = pdf.add_blank_page(page_size=(612, 792))  # Letter
            # MediaBox보다 작은 TrimBox 설정 (3mm 재단선)
            page.TrimBox = [8.5, 8.5, 603.5, 783.5]  # 약 3mm 안쪽
            
            pdf.save(tmp.name)
            pdf_path = Path(tmp.name)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            # 재단선 정보 확인
            page_info = result['pages'][0]
            assert 'bleed' in page_info
            
            pdf_path.unlink()
    
    def test_document_page_info_update(self, analyzer, sample_pdf_single_size):
        """문서 객체의 페이지 정보 업데이트 테스트"""
        document = PDFDocument.from_path(sample_pdf_single_size)
        
        # 초기 상태
        assert len(document.pages) == 0
        
        # 분석 수행
        analyzer.analyze(document, sample_pdf_single_size)
        
        # 페이지 정보 업데이트 확인
        assert len(document.pages) == 3
        assert document.is_uniform_size is True
        assert document.dominant_page_size is not None
        
        # 각 페이지 정보 확인
        for page in document.pages:
            assert isinstance(page, PageInfo)
            assert page.width_mm > 0
            assert page.height_mm > 0
    
    def test_page_orientation(self, analyzer):
        """페이지 방향 확인 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            
            # 세로 페이지
            pdf.add_blank_page(page_size=(595, 842))  # A4 세로
            # 가로 페이지
            pdf.add_blank_page(page_size=(842, 595))  # A4 가로
            
            pdf.save(tmp.name)
            pdf_path = Path(tmp.name)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            assert result['pages'][0]['orientation'] == 'portrait'
            assert result['pages'][1]['orientation'] == 'landscape'
            
            pdf_path.unlink()
    
    def test_dominant_size_calculation(self, analyzer):
        """주요 페이지 크기 계산 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            
            # A4 페이지 3개, A3 페이지 1개
            for _ in range(3):
                pdf.add_blank_page(page_size=(595, 842))  # A4
            pdf.add_blank_page(page_size=(842, 1191))  # A3
            
            pdf.save(tmp.name)
            pdf_path = Path(tmp.name)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            # A4가 dominant size여야 함
            assert result['dominant_size'] is not None
            assert result['dominant_size']['count'] == 3
            assert result['dominant_size']['percentage'] == 75.0
            
            pdf_path.unlink()
    
    def test_dependencies(self, analyzer):
        """의존성 확인 테스트"""
        deps = analyzer.get_dependencies()
        
        assert 'pikepdf' in deps
        assert deps['pikepdf'] is True