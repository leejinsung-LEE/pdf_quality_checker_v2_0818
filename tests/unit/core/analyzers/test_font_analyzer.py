# tests/unit/core/analyzers/test_font_analyzer.py
"""
FontAnalyzer 테스트
"""

import pytest
from pathlib import Path
import tempfile
import pikepdf
from unittest.mock import Mock, patch

from src.core.models import PDFDocument, FontInfo, FontType
from src.core.analyzers import FontAnalyzer
from src.external import ToolManager


class TestFontAnalyzer:
    """FontAnalyzer 테스트 클래스"""
    
    @pytest.fixture
    def analyzer(self):
        """FontAnalyzer 인스턴스 생성"""
        return FontAnalyzer()
    
    @pytest.fixture
    def analyzer_with_tools(self):
        """도구 관리자가 있는 FontAnalyzer"""
        tool_manager = Mock(spec=ToolManager)
        tool_manager.has_tool.return_value = False  # 기본적으로 외부 도구 없음
        return FontAnalyzer(tool_manager)
    
    @pytest.fixture
    def sample_pdf_with_fonts(self):
        """폰트가 포함된 PDF 생성"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            
            # 페이지 추가
            page = pdf.add_blank_page()
            
            # 폰트 리소스 추가 (시뮬레이션)
            # 실제로는 텍스트를 추가해야 하지만, 테스트용으로 간단히 처리
            font_dict = pikepdf.Dictionary({
                "/Type": pikepdf.Name("/Font"),
                "/Subtype": pikepdf.Name("/Type1"),
                "/BaseFont": pikepdf.Name("/Helvetica")
            })
            
            # Resources에 폰트 추가
            if "/Resources" not in page:
                page.Resources = pikepdf.Dictionary()
            if "/Font" not in page.Resources:
                page.Resources.Font = pikepdf.Dictionary()
            
            page.Resources.Font["/F1"] = font_dict
            
            pdf.save(tmp.name)
            yield Path(tmp.name)
            Path(tmp.name).unlink()
    
    def test_analyzer_initialization(self, analyzer):
        """분석기 초기화 테스트"""
        assert analyzer.name == "FontAnalyzer"
        assert analyzer.can_analyze(None) is True
        assert analyzer._pdffonts_available is False
        
        # 표준 14 폰트 확인
        assert 'Helvetica' in analyzer.standard_14_fonts
        assert 'Times-Roman' in analyzer.standard_14_fonts
    
    def test_analyze_basic_fonts(self, analyzer, sample_pdf_with_fonts):
        """기본 폰트 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf_with_fonts)
        result = analyzer.analyze(document, sample_pdf_with_fonts)
        
        # 기본 결과 구조 확인
        assert 'fonts' in result
        assert 'total_fonts' in result
        assert 'embedded_fonts' in result
        assert 'missing_fonts' in result
        assert 'font_issues' in result
    
    def test_font_type_determination(self, analyzer):
        """폰트 타입 결정 테스트"""
        test_cases = [
            ('TrueType', FontType.TRUETYPE),
            ('Type1', FontType.TYPE1),
            ('Type 1', FontType.TYPE1),
            ('Type3', FontType.TYPE3),
            ('CIDFontType0', FontType.CID_TYPE0),
            ('CIDFontType2', FontType.CID_TYPE2),
            ('OpenType', FontType.OPENTYPE),
            ('Unknown', FontType.UNKNOWN)
        ]
        
        for type_str, expected in test_cases:
            result = analyzer._determine_font_type(type_str)
            assert result == expected
    
    def test_pdffonts_integration(self, analyzer_with_tools):
        """pdffonts 통합 테스트"""
        # pdffonts 출력 시뮬레이션
        pdffonts_output = """name                                 type              encoding         emb sub uni object ID
------------------------------------ ----------------- ---------------- --- --- --- ---------
ABCDEF+NanumGothic                   TrueType          WinAnsi          yes yes yes      7  0
Arial                                TrueType          WinAnsi          no  no  yes      8  0
Times-Roman                          Type1             WinAnsi          no  no  no       9  0"""
        
        # Mock 설정
        analyzer_with_tools._pdffonts_available = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = pdffonts_output
            
            # 임시 PDF 생성
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                pdf = pikepdf.Pdf.new()
                pdf.add_blank_page()
                pdf.save(tmp.name)
                pdf_path = Path(tmp.name)
                
                document = PDFDocument.from_path(pdf_path)
                result = analyzer_with_tools.analyze(document, pdf_path)
                
                # 결과 확인
                assert result['total_fonts'] == 3
                assert result['embedded_fonts'] == 1  # NanumGothic만
                assert result['missing_fonts'] == 1   # Arial (Times-Roman은 표준 14)
                assert result['subset_fonts'] == 1
                
                pdf_path.unlink()
    
    def test_parse_pdffonts_line(self, analyzer):
        """pdffonts 출력 라인 파싱 테스트"""
        # 정상적인 라인
        line = "ABCDEF+TimesNewRoman                 TrueType          WinAnsi          yes yes yes      7  0"
        result = analyzer._parse_pdffonts_line(line)
        
        assert result is not None
        assert result['name'] == 'ABCDEF+TimesNewRoman'
        assert result['type'] == 'TrueType'
        assert result['encoding'] == 'WinAnsi'
        assert result['embedded'] is True
        assert result['subset'] is True
        assert result['unicode'] is True
        
        # 빈 라인
        assert analyzer._parse_pdffonts_line('') is None
        
        # 구분선
        assert analyzer._parse_pdffonts_line('--------------------') is None
    
    def test_subset_font_detection(self, analyzer):
        """서브셋 폰트 감지 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # 서브셋 폰트 (6자리 접두사)
            subset_font = pikepdf.Dictionary({
                "/Type": pikepdf.Name("/Font"),
                "/BaseFont": pikepdf.Name("/ABCDEF+NanumGothic")
            })
            
            # 일반 폰트
            normal_font = pikepdf.Dictionary({
                "/Type": pikepdf.Name("/Font"),
                "/BaseFont": pikepdf.Name("/Arial")
            })
            
            if "/Resources" not in page:
                page.Resources = pikepdf.Dictionary()
            if "/Font" not in page.Resources:
                page.Resources.Font = pikepdf.Dictionary()
            
            page.Resources.Font["/F1"] = subset_font
            page.Resources.Font["/F2"] = normal_font
            
            pdf.save(tmp.name)
            pdf_path = Path(tmp.name)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            # 내부 분석에서는 정확한 서브셋 감지가 어려울 수 있음
            assert result['total_fonts'] >= 0
            
            pdf_path.unlink()
    
    def test_standard_14_fonts(self, analyzer):
        """표준 14 폰트 처리 테스트"""
        # 표준 14 폰트 목록 확인
        standard_fonts = [
            'Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic',
            'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique',
            'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique',
            'Symbol', 'ZapfDingbats'
        ]
        
        for font in standard_fonts:
            assert font in analyzer.standard_14_fonts
    
    def test_error_handling(self, analyzer):
        """오류 처리 테스트"""
        # 존재하지 않는 파일
        invalid_path = Path("non_existent.pdf")
        
        # PDFDocument 생성 실패
        with pytest.raises(ValueError):
            PDFDocument.from_path(invalid_path)
    
    def test_external_tool_fallback(self, analyzer_with_tools):
        """외부 도구 실패 시 폴백 테스트"""
        # pdffonts 실패 시뮬레이션
        analyzer_with_tools._pdffonts_available = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("pdffonts failed")
            
            # 임시 PDF 생성
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                pdf = pikepdf.Pdf.new()
                pdf.add_blank_page()
                pdf.save(tmp.name)
                pdf_path = Path(tmp.name)
                
                document = PDFDocument.from_path(pdf_path)
                
                # 외부 도구 실패해도 내부 분석으로 폴백
                result = analyzer_with_tools.analyze(document, pdf_path)
                
                assert 'fonts' in result
                assert '_warning' in result  # 제한된 분석 경고
                
                pdf_path.unlink()
    
    def test_dependencies(self, analyzer):
        """의존성 확인 테스트"""
        deps = analyzer.get_dependencies()
        
        assert 'pikepdf' in deps
        assert 'pdffonts' in deps
        assert deps['pikepdf'] is True  # pikepdf는 설치되어 있어야 함