# -*- coding: utf-8 -*-
"""
고급 PDF 검사 규칙 - Ghent Output Suite 테스트 기반

이 모듈은 Ghent Output Suite에서 요구하는 고급 검사 규칙들을 구현합니다.
"""

from typing import List, Optional
from dataclasses import dataclass

from ..models import AnalysisResult, QualityIssue
from .base_checker import BaseChecker, CheckerContext


class AdvancedChecker(BaseChecker):
    """고급 PDF 검사기"""
    
    def __init__(self):
        """초기화"""
        super().__init__("AdvancedChecker")
    
    def _initialize_rules(self):
        """검사 규칙 초기화 - 현재는 직접 검사 수행"""
        # AdvancedChecker는 check 메서드에서 직접 검사를 수행하므로
        # 별도의 규칙 객체를 사용하지 않음
        pass
    
    def get_description(self) -> str:
        """검사기 설명 반환"""
        return "고급 PDF 품질 검사 (Ghent Output Suite 대응)"
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> List[QualityIssue]:
        """
        고급 품질 검사 수행
        
        Args:
            analysis_result: PDF 분석 결과
            context: 검사 컨텍스트
            
        Returns:
            List[QualityIssue]: 발견된 이슈 목록
        """
        issues = []
        
        # 1. 오버프린트 검사
        overprint_issues = self._check_overprint(analysis_result, context)
        issues.extend(overprint_issues)
        
        # 2. 16비트 이미지 검사
        sixteen_bit_issues = self._check_16bit_images(analysis_result, context)
        issues.extend(sixteen_bit_issues)
        
        # 3. JPEG2000/JBIG2 압축 검사
        compression_issues = self._check_compression(analysis_result, context)
        issues.extend(compression_issues)
        
        # 4. ICC 프로파일 검사
        icc_issues = self._check_icc_profiles(analysis_result, context)
        issues.extend(icc_issues)
        
        # 5. DeviceN 색상 공간 검사
        devicen_issues = self._check_devicen_colors(analysis_result, context)
        issues.extend(devicen_issues)
        
        # 6. Type3 폰트 검사
        type3_issues = self._check_type3_fonts(analysis_result, context)
        issues.extend(type3_issues)
        
        return issues
    
    def _check_overprint(self, analysis_result: AnalysisResult, context: CheckerContext) -> List[QualityIssue]:
        """오버프린트 설정 검사"""
        issues = []
        
        # 검사 활성화 여부 확인
        if not context.is_check_enabled('check_white_overprint'):
            return issues
        if not context.is_rule_enabled('white_overprint'):
            return issues
        
        # 색상 정보에서 오버프린트 확인
        if hasattr(analysis_result.colors, 'has_overprint') and analysis_result.colors.has_overprint:
            # 흰색 오버프린트 검사 (실제 구현 시 더 자세한 분석 필요)
            issue = QualityIssue(
                severity='warning',
                category='color',
                title='오버프린트 설정 발견',
                description='오버프린트 설정이 있습니다. 인쇄 시 예상치 못한 결과가 나올 수 있습니다.',
                pages=[],
                suggestion='오버프린트 설정을 확인하고 필요시 수정하세요.'
            )
            issues.append(issue)
        
        return issues
    
    def _check_16bit_images(self, analysis_result: AnalysisResult, context: CheckerContext) -> List[QualityIssue]:
        """16비트 이미지 검사"""
        issues = []
        
        # 검사 활성화 여부 확인
        if not context.is_check_enabled('check_16bit_images'):
            return issues
        if not context.is_rule_enabled('16bit_image'):
            return issues
        
        for image in analysis_result.images:
            if image.bits_per_component > 8:
                issue = QualityIssue(
                    severity='info',
                    category='image',
                    title=f'16비트 이미지 발견',
                    description=f'페이지 {image.page}에 {image.bits_per_component}비트 이미지가 있습니다.',
                    pages=[image.page],
                    suggestion='파일 크기를 줄이려면 8비트로 변환을 고려하세요.'
                )
                issues.append(issue)
        
        return issues
    
    def _check_compression(self, analysis_result: AnalysisResult, context: CheckerContext) -> List[QualityIssue]:
        """이미지 압축 방식 검사"""
        issues = []
        
        # JPEG2000 검사 활성화 확인
        check_jpeg2000 = context.is_check_enabled('check_jpeg2000') and context.is_rule_enabled('jpeg2000_compression')
        check_jbig2 = context.is_check_enabled('check_jbig2') and context.is_rule_enabled('jbig2_compression')
        
        if not check_jpeg2000 and not check_jbig2:
            return issues
        
        problematic_compressions = []
        if check_jpeg2000:
            problematic_compressions.extend(['JPEG2000', 'JPXDecode'])
        if check_jbig2:
            problematic_compressions.extend(['JBIG2', 'JBIG2Decode'])
        
        for image in analysis_result.images:
            if hasattr(image, 'filter') and image.filter in problematic_compressions:
                issue = QualityIssue(
                    severity='warning',
                    category='image',
                    title=f'{image.filter} 압축 사용',
                    description=f'페이지 {image.page}의 이미지가 {image.filter} 압축을 사용합니다.',
                    pages=[image.page],
                    suggestion='일부 RIP에서 지원하지 않을 수 있습니다. 표준 압축 방식 사용을 권장합니다.'
                )
                issues.append(issue)
        
        return issues
    
    def _check_icc_profiles(self, analysis_result: AnalysisResult, context: CheckerContext) -> List[QualityIssue]:
        """ICC 프로파일 검사"""
        issues = []
        
        # 검사 활성화 여부 확인
        if not context.is_check_enabled('check_icc_profile'):
            return issues
        if not context.is_rule_enabled('icc_profile_missing'):
            return issues
        
        # PDF 문서에 ICC 프로파일이 없는 경우
        if hasattr(analysis_result.document, 'has_icc_profile'):
            if not analysis_result.document.has_icc_profile:
                issue = QualityIssue(
                    severity='info',
                    category='color',
                    title='ICC 프로파일 없음',
                    description='문서에 ICC 프로파일이 포함되지 않았습니다.',
                    pages=[],
                    suggestion='색상 일관성을 위해 적절한 ICC 프로파일 추가를 고려하세요.'
                )
                issues.append(issue)
        
        return issues
    
    def _check_devicen_colors(self, analysis_result: AnalysisResult, context: CheckerContext) -> List[QualityIssue]:
        """DeviceN 색상 공간 검사"""
        issues = []
        
        # 검사 활성화 여부 확인
        if not context.is_check_enabled('check_devicen'):
            return issues
        if not context.is_rule_enabled('devicen_color'):
            return issues
        
        # DeviceN 색상 공간 사용 확인
        if hasattr(analysis_result.colors, 'color_spaces_used'):
            from ..models.analysis_result import ColorSpace
            if ColorSpace.DEVICE_N in analysis_result.colors.color_spaces_used:
                issue = QualityIssue(
                    severity='warning',
                    category='color',
                    title='DeviceN 색상 공간 사용',
                    description='DeviceN 색상 공간이 사용되었습니다. 복잡한 색상 처리가 필요합니다.',
                    pages=[],
                    suggestion='가능하면 표준 CMYK 또는 별색으로 변환을 고려하세요.'
                )
                issues.append(issue)
        
        return issues
    
    def _check_type3_fonts(self, analysis_result: AnalysisResult, context: CheckerContext) -> List[QualityIssue]:
        """Type3 폰트 검사"""
        issues = []
        
        # 검사 활성화 여부 확인
        if not context.is_check_enabled('check_type3_fonts'):
            return issues
        if not context.is_rule_enabled('type3_font'):
            return issues
        
        if hasattr(analysis_result, 'fonts'):
            for font_name, font_info in analysis_result.fonts.items():
                if hasattr(font_info, 'is_type3') and font_info.is_type3:
                    issue = QualityIssue(
                        severity='warning',
                        category='font',
                        title=f'Type3 폰트 사용: {font_name}',
                        description='Type3 폰트는 비트맵 폰트로 품질이 낮을 수 있습니다.',
                        pages=font_info.pages_used if hasattr(font_info, 'pages_used') else [],
                        suggestion='TrueType 또는 Type1 폰트로 교체를 권장합니다.'
                    )
                    issues.append(issue)
        
        return issues