# src/core/analyzers/color_analyzer.py
"""
PDF 색상 분석기

PDF에 사용된 색상 공간과 별색 정보를 분석합니다.
"""

from typing import Dict, Any, Set, List
from pathlib import Path
import pikepdf
import re

from .base_analyzer import BaseAnalyzer
from ..models import PDFDocument, ColorInfo, ColorSpace


class ColorAnalyzer(BaseAnalyzer):
    """
    PDF 색상 분석기
    
    PDF 파일의 색상 정보를 분석합니다:
    - 사용된 색상 공간 (RGB, CMYK, Grayscale 등)
    - 별색(Spot Color) 사용 여부
    - 투명도 사용 여부
    - 오버프린트 설정
    """
    
    def __init__(self):
        """색상 분석기 초기화"""
        super().__init__("ColorAnalyzer")
        
        # 색상 공간 패턴
        self.color_space_patterns = {
            'RGB': ['/DeviceRGB', '/CalRGB'],
            'CMYK': ['/DeviceCMYK', '/CalCMYK'],
            'Grayscale': ['/DeviceGray', '/CalGray'],
            'Lab': ['/Lab'],
            'Indexed': ['/Indexed'],
            'Pattern': ['/Pattern'],
            'Separation': ['/Separation'],
            'DeviceN': ['/DeviceN']
        }
    
    def analyze(self, document: PDFDocument, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF 색상 정보 분석
        
        Args:
            document: PDF 문서 모델 객체
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: 색상 분석 결과
        """
        # 색상 정보 분석 중
        
        result = {
            'color_spaces': set(),
            'spot_colors': [],
            'has_transparency': False,
            'has_overprint': False,
            'rgb_usage': 0,
            'cmyk_usage': 0,
            'page_color_info': []
        }
        
        try:
            with pikepdf.open(pdf_path) as pdf:
                # 각 페이지의 색상 정보 분석
                for page_num, page in enumerate(pdf.pages, 1):
                    page_info = self._analyze_page_colors(page, page_num)
                    result['page_color_info'].append(page_info)
                    
                    # 전체 문서 통계 업데이트
                    result['color_spaces'].update(page_info['color_spaces'])
                    result['spot_colors'].extend(page_info['spot_colors'])
                    result['has_transparency'] |= page_info['has_transparency']
                    result['has_overprint'] |= page_info['has_overprint']
                    
                    if 'RGB' in page_info['color_spaces']:
                        result['rgb_usage'] += 1
                    if 'CMYK' in page_info['color_spaces']:
                        result['cmyk_usage'] += 1
                
                # 중복 제거
                result['spot_colors'] = list(set(result['spot_colors']))
                
                # ColorInfo 객체 생성
                color_info = self._create_color_info(result, document.page_count)
                result['color_info'] = color_info
                
                # 색상 공간 분석 완료
                # Color spaces: {', '.join(result['color_spaces'])}
                if result['spot_colors']:
                    # Found {len(result['spot_colors'])} spot colors
                    pass
                
        except Exception as e:
            # 색상 분석 실패: {e}
            raise
        
        return result
    
    def _analyze_page_colors(self, page: pikepdf.Page, page_num: int) -> Dict[str, Any]:
        """
        단일 페이지의 색상 정보 분석
        
        Args:
            page: pikepdf Page 객체
            page_num: 페이지 번호
            
        Returns:
            Dict[str, Any]: 페이지 색상 정보
        """
        page_info = {
            'page_number': page_num,
            'color_spaces': set(),
            'spot_colors': [],
            'has_transparency': False,
            'has_overprint': False
        }
        
        # Resources 분석
        if '/Resources' in page:
            resources = page.Resources
            
            # ColorSpace 리소스 확인
            if '/ColorSpace' in resources:
                self._analyze_color_spaces(resources.ColorSpace, page_info)
            
            # ExtGState (투명도, 오버프린트 등) 확인
            if '/ExtGState' in resources:
                self._analyze_graphics_state(resources.ExtGState, page_info)
            
            # Pattern 확인
            if '/Pattern' in resources:
                page_info['color_spaces'].add('Pattern')
            
            # XObject (이미지, 폼) 분석
            if '/XObject' in resources:
                self._analyze_xobjects(resources.XObject, page_info)
        
        # 페이지 스트림 분석 (색상 연산자 찾기)
        try:
            content = page.get_filtered_stream()
            if content:
                self._analyze_content_stream(content, page_info)
        except Exception:
            # 스트림 분석 실패는 무시
            pass
        
        return page_info
    
    def _analyze_color_spaces(self, color_spaces: pikepdf.Dictionary, page_info: Dict[str, Any]):
        """
        ColorSpace 딕셔너리 분석
        
        Args:
            color_spaces: ColorSpace 딕셔너리
            page_info: 페이지 정보 딕셔너리
        """
        for name, cs_obj in color_spaces.items():
            if isinstance(cs_obj, pikepdf.Array):
                cs_type = str(cs_obj[0])
                
                # 색상 공간 타입 확인
                for space_name, patterns in self.color_space_patterns.items():
                    if any(pattern in cs_type for pattern in patterns):
                        page_info['color_spaces'].add(space_name)
                        break
                
                # Separation (별색) 처리
                if '/Separation' in cs_type and len(cs_obj) > 1:
                    spot_name = str(cs_obj[1])
                    if spot_name and not spot_name.startswith('/'):
                        page_info['spot_colors'].append(spot_name)
                
                # DeviceN 처리
                elif '/DeviceN' in cs_type and len(cs_obj) > 1:
                    if isinstance(cs_obj[1], pikepdf.Array):
                        for color_name in cs_obj[1]:
                            spot_name = str(color_name)
                            if spot_name and not spot_name.startswith('/'):
                                page_info['spot_colors'].append(spot_name)
            
            elif isinstance(cs_obj, pikepdf.Name):
                # 직접 색상 공간 참조
                cs_name = str(cs_obj)
                for space_name, patterns in self.color_space_patterns.items():
                    if any(pattern in cs_name for pattern in patterns):
                        page_info['color_spaces'].add(space_name)
                        break
    
    def _analyze_graphics_state(self, ext_gstates: pikepdf.Dictionary, page_info: Dict[str, Any]):
        """
        ExtGState 딕셔너리 분석 (투명도, 오버프린트 등)
        
        Args:
            ext_gstates: ExtGState 딕셔너리
            page_info: 페이지 정보 딕셔너리
        """
        for name, gs_obj in ext_gstates.items():
            if isinstance(gs_obj, pikepdf.Dictionary):
                # 투명도 확인
                if '/CA' in gs_obj or '/ca' in gs_obj:  # 선/채우기 투명도
                    alpha_stroke = float(gs_obj.get('/CA', 1.0))
                    alpha_fill = float(gs_obj.get('/ca', 1.0))
                    if alpha_stroke < 1.0 or alpha_fill < 1.0:
                        page_info['has_transparency'] = True
                
                # 블렌드 모드 확인
                if '/BM' in gs_obj:
                    blend_mode = str(gs_obj['/BM'])
                    if blend_mode != '/Normal':
                        page_info['has_transparency'] = True
                
                # 오버프린트 확인
                if '/OP' in gs_obj or '/op' in gs_obj:
                    overprint_stroke = gs_obj.get('/OP', False)
                    overprint_fill = gs_obj.get('/op', False)
                    if overprint_stroke or overprint_fill:
                        page_info['has_overprint'] = True
    
    def _analyze_xobjects(self, xobjects: pikepdf.Dictionary, page_info: Dict[str, Any]):
        """
        XObject 분석 (이미지, 폼 등)
        
        Args:
            xobjects: XObject 딕셔너리
            page_info: 페이지 정보 딕셔너리
        """
        for name, xobj in xobjects.items():
            if isinstance(xobj, pikepdf.Stream):
                # Stream 객체는 이미 딕셔너리 인터페이스를 가지고 있음
                
                # 이미지 XObject
                if xobj.get('/Subtype') == '/Image':
                    # 색상 공간 확인
                    if '/ColorSpace' in xobj:
                        cs = str(xobj['/ColorSpace'])
                        for space_name, patterns in self.color_space_patterns.items():
                            if any(pattern in cs for pattern in patterns):
                                page_info['color_spaces'].add(space_name)
                                break
                
                # Form XObject (재귀적 분석 필요)
                elif xobj.get('/Subtype') == '/Form':
                    # Form XObject도 Resources를 가질 수 있음
                    if '/Resources' in xobj:
                        # 간단히 색상 공간만 확인
                        if '/ColorSpace' in xobj.Resources:
                            self._analyze_color_spaces(xobj.Resources.ColorSpace, page_info)
    
    def _analyze_content_stream(self, content: bytes, page_info: Dict[str, Any]):
        """
        페이지 컨텐츠 스트림 분석 (색상 연산자 찾기)
        
        Args:
            content: 페이지 컨텐츠 스트림
            page_info: 페이지 정보 딕셔너리
        """
        try:
            content_str = content.decode('latin-1', errors='ignore')
            
            # RGB 색상 연산자
            if ' rg' in content_str or ' RG' in content_str:
                page_info['color_spaces'].add('RGB')
            
            # CMYK 색상 연산자
            if ' k' in content_str or ' K' in content_str:
                page_info['color_spaces'].add('CMYK')
            
            # 그레이스케일 연산자
            if ' g' in content_str or ' G' in content_str:
                page_info['color_spaces'].add('Grayscale')
            
            # 색상 공간 설정 연산자
            cs_pattern = re.compile(r'/(\w+)\s+cs|/(\w+)\s+CS')
            for match in cs_pattern.finditer(content_str):
                cs_name = match.group(1) or match.group(2)
                # 기본 색상 공간 확인
                if 'RGB' in cs_name:
                    page_info['color_spaces'].add('RGB')
                elif 'CMYK' in cs_name:
                    page_info['color_spaces'].add('CMYK')
                elif 'Gray' in cs_name:
                    page_info['color_spaces'].add('Grayscale')
                
        except Exception:
            # 스트림 파싱 오류는 무시
            pass
    
    def _create_color_info(self, analysis_result: Dict[str, Any], total_pages: int) -> ColorInfo:
        """
        ColorInfo 객체 생성
        
        Args:
            analysis_result: 분석 결과
            total_pages: 전체 페이지 수
            
        Returns:
            ColorInfo: 색상 정보 객체
        """
        # ColorSpace enum으로 변환
        color_spaces = set()
        for cs_name in analysis_result['color_spaces']:
            try:
                color_spaces.add(ColorSpace[cs_name.upper()])
            except KeyError:
                # 알 수 없는 색상 공간은 무시
                pass
        
        # 주요 색상 공간 결정
        dominant_space = None
        if ColorSpace.CMYK in color_spaces:
            dominant_space = ColorSpace.CMYK
        elif ColorSpace.RGB in color_spaces:
            dominant_space = ColorSpace.RGB
        elif ColorSpace.GRAYSCALE in color_spaces:
            dominant_space = ColorSpace.GRAYSCALE
        
        color_info = ColorInfo(
            color_spaces_used=color_spaces,
            spot_colors=analysis_result['spot_colors'],
            has_transparency=analysis_result['has_transparency'],
            has_overprint=analysis_result['has_overprint'],
            dominant_color_space=dominant_space,
            rgb_object_count=analysis_result['rgb_usage'],
            cmyk_object_count=analysis_result['cmyk_usage'],
            spot_color_count=len(analysis_result['spot_colors'])
        )
        
        return color_info
    
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
        try:
            import pikepdf
            return {'pikepdf': True}
        except ImportError:
            return {'pikepdf': False}