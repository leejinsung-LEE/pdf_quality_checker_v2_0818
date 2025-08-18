# src/core/analyzers/page_analyzer.py
"""
PDF 페이지 분석기

각 페이지의 크기, 방향, 재단선 등을 분석합니다.
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import pikepdf
from collections import Counter

from .base_analyzer import BaseAnalyzer
from ..models import PDFDocument, PageInfo, PageSize, Rectangle, BleedInfo


class PageAnalyzer(BaseAnalyzer):
    """
    PDF 페이지 분석기
    
    각 페이지의 다음 정보를 분석합니다:
    - 페이지 크기 및 방향
    - 회전 정보
    - 재단선(Bleed) 정보
    - 컨텐츠 영역
    - 페이지 크기 일관성
    """
    
    def __init__(self):
        """페이지 분석기 초기화"""
        super().__init__("PageAnalyzer")
    
    def analyze(self, document: PDFDocument, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF 페이지 정보 분석
        
        Args:
            document: PDF 문서 모델 객체
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: 페이지 분석 결과
        """
        # 페이지 정보 분석 중
        
        result = {
            'pages': [],
            'page_sizes': {},
            'has_mixed_sizes': False,
            'has_mixed_orientations': False,
            'dominant_size': None,
            'total_pages': 0
        }
        
        try:
            # pikepdf로 PDF 열기
            with pikepdf.open(pdf_path) as pdf:
                pages_info = []
                size_counter = Counter()
                orientations = set()
                
                # 각 페이지 분석
                for page_num, page in enumerate(pdf.pages, 1):
                    page_info = self._analyze_single_page(page, page_num)
                    pages_info.append(page_info)
                    
                    # PageInfo 객체 생성하여 문서에 추가
                    page_obj = PageInfo(
                        page_number=page_num,
                        width_mm=page_info['width_mm'],
                        height_mm=page_info['height_mm'],
                        rotation=page_info['rotation'],
                        bleed_info=self._create_bleed_info(page_info.get('bleed'))
                    )
                    document.add_page_info(page_obj)
                    
                    # 통계 수집
                    size_key = f"{page_info['width_mm']:.0f}x{page_info['height_mm']:.0f}mm"
                    size_counter[size_key] += 1
                    orientations.add(page_info['orientation'])
                
                # 결과 정리
                result['pages'] = pages_info
                result['total_pages'] = len(pages_info)
                result['page_sizes'] = dict(size_counter)
                result['has_mixed_sizes'] = len(size_counter) > 1
                result['has_mixed_orientations'] = len(orientations) > 1
                
                # 가장 많이 사용된 크기
                if size_counter:
                    dominant_size = size_counter.most_common(1)[0]
                    result['dominant_size'] = {
                        'size': dominant_size[0],
                        'count': dominant_size[1],
                        'percentage': (dominant_size[1] / len(pages_info)) * 100
                    }
                
                # 페이지 분석 완료
                pass
                
        except Exception as e:
            # 페이지 분석 중 오류 발생
            raise
        
        return result
    
    def _analyze_single_page(self, page: pikepdf.Page, page_num: int) -> Dict[str, Any]:
        """
        단일 페이지 분석
        
        Args:
            page: pikepdf Page 객체
            page_num: 페이지 번호
            
        Returns:
            Dict[str, Any]: 페이지 정보
        """
        # MediaBox 가져오기 (전체 페이지 크기)
        mediabox = page.mediabox
        media_width = float(mediabox[2] - mediabox[0])
        media_height = float(mediabox[3] - mediabox[1])
        
        # 회전 정보
        rotation = int(page.get('/Rotate', 0))
        
        # 회전을 고려한 실제 크기 계산
        if rotation in (90, 270):
            width_pt = media_height
            height_pt = media_width
        else:
            width_pt = media_width
            height_pt = media_height
        
        # 포인트를 밀리미터로 변환 (1pt = 0.352778mm)
        width_mm = width_pt * 0.352778
        height_mm = height_pt * 0.352778
        
        # 페이지 정보 구성
        page_info = {
            'page_number': page_num,
            'width_pt': width_pt,
            'height_pt': height_pt,
            'width_mm': round(width_mm, 1),
            'height_mm': round(height_mm, 1),
            'rotation': rotation,
            'orientation': 'portrait' if height_mm > width_mm else 'landscape',
            'paper_size': self._detect_paper_size(width_mm, height_mm)
        }
        
        # 재단선 정보 분석
        bleed_info = self._analyze_bleed(page, mediabox)
        if bleed_info:
            page_info['bleed'] = bleed_info
        
        # CropBox 정보 (있는 경우)
        if '/CropBox' in page:
            cropbox = page.cropbox
            page_info['has_cropbox'] = True
            page_info['cropbox'] = {
                'x': float(cropbox[0]),
                'y': float(cropbox[1]),
                'width': float(cropbox[2] - cropbox[0]),
                'height': float(cropbox[3] - cropbox[1])
            }
        
        # TrimBox 정보 (최종 재단 크기)
        if '/TrimBox' in page:
            trimbox = page.trimbox
            page_info['has_trimbox'] = True
            page_info['trimbox'] = {
                'x': float(trimbox[0]),
                'y': float(trimbox[1]),
                'width': float(trimbox[2] - trimbox[0]),
                'height': float(trimbox[3] - trimbox[1])
            }
        
        return page_info
    
    def _detect_paper_size(self, width_mm: float, height_mm: float) -> str:
        """
        용지 크기 감지
        
        Args:
            width_mm: 너비 (mm)
            height_mm: 높이 (mm)
            
        Returns:
            str: 용지 크기 이름
        """
        # 표준 용지 크기 정의 (너비x높이 mm, 2mm 허용 오차)
        paper_sizes = {
            'A0': (841, 1189),
            'A1': (594, 841),
            'A2': (420, 594),
            'A3': (297, 420),
            'A4': (210, 297),
            'A5': (148, 210),
            'A6': (105, 148),
            'Letter': (216, 279),
            'Legal': (216, 356),
            'Tabloid': (279, 432),
            'B4': (250, 353),
            'B5': (176, 250)
        }
        
        tolerance = 2.0  # mm
        
        # 가로/세로 모두 확인
        for name, (std_width, std_height) in paper_sizes.items():
            # 정방향 확인
            if (abs(width_mm - std_width) <= tolerance and 
                abs(height_mm - std_height) <= tolerance):
                return name
            # 회전된 방향 확인
            if (abs(width_mm - std_height) <= tolerance and 
                abs(height_mm - std_width) <= tolerance):
                return f"{name} (Landscape)"
        
        return "Custom"
    
    def _analyze_bleed(self, page: pikepdf.Page, mediabox: pikepdf.Array) -> Optional[Dict[str, float]]:
        """
        재단선(Bleed) 정보 분석
        
        Args:
            page: pikepdf Page 객체
            mediabox: MediaBox 배열
            
        Returns:
            Dict[str, float]: 재단선 정보 (mm) 또는 None
        """
        # BleedBox가 있는 경우
        if '/BleedBox' in page:
            bleedbox = page.bleedbox
            
            # 각 방향의 재단선 계산 (포인트)
            bleed_left = float(mediabox[0] - bleedbox[0])
            bleed_bottom = float(mediabox[1] - bleedbox[1])
            bleed_right = float(bleedbox[2] - mediabox[2])
            bleed_top = float(bleedbox[3] - mediabox[3])
            
            # mm로 변환
            pt_to_mm = 0.352778
            return {
                'left': round(bleed_left * pt_to_mm, 1),
                'bottom': round(bleed_bottom * pt_to_mm, 1),
                'right': round(bleed_right * pt_to_mm, 1),
                'top': round(bleed_top * pt_to_mm, 1)
            }
        
        # TrimBox가 있는 경우 MediaBox와의 차이로 계산
        elif '/TrimBox' in page:
            trimbox = page.trimbox
            
            bleed_left = float(trimbox[0] - mediabox[0])
            bleed_bottom = float(trimbox[1] - mediabox[1])
            bleed_right = float(mediabox[2] - trimbox[2])
            bleed_top = float(mediabox[3] - trimbox[3])
            
            # 모든 값이 0 이상인 경우만 재단선으로 인정
            if all(b >= 0 for b in [bleed_left, bleed_bottom, bleed_right, bleed_top]):
                pt_to_mm = 0.352778
                return {
                    'left': round(bleed_left * pt_to_mm, 1),
                    'bottom': round(bleed_bottom * pt_to_mm, 1),
                    'right': round(bleed_right * pt_to_mm, 1),
                    'top': round(bleed_top * pt_to_mm, 1)
                }
        
        return None
    
    def _create_bleed_info(self, bleed_dict: Optional[Dict[str, float]]) -> Optional[BleedInfo]:
        """
        BleedInfo 객체 생성
        
        Args:
            bleed_dict: 재단선 정보 딕셔너리
            
        Returns:
            BleedInfo: 재단선 정보 객체 또는 None
        """
        if not bleed_dict:
            return None
        
        return BleedInfo(
            top=bleed_dict.get('top', 0.0),
            bottom=bleed_dict.get('bottom', 0.0),
            left=bleed_dict.get('left', 0.0),
            right=bleed_dict.get('right', 0.0)
        )
    
    def can_analyze(self, document: PDFDocument) -> bool:
        """
        이 분석기가 주어진 문서를 분석할 수 있는지 확인
        
        페이지 분석은 모든 PDF에 대해 가능합니다.
        
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