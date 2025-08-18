# tests/unit/core/analyzers/test_color_analyzer.py
"""
ColorAnalyzer 테스트
"""

import pytest
from pathlib import Path
import tempfile
import pikepdf

from src.core.models import PDFDocument, ColorSpace
from src.core.analyzers import ColorAnalyzer


class TestColorAnalyzer:
    """ColorAnalyzer 테스트 클래스"""
    
    @pytest.fixture
    def analyzer(self):
        """ColorAnalyzer 인스턴스 생성"""
        return ColorAnalyzer()
    
    @pytest.fixture
    def sample_pdf_rgb(self):
        """RGB 색상을 사용하는 PDF 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "test_rgb.pdf"
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # RGB 색상 사용하는 컨텐츠
            content = pikepdf.Stream(pdf, b"""
                q
                1 0 0 rg
                100 100 100 100 re
                f
                Q
            """)
            page.Contents = content
            
            pdf.save(tmp_path)
            yield tmp_path
    
    @pytest.fixture
    def sample_pdf_cmyk(self):
        """CMYK 색상을 사용하는 PDF 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "test_cmyk.pdf"
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # CMYK 색상 사용하는 컨텐츠
            content = pikepdf.Stream(pdf, b"""
                q
                0 1 1 0 k
                200 200 100 100 re
                f
                Q
            """)
            page.Contents = content
            
            pdf.save(tmp_path)
            yield tmp_path
    
    @pytest.fixture
    def sample_pdf_with_transparency(self):
        """투명도가 있는 PDF 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "test_transparency.pdf"
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # ExtGState 리소스 추가
            gs = pikepdf.Dictionary({
                "/Type": pikepdf.Name("/ExtGState"),
                "/CA": 0.5,  # 선 투명도
                "/ca": 0.7   # 채우기 투명도
            })
            
            if "/Resources" not in page:
                page.Resources = pikepdf.Dictionary()
            if "/ExtGState" not in page.Resources:
                page.Resources.ExtGState = pikepdf.Dictionary()
            
            page.Resources.ExtGState["/GS1"] = gs
            
            pdf.save(tmp_path)
            yield tmp_path
    
    def test_analyzer_initialization(self, analyzer):
        """분석기 초기화 테스트"""
        assert analyzer.name == "ColorAnalyzer"
        assert analyzer.can_analyze(None) is True
        
        # 색상 공간 패턴 확인
        assert 'RGB' in analyzer.color_space_patterns
        assert 'CMYK' in analyzer.color_space_patterns
        assert 'Grayscale' in analyzer.color_space_patterns
    
    def test_analyze_rgb_colors(self, analyzer, sample_pdf_rgb):
        """RGB 색상 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf_rgb)
        result = analyzer.analyze(document, sample_pdf_rgb)
        
        # 결과 확인
        assert 'color_spaces' in result
        assert 'RGB' in result['color_spaces']
        assert result['rgb_usage'] > 0
        assert 'color_info' in result
        
        # ColorInfo 객체 확인
        color_info = result['color_info']
        assert ColorSpace.RGB in color_info.color_spaces_used
    
    def test_analyze_cmyk_colors(self, analyzer, sample_pdf_cmyk):
        """CMYK 색상 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf_cmyk)
        result = analyzer.analyze(document, sample_pdf_cmyk)
        
        # 결과 확인
        assert 'CMYK' in result['color_spaces']
        assert result['cmyk_usage'] > 0
        
        # ColorInfo 객체 확인
        color_info = result['color_info']
        assert ColorSpace.CMYK in color_info.color_spaces_used
    
    def test_analyze_transparency(self, analyzer, sample_pdf_with_transparency):
        """투명도 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf_with_transparency)
        result = analyzer.analyze(document, sample_pdf_with_transparency)
        
        # 투명도 감지 확인
        assert result['has_transparency'] is True
        
        color_info = result['color_info']
        assert color_info.has_transparency is True
    
    def test_spot_color_detection(self, analyzer):
        """별색 감지 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test_spot.pdf"
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # Separation 색상 공간 (별색)
            separation = pikepdf.Array([
                pikepdf.Name("/Separation"),
                pikepdf.Name("/Pantone_185_C"),  # Name must start with /
                pikepdf.Name("/DeviceCMYK"),
                pikepdf.Stream(pdf, b"{ dup 0.0 exch 1.0 exch sub 1.0 }")
            ])
            
            if "/Resources" not in page:
                page.Resources = pikepdf.Dictionary()
            if "/ColorSpace" not in page.Resources:
                page.Resources.ColorSpace = pikepdf.Dictionary()
            
            page.Resources.ColorSpace["/CS1"] = separation
            
            pdf.save(pdf_path)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            # 별색 감지 확인
            assert len(result['spot_colors']) > 0
            assert 'Pantone_185_C' in result['spot_colors'][0]
    
    def test_overprint_detection(self, analyzer):
        """오버프린트 설정 감지 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test_overprint.pdf"
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # 오버프린트 설정이 있는 ExtGState
            gs = pikepdf.Dictionary({
                "/Type": pikepdf.Name("/ExtGState"),
                "/OP": True,   # 선 오버프린트
                "/op": False   # 채우기 오버프린트
            })
            
            if "/Resources" not in page:
                page.Resources = pikepdf.Dictionary()
            if "/ExtGState" not in page.Resources:
                page.Resources.ExtGState = pikepdf.Dictionary()
            
            page.Resources.ExtGState["/GS1"] = gs
            
            pdf.save(pdf_path)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            assert result['has_overprint'] is True
    
    def test_mixed_color_spaces(self, analyzer):
        """혼합 색상 공간 분석 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test_mixed.pdf"
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # RGB와 CMYK를 모두 사용하는 컨텐츠
            content = pikepdf.Stream(pdf, b"""
                q
                1 0 0 rg
                100 100 50 50 re
                f
                0 1 1 0 k
                200 200 50 50 re
                f
                Q
            """)
            page.Contents = content
            
            pdf.save(pdf_path)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            # 두 색상 공간 모두 감지되어야 함
            assert 'RGB' in result['color_spaces']
            assert 'CMYK' in result['color_spaces']
            
            color_info = result['color_info']
            assert color_info.uses_rgb is True
            assert color_info.uses_cmyk is True
            assert color_info.is_print_ready is False  # RGB 사용으로 인쇄 준비 안됨
    
    def test_color_mode_summary(self, analyzer):
        """색상 모드 요약 테스트"""
        # 다양한 색상 조합 테스트
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test_summary.pdf"
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # Separation 추가
            separation = pikepdf.Array([
                pikepdf.Name("/Separation"),
                pikepdf.Name("/Special_Red"),  # Name must start with /
                pikepdf.Name("/DeviceCMYK"),
                pikepdf.Stream(pdf, b"{ }")
            ])
            
            if "/Resources" not in page:
                page.Resources = pikepdf.Dictionary()
            if "/ColorSpace" not in page.Resources:
                page.Resources.ColorSpace = pikepdf.Dictionary()
            
            page.Resources.ColorSpace["/CS1"] = separation
            
            # CMYK 컨텐츠
            content = pikepdf.Stream(pdf, b"0 1 1 0 k 100 100 100 100 re f")
            page.Contents = content
            
            pdf.save(pdf_path)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            color_info = result['color_info']
            summary = color_info.color_mode_summary
            
            # CMYK와 Spot이 포함되어야 함
            assert 'CMYK' in summary
            assert 'Spot' in summary
    
    def test_grayscale_detection(self, analyzer):
        """그레이스케일 감지 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test_grayscale.pdf"
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # 그레이스케일 컨텐츠
            content = pikepdf.Stream(pdf, b"""
                q
                0.5 g
                100 100 100 100 re
                f
                Q
            """)
            page.Contents = content
            
            pdf.save(pdf_path)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            assert 'Grayscale' in result['color_spaces']
    
    def test_dependencies(self, analyzer):
        """의존성 확인 테스트"""
        deps = analyzer.get_dependencies()
        
        assert 'pikepdf' in deps
        assert deps['pikepdf'] is True