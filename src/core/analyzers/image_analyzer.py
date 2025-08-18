# src/core/analyzers/image_analyzer.py
"""
PDF 이미지 분석기

PDF에 포함된 이미지의 해상도와 품질을 분석합니다.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import pikepdf
import fitz  # PyMuPDF

from .base_analyzer import BaseAnalyzer
from ..models import PDFDocument, ImageInfo, ColorSpace
from src.utils import calculate_dpi, points_to_mm


class ImageAnalyzer(BaseAnalyzer):
    """
    PDF 이미지 분석기
    
    PDF 파일의 이미지 정보를 분석합니다:
    - 이미지 개수 및 위치
    - 해상도 (DPI)
    - 색상 공간
    - 압축 방식
    - 크기 및 비율
    """
    
    def __init__(self):
        """이미지 분석기 초기화"""
        super().__init__("ImageAnalyzer")
        
        # 해상도 기준값
        self.DPI_CRITICAL = 72    # 웹용
        self.DPI_WARNING = 150    # 저품질 인쇄
        self.DPI_ACCEPTABLE = 200 # 일반 인쇄
        self.DPI_OPTIMAL = 300    # 고품질 인쇄
        
        # 이미지 필터(압축) 타입 매핑
        self.filter_names = {
            '/DCTDecode': 'JPEG',
            '/JPXDecode': 'JPEG2000',
            '/FlateDecode': 'ZIP',
            '/LZWDecode': 'LZW',
            '/RunLengthDecode': 'RLE',
            '/CCITTFaxDecode': 'CCITT',
            '/JBIG2Decode': 'JBIG2',
            '/ASCII85Decode': 'ASCII85',
            '/ASCIIHexDecode': 'ASCIIHex'
        }
    
    def analyze(self, document: PDFDocument, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF 이미지 정보 분석
        
        Args:
            document: PDF 문서 모델 객체
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: 이미지 분석 결과
        """
        # 이미지 정보 분석 중
        
        result = {
            'total_images': 0,
            'low_resolution_images': 0,
            'very_low_resolution_images': 0,
            'images': [],
            'resolution_distribution': {
                'critical': 0,     # < 72 DPI
                'warning': 0,      # 72-150 DPI
                'acceptable': 0,   # 150-300 DPI
                'optimal': 0       # >= 300 DPI
            },
            'color_space_distribution': {},
            'compression_distribution': {}
        }
        
        try:
            # PyMuPDF를 사용한 이미지 분석
            doc = fitz.open(str(pdf_path))
            
            for page_num, page in enumerate(doc, 1):
                page_images = self._analyze_page_images(page, page_num)
                result['images'].extend(page_images)
            
            doc.close()
            
            # 통계 계산
            result['total_images'] = len(result['images'])
            
            for img_info in result['images']:
                # 해상도 분류
                dpi = img_info.effective_dpi
                if dpi > 0:
                    if dpi < self.DPI_CRITICAL:
                        result['resolution_distribution']['critical'] += 1
                        result['very_low_resolution_images'] += 1
                        result['low_resolution_images'] += 1
                    elif dpi < self.DPI_WARNING:
                        result['resolution_distribution']['warning'] += 1
                        result['low_resolution_images'] += 1
                    elif dpi < self.DPI_OPTIMAL:
                        result['resolution_distribution']['acceptable'] += 1
                    else:
                        result['resolution_distribution']['optimal'] += 1
                
                # 색상 공간 통계
                cs = img_info.color_space.value
                result['color_space_distribution'][cs] = result['color_space_distribution'].get(cs, 0) + 1
                
                # 압축 방식 통계
                filter_name = img_info.filter
                result['compression_distribution'][filter_name] = result['compression_distribution'].get(filter_name, 0) + 1
            
            # 이미지 분석 완료
            if result['low_resolution_images'] > 0:
                # 저해상도 이미지 발견
                pass
            
        except Exception as e:
            # 이미지 분석 중 오류 발생
            raise
        
        return result
    
    def _analyze_page_images(self, page: fitz.Page, page_num: int) -> List[ImageInfo]:
        """
        단일 페이지의 이미지 분석
        
        Args:
            page: PyMuPDF Page 객체
            page_num: 페이지 번호
            
        Returns:
            List[ImageInfo]: 이미지 정보 목록
        """
        images = []
        
        # 페이지의 이미지 목록 가져오기
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            try:
                # 이미지 정보 추출
                xref = img[0]  # 이미지 참조 번호
                pix = fitz.Pixmap(page.parent, xref)  # 픽스맵으로 변환
                
                # 페이지에서의 이미지 위치와 크기 찾기
                img_rects = page.get_image_rects(xref)
                if img_rects:
                    rect = img_rects[0]  # 첫 번째 위치 사용
                    display_width_pt = rect.width
                    display_height_pt = rect.height
                    x_pt = rect.x0
                    y_pt = rect.y0
                else:
                    # 위치를 찾을 수 없는 경우 기본값
                    display_width_pt = float(pix.width)
                    display_height_pt = float(pix.height)
                    x_pt = 0.0
                    y_pt = 0.0
                
                # DPI 계산
                display_width_mm = points_to_mm(display_width_pt)
                display_height_mm = points_to_mm(display_height_pt)
                
                dpi_x = calculate_dpi(pix.width, display_width_mm) if display_width_mm > 0 else 0
                dpi_y = calculate_dpi(pix.height, display_height_mm) if display_height_mm > 0 else 0
                
                # 색상 공간 결정
                color_space = self._determine_color_space(pix.colorspace)
                
                # 압축 방식 확인 (이미지 딕셔너리에서)
                filter_type = self._get_image_filter(page.parent, xref)
                
                # ImageInfo 객체 생성
                img_info = ImageInfo(
                    page=page_num,
                    width=pix.width,
                    height=pix.height,
                    color_space=color_space,
                    bits_per_component=pix.n * 8 // (pix.width * pix.height) if pix.width * pix.height > 0 else 8,
                    filter=filter_type,
                    dpi_x=round(dpi_x, 1),
                    dpi_y=round(dpi_y, 1),
                    file_size=len(pix.pil_tobytes()),  # 대략적인 크기
                    has_transparency=pix.alpha,
                    is_compressed=filter_type != 'None',
                    x=round(points_to_mm(x_pt), 1),
                    y=round(points_to_mm(y_pt), 1),
                    display_width=round(display_width_mm, 1),
                    display_height=round(display_height_mm, 1)
                )
                
                images.append(img_info)
                
                # 메모리 해제
                pix = None
                
            except Exception as e:
                # 페이지 이미지 분석 실패
                continue
        
        return images
    
    def _determine_color_space(self, colorspace) -> ColorSpace:
        """
        PyMuPDF 색상 공간을 ColorSpace enum으로 변환
        
        Args:
            colorspace: PyMuPDF colorspace 객체
            
        Returns:
            ColorSpace: 색상 공간
        """
        if colorspace is None:
            return ColorSpace.GRAYSCALE
        
        cs_name = colorspace.name.upper()
        
        if 'RGB' in cs_name:
            return ColorSpace.RGB
        elif 'CMYK' in cs_name:
            return ColorSpace.CMYK
        elif 'GRAY' in cs_name:
            return ColorSpace.GRAYSCALE
        elif 'LAB' in cs_name:
            return ColorSpace.LAB
        elif 'INDEXED' in cs_name:
            return ColorSpace.INDEXED
        elif 'SEPARATION' in cs_name:
            return ColorSpace.SEPARATION
        elif 'DEVICEN' in cs_name:
            return ColorSpace.DEVICE_N
        elif 'PATTERN' in cs_name:
            return ColorSpace.PATTERN
        else:
            return ColorSpace.GRAYSCALE  # 기본값
    
    def _get_image_filter(self, doc: fitz.Document, xref: int) -> str:
        """
        이미지의 압축 필터 확인
        
        Args:
            doc: PyMuPDF Document 객체
            xref: 이미지 참조 번호
            
        Returns:
            str: 필터 이름
        """
        try:
            # pikepdf로 더 정확한 필터 정보 얻기
            with pikepdf.open(doc.name) as pdf:
                obj = pdf.get_object((xref, 0))
                if isinstance(obj, pikepdf.Stream):
                    # Stream 객체는 이미 딕셔너리 인터페이스를 가지고 있음
                    if '/Filter' in obj:
                        filter_obj = obj['/Filter']
                        if isinstance(filter_obj, pikepdf.Name):
                            filter_name = str(filter_obj)
                            return self.filter_names.get(filter_name, filter_name.lstrip('/'))
                        elif isinstance(filter_obj, pikepdf.Array) and len(filter_obj) > 0:
                            filter_name = str(filter_obj[0])
                            return self.filter_names.get(filter_name, filter_name.lstrip('/'))
        except Exception:
            pass
        
        return 'Unknown'
    
    def can_analyze(self, document: PDFDocument) -> bool:
        """
        이 분석기가 주어진 문서를 분석할 수 있는지 확인
        
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
            Dict[str, bool]: 의존성 상태
        """
        deps = {'pikepdf': False, 'PyMuPDF': False}
        
        try:
            import pikepdf
            deps['pikepdf'] = True
        except ImportError:
            pass
        
        try:
            import fitz
            deps['PyMuPDF'] = True
        except ImportError:
            pass
        
        return deps