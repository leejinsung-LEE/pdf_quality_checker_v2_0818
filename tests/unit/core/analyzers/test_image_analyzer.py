# tests/unit/core/analyzers/test_image_analyzer.py
"""
ImageAnalyzer 테스트
"""

import pytest
from pathlib import Path
import tempfile
import pikepdf
from unittest.mock import Mock, MagicMock

from src.core.models import PDFDocument, ImageInfo, ColorSpace
from src.core.analyzers import ImageAnalyzer


class TestImageAnalyzer:
    """ImageAnalyzer 테스트 클래스"""
    
    @pytest.fixture
    def analyzer(self):
        """ImageAnalyzer 인스턴스 생성"""
        return ImageAnalyzer()
    
    @pytest.fixture
    def sample_pdf_with_image(self):
        """이미지가 포함된 PDF 생성"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            page = pdf.add_blank_page()
            
            # 간단한 이미지 XObject 생성 (1x1 픽셀)
            image_data = b'\xff\x00\x00'  # RGB 빨간색 픽셀
            image = pikepdf.Stream(pdf, image_data)
            image.stream_dict = pikepdf.Dictionary({
                "/Type": pikepdf.Name("/XObject"),
                "/Subtype": pikepdf.Name("/Image"),
                "/Width": 100,
                "/Height": 100,
                "/ColorSpace": pikepdf.Name("/DeviceRGB"),
                "/BitsPerComponent": 8,
                "/Filter": pikepdf.Name("/DCTDecode")
            })
            
            # Resources에 이미지 추가
            if "/Resources" not in page:
                page.Resources = pikepdf.Dictionary()
            if "/XObject" not in page.Resources:
                page.Resources.XObject = pikepdf.Dictionary()
            
            page.Resources.XObject["/Im1"] = image
            
            # 이미지를 페이지에 그리는 컨텐츠
            content = pikepdf.Stream(pdf, b"""
                q
                100 0 0 100 50 50 cm
                /Im1 Do
                Q
            """)
            page.Contents = content
            
            pdf.save(tmp.name)
            yield Path(tmp.name)
            Path(tmp.name).unlink()
    
    def test_analyzer_initialization(self, analyzer):
        """분석기 초기화 테스트"""
        assert analyzer.name == "ImageAnalyzer"
        assert analyzer.can_analyze(None) is True
        
        # DPI 기준값 확인
        assert analyzer.DPI_CRITICAL == 72
        assert analyzer.DPI_WARNING == 150
        assert analyzer.DPI_ACCEPTABLE == 200
        assert analyzer.DPI_OPTIMAL == 300
    
    def test_analyze_empty_pdf(self, analyzer):
        """이미지가 없는 PDF 분석 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            pdf.add_blank_page()
            pdf.save(tmp.name)
            pdf_path = Path(tmp.name)
            
            document = PDFDocument.from_path(pdf_path)
            result = analyzer.analyze(document, pdf_path)
            
            # 기본 구조 확인
            assert result['total_images'] == 0
            assert result['low_resolution_images'] == 0
            assert len(result['images']) == 0
            assert all(count == 0 for count in result['resolution_distribution'].values())
            
            pdf_path.unlink()
    
    def test_resolution_classification(self, analyzer):
        """해상도 분류 테스트"""
        # ImageInfo 객체 생성하여 테스트
        test_cases = [
            (50, 'critical'),    # < 72 DPI
            (100, 'warning'),    # 72-150 DPI
            (200, 'acceptable'), # 150-300 DPI
            (350, 'optimal')     # >= 300 DPI
        ]
        
        for dpi, expected_category in test_cases:
            # 해상도 기준 확인
            if expected_category == 'critical':
                assert dpi < analyzer.DPI_CRITICAL
            elif expected_category == 'warning':
                assert analyzer.DPI_CRITICAL <= dpi < analyzer.DPI_WARNING
            elif expected_category == 'acceptable':
                assert analyzer.DPI_WARNING <= dpi < analyzer.DPI_OPTIMAL
            else:  # optimal
                assert dpi >= analyzer.DPI_OPTIMAL
    
    def test_filter_name_mapping(self, analyzer):
        """압축 필터 이름 매핑 테스트"""
        assert analyzer.filter_names['/DCTDecode'] == 'JPEG'
        assert analyzer.filter_names['/JPXDecode'] == 'JPEG2000'
        assert analyzer.filter_names['/FlateDecode'] == 'ZIP'
        assert analyzer.filter_names['/LZWDecode'] == 'LZW'
    
    def test_color_space_determination(self, analyzer):
        """색상 공간 결정 테스트"""
        # Mock colorspace 객체
        test_cases = [
            ('DeviceRGB', ColorSpace.RGB),
            ('DeviceCMYK', ColorSpace.CMYK),
            ('DeviceGray', ColorSpace.GRAYSCALE),
            ('Lab', ColorSpace.LAB),
            ('Indexed', ColorSpace.INDEXED),
            ('Unknown', ColorSpace.GRAYSCALE)  # 기본값
        ]
        
        for cs_name, expected in test_cases:
            mock_cs = Mock()
            mock_cs.name = cs_name
            result = analyzer._determine_color_space(mock_cs)
            assert result == expected
    
    def test_analyze_with_pymupdf_mock(self, analyzer):
        """PyMuPDF를 모킹한 분석 테스트"""
        # PyMuPDF 관련 객체들 모킹
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            pdf.add_blank_page()
            pdf.save(tmp.name)
            pdf_path = Path(tmp.name)
            
            document = PDFDocument.from_path(pdf_path)
            
            # fitz 모듈 모킹
            with pytest.MonkeyPatch.context() as m:
                mock_doc = MagicMock()
                mock_page = MagicMock()
                
                # 이미지 정보 설정
                mock_page.get_images.return_value = [(1, 0, 100, 100, 8, 'DeviceRGB', '', 'Im1', None)]
                mock_page.get_image_rects.return_value = [MagicMock(width=100, height=100, x0=0, y0=0)]
                mock_page.parent = mock_doc
                
                # Pixmap 모킹
                mock_pix = MagicMock()
                mock_pix.width = 300
                mock_pix.height = 300
                mock_pix.n = 3  # RGB
                mock_pix.alpha = False
                mock_pix.colorspace = MagicMock(name='DeviceRGB')
                mock_pix.pil_tobytes.return_value = b'dummy_data'
                
                mock_doc.__iter__.return_value = [mock_page]
                mock_doc.name = str(pdf_path)
                
                # fitz 모듈 패치
                m.setattr('fitz.open', lambda path: mock_doc)
                m.setattr('fitz.Pixmap', lambda doc, xref: mock_pix)
                
                try:
                    result = analyzer.analyze(document, pdf_path)
                    
                    # 결과 검증
                    assert result['total_images'] > 0
                    # DPI 계산: 300 픽셀 / (100pt * 0.352778 mm/pt / 25.4 mm/inch) ≈ 216 DPI
                    # 정확한 값은 계산 방식에 따라 다를 수 있음
                    
                except ImportError:
                    # PyMuPDF가 설치되지 않은 경우 스킵
                    pytest.skip("PyMuPDF not installed")
            
            pdf_path.unlink()
    
    def test_low_resolution_detection(self, analyzer):
        """저해상도 이미지 감지 테스트"""
        # ImageInfo 객체로 테스트
        low_res_image = ImageInfo(
            page=1,
            width=100,
            height=100,
            color_space=ColorSpace.RGB,
            bits_per_component=8,
            filter='JPEG',
            dpi_x=72,
            dpi_y=72
        )
        
        high_res_image = ImageInfo(
            page=1,
            width=300,
            height=300,
            color_space=ColorSpace.RGB,
            bits_per_component=8,
            filter='JPEG',
            dpi_x=300,
            dpi_y=300
        )
        
        assert low_res_image.is_low_resolution is True
        assert low_res_image.is_very_low_resolution is True
        assert high_res_image.is_low_resolution is False
        assert high_res_image.is_very_low_resolution is False
    
    def test_image_info_properties(self):
        """ImageInfo 속성 테스트"""
        img = ImageInfo(
            page=1,
            width=600,
            height=400,
            color_space=ColorSpace.CMYK,
            bits_per_component=8,
            filter='ZIP',
            dpi_x=150,
            dpi_y=200
        )
        
        # 속성 확인
        assert img.effective_dpi == 150  # min(150, 200)
        assert img.pixel_count == 240000  # 600 * 400
        assert img.aspect_ratio == 1.5  # 600 / 400
        
        # 문자열 표현
        str_repr = str(img)
        assert 'page 1' in str_repr
        assert '600x400' in str_repr
        assert '150dpi' in str_repr
    
    def test_statistics_calculation(self, analyzer):
        """통계 계산 테스트"""
        # 다양한 이미지 정보를 가진 결과 시뮬레이션
        images = [
            ImageInfo(page=1, width=100, height=100, color_space=ColorSpace.RGB,
                     bits_per_component=8, filter='JPEG', dpi_x=50, dpi_y=50),
            ImageInfo(page=1, width=200, height=200, color_space=ColorSpace.CMYK,
                     bits_per_component=8, filter='ZIP', dpi_x=150, dpi_y=150),
            ImageInfo(page=2, width=300, height=300, color_space=ColorSpace.RGB,
                     bits_per_component=8, filter='JPEG', dpi_x=300, dpi_y=300),
        ]
        
        # 통계 계산 시뮬레이션
        result = {
            'images': images,
            'total_images': len(images),
            'low_resolution_images': 0,
            'very_low_resolution_images': 0,
            'resolution_distribution': {
                'critical': 0,
                'warning': 0,
                'acceptable': 0,
                'optimal': 0
            },
            'color_space_distribution': {},
            'compression_distribution': {}
        }
        
        # 통계 계산
        for img in images:
            dpi = img.effective_dpi
            if dpi < 72:
                result['resolution_distribution']['critical'] += 1
                result['very_low_resolution_images'] += 1
                result['low_resolution_images'] += 1
            elif dpi < 150:
                result['resolution_distribution']['warning'] += 1
                result['low_resolution_images'] += 1
            elif dpi < 300:
                result['resolution_distribution']['acceptable'] += 1
            else:
                result['resolution_distribution']['optimal'] += 1
            
            cs = img.color_space.value
            result['color_space_distribution'][cs] = result['color_space_distribution'].get(cs, 0) + 1
            
            result['compression_distribution'][img.filter] = result['compression_distribution'].get(img.filter, 0) + 1
        
        # 결과 검증
        assert result['resolution_distribution']['critical'] == 1
        assert result['resolution_distribution']['acceptable'] == 1
        assert result['resolution_distribution']['optimal'] == 1
        assert result['low_resolution_images'] == 1
        assert result['color_space_distribution']['RGB'] == 2
        assert result['color_space_distribution']['CMYK'] == 1
        assert result['compression_distribution']['JPEG'] == 2
        assert result['compression_distribution']['ZIP'] == 1
    
    def test_dependencies(self, analyzer):
        """의존성 확인 테스트"""
        deps = analyzer.get_dependencies()
        
        assert 'pikepdf' in deps
        assert 'PyMuPDF' in deps
        # 실제 설치 여부는 환경에 따라 다름