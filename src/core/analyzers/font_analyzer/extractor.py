# -*- coding: utf-8 -*-
"""
폰트 추출 모듈

PDF에서 폰트 정보를 추출합니다.
"""

import re
from typing import Dict, Set, Optional, List, Any
from pathlib import Path
import logging
import pikepdf

from .models import FontPageMapping


class FontExtractor:
    """폰트 추출기"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
    def extract_fonts_from_pdf(self, pdf_path: Path) -> FontPageMapping:
        """
        PDF에서 폰트 정보 추출
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            FontPageMapping: 폰트-페이지 매핑 정보
        """
        font_to_pages = {}
        page_to_fonts = {}
        
        try:
            with pikepdf.open(pdf_path) as pdf:
                fonts_by_page = self._extract_fonts_pikepdf(pdf)
                
                # 매핑 정보 구성
                for page_num, page_fonts in fonts_by_page.items():
                    page_to_fonts[page_num] = page_fonts
                    
                    for font_name in page_fonts:
                        if font_name not in font_to_pages:
                            font_to_pages[font_name] = []
                        font_to_pages[font_name].append(page_num)
                        
        except Exception as e:
            self.logger.error(f"폰트 추출 실패: {e}")
            
        return FontPageMapping(
            font_to_pages=font_to_pages,
            page_to_fonts=page_to_fonts
        )
        
    def _extract_fonts_pikepdf(self, pdf: pikepdf.Pdf) -> Dict[int, Set[str]]:
        """
        pikepdf를 사용한 폰트 추출
        
        Args:
            pdf: pikepdf PDF 객체
            
        Returns:
            Dict[int, Set[str]]: 페이지별 폰트 이름 집합
        """
        fonts_by_page = {}
        
        for page_num, page in enumerate(pdf.pages, 1):
            page_fonts = set()
            
            # Resources에서 Font 추출
            try:
                if '/Resources' in page and '/Font' in page.Resources:
                    for font_name, font_obj in page.Resources.Font.items():
                        if isinstance(font_obj, pikepdf.Dictionary):
                            # 실제 폰트 이름 추출
                            actual_name = self._get_font_name(font_obj)
                            if actual_name:
                                page_fonts.add(actual_name)
                                self.logger.debug(f"페이지 {page_num}: 폰트 {actual_name} 발견")
            except Exception as e:
                self.logger.warning(f"페이지 {page_num} 폰트 추출 오류: {e}")
                
            if page_fonts:
                fonts_by_page[page_num] = page_fonts
                
        return fonts_by_page
        
    def _get_font_name(self, font_obj: pikepdf.Dictionary) -> Optional[str]:
        """
        폰트 객체에서 실제 폰트 이름 추출
        
        Args:
            font_obj: pikepdf 폰트 딕셔너리
            
        Returns:
            str: 폰트 이름 또는 None
        """
        try:
            # BaseFont 확인
            if '/BaseFont' in font_obj:
                return str(font_obj['/BaseFont']).lstrip('/')
                
            # DescendantFonts 확인 (Type0 폰트)
            if '/DescendantFonts' in font_obj:
                descendants = font_obj['/DescendantFonts']
                if isinstance(descendants, pikepdf.Array) and len(descendants) > 0:
                    desc_font = descendants[0]
                    if isinstance(desc_font, pikepdf.Dictionary) and '/BaseFont' in desc_font:
                        return str(desc_font['/BaseFont']).lstrip('/')
                        
            # FontName 확인 (대체)
            if '/FontName' in font_obj:
                return str(font_obj['/FontName']).lstrip('/')
                
        except Exception as e:
            self.logger.debug(f"폰트 이름 추출 오류: {e}")
            
        return None
        
    def extract_font_properties(self, font_obj: pikepdf.Dictionary) -> Dict[str, Any]:
        """
        폰트 객체에서 속성 추출
        
        Args:
            font_obj: pikepdf 폰트 딕셔너리
            
        Returns:
            Dict[str, Any]: 폰트 속성
        """
        properties = {}
        
        try:
            # 기본 속성
            if '/Subtype' in font_obj:
                properties['subtype'] = str(font_obj['/Subtype']).lstrip('/')
                
            if '/Encoding' in font_obj:
                encoding = font_obj['/Encoding']
                if isinstance(encoding, pikepdf.Name):
                    properties['encoding'] = str(encoding).lstrip('/')
                elif isinstance(encoding, pikepdf.Dictionary):
                    if '/BaseEncoding' in encoding:
                        properties['encoding'] = str(encoding['/BaseEncoding']).lstrip('/')
                        
            # FontDescriptor 확인
            if '/FontDescriptor' in font_obj:
                descriptor = font_obj['/FontDescriptor']
                if isinstance(descriptor, pikepdf.Dictionary):
                    properties.update(self._extract_descriptor_info(descriptor))
                    
            # ToUnicode 맵 존재 여부
            if '/ToUnicode' in font_obj:
                properties['has_unicode_map'] = True
            else:
                properties['has_unicode_map'] = False
                
        except Exception as e:
            self.logger.debug(f"폰트 속성 추출 오류: {e}")
            
        return properties
        
    def _extract_descriptor_info(self, descriptor: pikepdf.Dictionary) -> Dict[str, Any]:
        """
        FontDescriptor에서 정보 추출
        
        Args:
            descriptor: FontDescriptor 딕셔너리
            
        Returns:
            Dict[str, Any]: 디스크립터 정보
        """
        info = {}
        
        try:
            # 폰트 플래그
            if '/Flags' in descriptor:
                flags = int(descriptor['/Flags'])
                info['is_fixed_pitch'] = bool(flags & 1)
                info['is_serif'] = bool(flags & 2)
                info['is_symbolic'] = bool(flags & 4)
                info['is_script'] = bool(flags & 8)
                info['is_italic'] = bool(flags & 64)
                
            # 폰트 파일 존재 여부 (임베딩 확인)
            if '/FontFile' in descriptor or '/FontFile2' in descriptor or '/FontFile3' in descriptor:
                info['is_embedded'] = True
            else:
                info['is_embedded'] = False
                
            # 기타 메트릭
            if '/Ascent' in descriptor:
                info['ascent'] = float(descriptor['/Ascent'])
            if '/Descent' in descriptor:
                info['descent'] = float(descriptor['/Descent'])
            if '/CapHeight' in descriptor:
                info['cap_height'] = float(descriptor['/CapHeight'])
                
        except Exception as e:
            self.logger.debug(f"디스크립터 정보 추출 오류: {e}")
            
        return info
        
    def identify_subset_fonts(self, font_names: List[str]) -> Dict[str, bool]:
        """
        서브셋 폰트 식별
        
        Args:
            font_names: 폰트 이름 목록
            
        Returns:
            Dict[str, bool]: 폰트별 서브셋 여부
        """
        subset_map = {}
        
        # 서브셋 패턴: ABCDEF+FontName 또는 +FontName
        subset_pattern = re.compile(r'^([A-Z]{6}\+|^\+)')
        
        for font_name in font_names:
            is_subset = bool(subset_pattern.match(font_name))
            subset_map[font_name] = is_subset
            
            if is_subset:
                self.logger.debug(f"서브셋 폰트 감지: {font_name}")
                
        return subset_map