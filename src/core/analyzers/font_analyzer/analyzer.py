# -*- coding: utf-8 -*-
"""
폰트 분석기 메인 클래스

PDF 폰트 정보를 종합적으로 분석합니다.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..base_analyzer import BaseAnalyzer
from ...models import PDFDocument, FontInfo, FontType

from .models import (
    FontAnalysisResult, 
    FontAnalysisMethod,
    FontIssue,
    PDFFontsResult
)
from .extractor import FontExtractor
from .external_tools import ExternalToolsManager
from .validator import FontValidator
from ....external.tool_manager import get_tool_manager


class FontAnalyzer(BaseAnalyzer):
    """
    PDF 폰트 분석기
    
    PDF 파일의 폰트 정보를 분석합니다:
    - 사용된 폰트 목록
    - 폰트 타입 (TrueType, Type1, CID 등)
    - 임베딩 상태
    - 서브셋 여부
    - 인코딩 정보
    - 페이지별 폰트 사용 현황
    
    외부 도구(pdffonts)가 있으면 더 정확한 분석을 수행합니다.
    """
    
    def __init__(self, tool_manager=None):
        """
        폰트 분석기 초기화
        
        Args:
            tool_manager: 외부 도구 관리자 (선택사항)
        """
        super().__init__("FontAnalyzer")
        self.tool_manager = tool_manager
        
        # 로거 설정
        self.logger = logging.getLogger(__name__)
        
        # 컴포넌트 초기화
        self.extractor = FontExtractor(self.logger)
        self.external_tools = ExternalToolsManager(self.logger)
        self.validator = FontValidator(self.logger)
        
        # PDF 표준 14 폰트
        self.standard_14_fonts = FontValidator.STANDARD_14_FONTS
        
    def initialize(self) -> bool:
        """
        분석기 초기화 - pdffonts 도구 확인
        
        Returns:
            bool: 초기화 성공 여부
        """
        # 외부 도구 확인
        available_tools = self.external_tools.check_available_tools()
        
        if available_tools['pdffonts']:
            self.logger.info("pdffonts 도구를 사용하여 정밀 분석을 수행합니다")
        else:
            self.logger.warning("pdffonts 도구를 사용할 수 없어 기본 분석만 수행됩니다")
            
        return super().initialize()
        
    def analyze_result(self, analysis_result):
        """
        AnalysisResult 객체에 폰트 정보 추가
        
        Args:
            analysis_result: AnalysisResult 객체
        """
        try:
            # PDF 경로 가져오기 (path 속성 사용 - 전체 경로)
            pdf_path = analysis_result.document.path
            if not isinstance(pdf_path, Path):
                pdf_path = Path(pdf_path)
            
            # 폰트 분석 수행
            font_data = self.analyze(analysis_result.document, pdf_path)
            
            # 결과를 AnalysisResult에 저장
            if isinstance(font_data, dict) and 'fonts' in font_data:
                # 폰트 정보를 FontInfo 객체로 변환
                for font_name, font_dict in font_data['fonts'].items():
                    font_info = self._dict_to_font_info(font_name, font_dict)
                    if font_info:
                        analysis_result.fonts[font_name] = font_info
            
        except Exception as e:
            self.logger.error(f"폰트 분석 실패: {e}")
    
    def _dict_to_font_info(self, font_name: str, font_dict: Dict[str, Any]) -> Optional[FontInfo]:
        """딕셔너리를 FontInfo 객체로 변환"""
        try:
            # FontType 결정
            font_type = self._determine_font_type(font_dict.get('type', 'Unknown'))
            
            return FontInfo(
                name=font_name,
                type=font_type,
                is_embedded=font_dict.get('is_embedded', False),
                is_subset=font_dict.get('is_subset', False),
                encoding=font_dict.get('encoding', ''),
                pages_used=font_dict.get('pages_used', [])
            )
        except Exception as e:
            self.logger.error(f"FontInfo 변환 실패: {e}")
            return None
    
    def analyze(self, document: PDFDocument, pdf_path: Path) -> Dict[str, Any]:
        """
        PDF 폰트 정보 분석
        
        Args:
            document: PDF 문서 모델 객체
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: 폰트 분석 결과
        """
        self.logger.info(f"폰트 분석 시작: {pdf_path.name}")
        
        # 분석 방법 선택
        analysis_method = FontAnalysisMethod.PIKEPDF
        
        # 먼저 tool_manager 사용 시도
        tool_manager = get_tool_manager()
        if tool_manager.has_tool('pdffonts'):
            try:
                # tool_manager를 통해 pdffonts 실행
                self.logger.info("tool_manager를 통해 pdffonts 실행")
                result = tool_manager.run_tool('pdffonts', [str(pdf_path)])
                if result.returncode == 0 and result.stdout:
                    # pdffonts 결과 파싱
                    external_result = self._parse_pdffonts_output(result.stdout)
                    if external_result.success:
                        result = self._process_external_result(external_result)
                        analysis_method = FontAnalysisMethod.PDFFONTS
                        self.logger.info(f"pdffonts를 사용한 분석 완료: {result.total_fonts}개 폰트 발견")
                    else:
                        self.logger.warning("pdffonts 결과 파싱 실패, 내부 분석으로 폴백")
                        result = self._perform_internal_analysis(pdf_path)
                else:
                    self.logger.warning(f"pdffonts 실행 실패: {result.stderr}")
                    result = self._perform_internal_analysis(pdf_path)
            except Exception as e:
                self.logger.warning(f"tool_manager pdffonts 실행 실패: {e}")
                # 기존 external_tools 사용 시도
                if self.external_tools.check_pdffonts_availability():
                    external_result = self.external_tools.analyze_with_pdffonts(pdf_path)
                    if external_result.success:
                        result = self._process_external_result(external_result)
                        analysis_method = FontAnalysisMethod.PDFFONTS
                        self.logger.info(f"pdffonts를 사용한 분석 완료: {result.total_fonts}개 폰트 발견")
                    else:
                        result = self._perform_internal_analysis(pdf_path)
                else:
                    result = self._perform_internal_analysis(pdf_path)
        # tool_manager에 pdffonts가 없으면 기존 방식 시도
        elif self.external_tools.check_pdffonts_availability():
            external_result = self.external_tools.analyze_with_pdffonts(pdf_path)
            
            if external_result.success:
                # pdffonts 결과 처리
                result = self._process_external_result(external_result)
                analysis_method = FontAnalysisMethod.PDFFONTS
                self.logger.info(f"pdffonts를 사용한 분석 완료: {result.total_fonts}개 폰트 발견")
            else:
                self.logger.warning(f"pdffonts 분석 실패: {external_result.error_message}")
                # 내부 분석으로 폴백
                result = self._perform_internal_analysis(pdf_path)
        else:
            # 내부 분석 수행
            result = self._perform_internal_analysis(pdf_path)
            
        # 분석 방법 설정
        result.analysis_method = analysis_method
        
        # 유효성 검사
        issues = self.validator.validate_fonts(result.fonts)
        result.font_issues.extend(issues)
        
        # 인쇄 호환성 검사
        print_issues = self.validator.check_print_compatibility(result.fonts)
        result.font_issues.extend(print_issues)
        
        self.logger.info(f"폰트 분석 완료: {result.total_fonts}개 폰트, {len(result.font_issues)}개 문제 발견")
        
        # 결과를 딕셔너리로 변환
        return result.to_dict()
        
    def _perform_internal_analysis(self, pdf_path: Path) -> FontAnalysisResult:
        """
        내부 엔진을 사용한 폰트 분석
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            FontAnalysisResult: 분석 결과
        """
        self.logger.debug("pikepdf를 사용한 내부 분석 수행")
        
        # 폰트 추출
        font_mapping = self.extractor.extract_fonts_from_pdf(pdf_path)
        
        # 폰트 정보 구성
        fonts = {}
        subset_count = 0
        
        for font_name in font_mapping.font_to_pages.keys():
            # 서브셋 여부 확인
            is_subset = self._is_subset_font(font_name)
            if is_subset:
                subset_count += 1
                
            # 표준 14 폰트 확인
            is_standard_14 = self._is_standard_14_font(font_name)
            
            # FontInfo 객체 생성
            font_info = FontInfo(
                name=font_name,
                type=FontType.UNKNOWN,
                is_embedded=True,  # pikepdf로는 정확한 판단 어려움
                is_subset=is_subset,
                encoding='Unknown',
                is_standard_14=is_standard_14,
                pages_used=font_mapping.get_pages_for_font(font_name)
            )
            
            fonts[font_name] = font_info
            
        # 결과 구성
        result = FontAnalysisResult(
            fonts=fonts,
            total_fonts=len(fonts),
            embedded_fonts=len(fonts),  # 정확한 정보 없음
            missing_fonts=0,
            subset_fonts=subset_count,
            type3_fonts=0,
            font_issues=[],
            analysis_method=FontAnalysisMethod.PIKEPDF,
            warnings=['pdffonts를 사용할 수 없어 제한된 분석만 수행됨']
        )
        
        return result
        
    def _parse_pdffonts_output(self, output: str) -> PDFFontsResult:
        """
        pdffonts 출력 파싱
        
        Args:
            output: pdffonts 명령어 출력
            
        Returns:
            PDFFontsResult: 파싱된 결과
        """
        fonts = {}
        lines = output.strip().split('\n')
        
        if len(lines) < 2:
            return PDFFontsResult(fonts={}, error_message="출력이 너무 짧음")
        
        # 헤더와 구분선에서 컬럼 위치 동적 감지
        header_line = lines[0] if len(lines) > 0 else ""
        separator_line = lines[1] if len(lines) > 1 else ""
        
        # 구분선에서 컬럼 경계 찾기
        columns = []
        if separator_line and '-' in separator_line:
            import re
            start = 0
            for match in re.finditer(r'-+', separator_line):
                columns.append((start, match.end()))
                start = match.end() + 1
        
        # 컬럼이 제대로 감지되지 않으면 기본값 사용
        if len(columns) < 6:
            # fallback: 일반적인 pdffonts 출력 형식
            columns = [
                (0, 36),    # name
                (37, 54),   # type  
                (55, 71),   # encoding
                (72, 75),   # emb
                (76, 79),   # sub
                (80, 83),   # uni
                (84, None)  # object ID
            ]
        
        # 데이터 라인 파싱
        for line in lines[2:]:
            if not line.strip():
                continue
            
            try:
                # 동적으로 감지된 컬럼 위치로 파싱
                values = []
                for start, end in columns:
                    if end is None:
                        value = line[start:].strip() if start < len(line) else ''
                    else:
                        value = line[start:end].strip() if start < len(line) else ''
                    values.append(value)
                
                # 최소 6개 컬럼이 있어야 유효한 데이터
                if len(values) >= 6:
                    font_name = values[0]
                    font_type = values[1]
                    encoding = values[2]
                    embedded = values[3].lower() == 'yes'
                    subset = values[4].lower() == 'yes'
                    unicode = values[5].lower() == 'yes'
                    
                    # 유효한 데이터인지 확인
                    if font_name and font_type:
                        fonts[font_name] = {
                            'type': font_type,
                            'encoding': encoding,
                            'embedded': embedded,
                            'subset': subset,
                            'unicode': unicode
                        }
            except Exception as e:
                self.logger.debug(f"폰트 라인 파싱 오류: {line} - {e}")
                continue
        
        return PDFFontsResult(
            fonts=fonts,
            raw_output=output,
            error_message=None if (len(fonts) > 0 or len(lines) == 2) else "폰트를 찾을 수 없음"
        )
    
    def _process_external_result(self, external_result: PDFFontsResult) -> FontAnalysisResult:
        """
        외부 도구 결과를 표준 형식으로 변환
        
        Args:
            external_result: pdffonts 분석 결과
            
        Returns:
            FontAnalysisResult: 표준화된 결과
        """
        fonts = {}
        embedded_count = 0
        missing_count = 0
        subset_count = 0
        type3_count = 0
        font_issues = []
        
        for font_name, font_data in external_result.fonts.items():
            # FontType 결정
            font_type = self._determine_font_type(font_data.get('type', ''))
            
            # 서브셋 여부 확인
            is_subset = font_data.get('subset', False) or self._is_subset_font(font_name)
            if is_subset:
                subset_count += 1
                
            # 표준 14 폰트 확인
            is_standard_14 = self._is_standard_14_font(font_name)
            
            # FontInfo 객체 생성
            font_info = FontInfo(
                name=font_name,
                type=font_type,
                is_embedded=font_data.get('embedded', False),
                is_subset=is_subset,
                encoding=font_data.get('encoding', 'Unknown'),
                is_standard_14=is_standard_14,
                has_unicode_map=font_data.get('unicode', False)
            )
            
            fonts[font_name] = font_info
            
            # 통계 업데이트
            if font_info.is_embedded:
                embedded_count += 1
            elif not font_info.is_standard_14:
                missing_count += 1
                
            if font_type == FontType.TYPE3:
                type3_count += 1
                
        # 결과 구성
        result = FontAnalysisResult(
            fonts=fonts,
            total_fonts=len(fonts),
            embedded_fonts=embedded_count,
            missing_fonts=missing_count,
            subset_fonts=subset_count,
            type3_fonts=type3_count,
            font_issues=font_issues,
            analysis_method=FontAnalysisMethod.PDFFONTS
        )
        
        return result
        
    def _determine_font_type(self, type_str: str) -> FontType:
        """
        폰트 타입 문자열을 FontType enum으로 변환
        
        Args:
            type_str: 폰트 타입 문자열
            
        Returns:
            FontType: 폰트 타입
        """
        # type_str이 이미 FontType enum일 수도 있음
        if hasattr(type_str, 'value'):
            return type_str  # 이미 FontType enum
        type_str = str(type_str).upper()
        
        if 'TRUETYPE' in type_str:
            return FontType.TRUETYPE
        elif 'TYPE1' in type_str or 'TYPE 1' in type_str:
            return FontType.TYPE1
        elif 'TYPE3' in type_str or 'TYPE 3' in type_str:
            return FontType.TYPE3
        elif 'TYPE0' in type_str or 'TYPE 0' in type_str:
            return FontType.TYPE0
        elif 'CID' in type_str:
            if 'TYPE0' in type_str:
                return FontType.CID_TYPE0
            elif 'TYPE2' in type_str:
                return FontType.CID_TYPE2
            else:
                return FontType.TYPE0
        elif 'OPENTYPE' in type_str:
            return FontType.OPENTYPE
        else:
            return FontType.UNKNOWN
            
    def _is_subset_font(self, font_name: str) -> bool:
        """
        서브셋 폰트 여부 확인
        
        Args:
            font_name: 폰트 이름
            
        Returns:
            bool: 서브셋 여부
        """
        return font_name.startswith('+') or bool(re.match(r'^[A-Z]{6}\+', font_name))
        
    def _is_standard_14_font(self, font_name: str) -> bool:
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
        
        return base_name in self.standard_14_fonts
        
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
        deps = {
            'pikepdf': False,
            'pdffonts': self.external_tools.check_pdffonts_availability()
        }
        
        try:
            import pikepdf
            deps['pikepdf'] = True
        except ImportError:
            pass
            
        return deps