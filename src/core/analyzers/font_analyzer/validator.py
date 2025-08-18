# -*- coding: utf-8 -*-
"""
폰트 유효성 검사 모듈

폰트의 유효성을 검사하고 문제점을 검출합니다.
"""

import re
from typing import Dict, Any, List, Set, Optional
import logging

from .models import FontIssue


class FontValidator:
    """폰트 유효성 검사기"""
    
    # PDF 표준 14 폰트
    STANDARD_14_FONTS = {
        'Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic',
        'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique',
        'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique',
        'Symbol', 'ZapfDingbats'
    }
    
    # CJK (한중일) 폰트 패턴
    CJK_FONT_PATTERNS = [
        r'Batang', r'Dotum', r'Gulim', r'Malgun',  # 한국어
        r'Ming', r'Song', r'Hei', r'Kai',  # 중국어
        r'Mincho', r'Gothic',  # 일본어
        r'CJK', r'Korean', r'Chinese', r'Japanese'
    ]
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
    def validate_fonts(self, fonts: Dict[str, Any]) -> List[FontIssue]:
        """
        폰트 목록 유효성 검사
        
        Args:
            fonts: 폰트 정보 딕셔너리
            
        Returns:
            List[FontIssue]: 발견된 문제 목록
        """
        issues = []
        
        for font_name, font_info in fonts.items():
            # 각 폰트별 검사
            font_issues = self._validate_single_font(font_name, font_info)
            issues.extend(font_issues)
            
        # 전체 폰트 세트 검사
        set_issues = self._validate_font_set(fonts)
        issues.extend(set_issues)
        
        return issues
        
    def _validate_single_font(self, font_name: str, font_info: Dict[str, Any]) -> List[FontIssue]:
        """
        개별 폰트 유효성 검사
        
        Args:
            font_name: 폰트 이름
            font_info: 폰트 정보
            
        Returns:
            List[FontIssue]: 발견된 문제 목록
        """
        issues = []
        
        # 임베딩 검사
        if not self._is_embedded(font_info) and not self._is_standard_font(font_name):
            issues.append(FontIssue(
                type='missing_embedding',
                font=font_name,
                severity='error',
                description=f"폰트 '{font_name}'이(가) 임베딩되지 않았습니다"
            ))
            
        # Type3 폰트 검사
        if self._is_type3_font(font_info):
            issues.append(FontIssue(
                type='type3_font',
                font=font_name,
                severity='warning',
                description=f"Type3 폰트 '{font_name}' 사용 (품질 저하 가능)"
            ))
            
        # 인코딩 검사
        encoding_issue = self._check_encoding(font_name, font_info)
        if encoding_issue:
            issues.append(encoding_issue)
            
        # CJK 폰트 검사
        if self._is_cjk_font(font_name) and not self._has_unicode_support(font_info):
            issues.append(FontIssue(
                type='cjk_unicode_missing',
                font=font_name,
                severity='warning',
                description=f"CJK 폰트 '{font_name}'에 유니코드 매핑이 없습니다"
            ))
            
        return issues
        
    def _validate_font_set(self, fonts: Dict[str, Any]) -> List[FontIssue]:
        """
        전체 폰트 세트 유효성 검사
        
        Args:
            fonts: 폰트 정보 딕셔너리
            
        Returns:
            List[FontIssue]: 발견된 문제 목록
        """
        issues = []
        
        # 폰트 수가 너무 많은 경우
        if len(fonts) > 20:
            issues.append(FontIssue(
                type='too_many_fonts',
                font='',
                severity='warning',
                description=f"폰트가 너무 많습니다 ({len(fonts)}개). 파일 크기가 증가할 수 있습니다"
            ))
            
        # 일관성 없는 폰트 사용
        font_families = self._extract_font_families(fonts.keys())
        if len(font_families) > 5:
            issues.append(FontIssue(
                type='inconsistent_fonts',
                font='',
                severity='info',
                description=f"다양한 폰트 패밀리 사용 ({len(font_families)}개). 일관성 검토 필요"
            ))
            
        return issues
        
    def _is_embedded(self, font_info: Dict[str, Any]) -> bool:
        """
        폰트 임베딩 여부 확인
        
        Args:
            font_info: 폰트 정보
            
        Returns:
            bool: 임베딩 여부
        """
        # FontInfo 객체인 경우
        if hasattr(font_info, 'is_embedded'):
            return font_info.is_embedded
            
        # 딕셔너리인 경우
        return font_info.get('embedded', False) or font_info.get('is_embedded', False)
        
    def _is_standard_font(self, font_name: str) -> bool:
        """
        표준 14 폰트 여부 확인
        
        Args:
            font_name: 폰트 이름
            
        Returns:
            bool: 표준 폰트 여부
        """
        # 서브셋 접두사 제거
        base_name = re.sub(r'^[A-Z]{6}\+', '', font_name)
        base_name = base_name.lstrip('+')
        
        return base_name in self.STANDARD_14_FONTS
        
    def _is_type3_font(self, font_info: Dict[str, Any]) -> bool:
        """
        Type3 폰트 여부 확인
        
        Args:
            font_info: 폰트 정보
            
        Returns:
            bool: Type3 폰트 여부
        """
        # FontInfo 객체인 경우
        if hasattr(font_info, 'is_type3'):
            return font_info.is_type3
            
        # 딕셔너리인 경우
        font_type = font_info.get('type', '')
        # FontType enum이거나 문자열일 수 있음
        if hasattr(font_type, 'value'):
            font_type_str = font_type.value.upper()
        else:
            font_type_str = str(font_type).upper()
        return 'TYPE3' in font_type_str or 'TYPE 3' in font_type_str
        
    def _check_encoding(self, font_name: str, font_info: Dict[str, Any]) -> Optional[FontIssue]:
        """
        폰트 인코딩 검사
        
        Args:
            font_name: 폰트 이름
            font_info: 폰트 정보
            
        Returns:
            FontIssue: 인코딩 문제 또는 None
        """
        encoding = font_info.get('encoding', '')
        
        # 문제가 있는 인코딩
        problematic_encodings = ['Custom', 'Identity-H', 'Identity-V']
        
        if encoding in problematic_encodings and not self._has_unicode_support(font_info):
            return FontIssue(
                type='encoding_issue',
                font=font_name,
                severity='warning',
                description=f"폰트 '{font_name}'의 인코딩 '{encoding}'에 유니코드 매핑이 없을 수 있습니다"
            )
            
        return None
        
    def _has_unicode_support(self, font_info: Dict[str, Any]) -> bool:
        """
        유니코드 지원 여부 확인
        
        Args:
            font_info: 폰트 정보
            
        Returns:
            bool: 유니코드 지원 여부
        """
        # FontInfo 객체인 경우
        if hasattr(font_info, 'has_unicode_map'):
            return font_info.has_unicode_map
            
        # 딕셔너리인 경우
        return font_info.get('unicode', False) or font_info.get('has_unicode_map', False)
        
    def _is_cjk_font(self, font_name: str) -> bool:
        """
        CJK (한중일) 폰트 여부 확인
        
        Args:
            font_name: 폰트 이름
            
        Returns:
            bool: CJK 폰트 여부
        """
        for pattern in self.CJK_FONT_PATTERNS:
            if re.search(pattern, font_name, re.IGNORECASE):
                return True
        return False
        
    def _extract_font_families(self, font_names: List[str]) -> Set[str]:
        """
        폰트 패밀리 추출
        
        Args:
            font_names: 폰트 이름 목록
            
        Returns:
            Set[str]: 폰트 패밀리 집합
        """
        families = set()
        
        for font_name in font_names:
            # 서브셋 접두사 제거
            clean_name = re.sub(r'^[A-Z]{6}\+', '', font_name)
            clean_name = clean_name.lstrip('+')
            
            # 스타일 접미사 제거
            family = re.sub(r'[-_](Bold|Italic|Oblique|Regular|Light|Medium|Heavy).*$', '', clean_name, flags=re.IGNORECASE)
            
            families.add(family)
            
        return families
        
    def check_print_compatibility(self, fonts: Dict[str, Any]) -> List[FontIssue]:
        """
        인쇄 호환성 검사
        
        Args:
            fonts: 폰트 정보 딕셔너리
            
        Returns:
            List[FontIssue]: 인쇄 관련 문제 목록
        """
        issues = []
        
        for font_name, font_info in fonts.items():
            # 비트맵 폰트 검사
            if self._is_bitmap_font(font_info):
                issues.append(FontIssue(
                    type='bitmap_font',
                    font=font_name,
                    severity='error',
                    description=f"비트맵 폰트 '{font_name}' 사용 (인쇄 품질 문제)"
                ))
                
            # 저해상도 폰트 검사
            if self._is_low_resolution_font(font_info):
                issues.append(FontIssue(
                    type='low_resolution_font',
                    font=font_name,
                    severity='warning',
                    description=f"저해상도 폰트 '{font_name}' 감지"
                ))
                
        return issues
        
    def _is_bitmap_font(self, font_info: Dict[str, Any]) -> bool:
        """비트맵 폰트 여부 확인"""
        font_type = font_info.get('type', '')
        # FontType enum이거나 문자열일 수 있음
        if hasattr(font_type, 'value'):
            font_type_str = font_type.value.upper()
        else:
            font_type_str = str(font_type).upper()
        return 'BITMAP' in font_type_str or 'TYPE3' in font_type_str
        
    def _is_low_resolution_font(self, font_info: Dict[str, Any]) -> bool:
        """저해상도 폰트 여부 확인"""
        # 구현 필요에 따라 추가
        return False