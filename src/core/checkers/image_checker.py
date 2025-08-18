# src/core/checkers/image_checker.py
"""
이미지 품질 검사기

이미지 해상도, 압축 품질, 색상 모드 등
이미지 관련 품질 문제를 검사합니다.
"""

from typing import Optional, List, Dict, Any
import fitz  # PyMuPDF

from .base_checker import BaseChecker, CheckRule, CheckerContext
from ..models import AnalysisResult, QualityIssue, ImageInfo
from ..models.quality_issue import (
    IssueSeverity, IssueCategory,
    create_low_resolution_image_issue
)


class ImageResolutionRule(CheckRule):
    """이미지 해상도 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="image_resolution",
            category=IssueCategory.IMAGE_RESOLUTION,
            default_severity=IssueSeverity.WARNING
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """이미지 해상도 검사"""
        # 설정값 가져오기
        min_dpi = context.profile_settings.get('min_image_dpi', 72)
        warning_dpi = context.profile_settings.get('warning_image_dpi', 150)
        optimal_dpi = context.profile_settings.get('optimal_image_dpi', 300)
        
        # 저해상도 이미지 분류
        critical_images = []  # min_dpi 미만
        warning_images = []   # warning_dpi 미만
        
        for img in analysis_result.images:
            if img.effective_dpi <= 0:
                continue  # DPI 정보가 없는 이미지는 건너뛰기
                
            if img.effective_dpi < min_dpi:
                critical_images.append({
                    'page': img.page,
                    'resolution': img.effective_dpi,
                    'size': f"{img.width}x{img.height}",
                    'display_size': f"{img.display_width:.1f}x{img.display_height:.1f}mm"
                })
            elif img.effective_dpi < warning_dpi:
                warning_images.append({
                    'page': img.page,
                    'resolution': img.effective_dpi,
                    'size': f"{img.width}x{img.height}",
                    'display_size': f"{img.display_width:.1f}x{img.display_height:.1f}mm"
                })
        
        # 문제가 없으면 None 반환
        if not critical_images and not warning_images:
            return None
        
        # 가장 심각한 문제 기준으로 이슈 생성
        if critical_images:
            severity = IssueSeverity.ERROR
            title = "매우 낮은 해상도 이미지"
            count = len(critical_images)
            min_found = min(img['resolution'] for img in critical_images)
            description = (f"{count}개 이미지가 {min_dpi}dpi 미만입니다. "
                          f"인쇄 품질이 심각하게 저하됩니다. (최저: {min_found:.0f}dpi)")
            problem_images = critical_images
        else:
            severity = self.get_severity(context)
            title = "낮은 해상도 이미지"
            count = len(warning_images)
            min_found = min(img['resolution'] for img in warning_images)
            description = (f"{count}개 이미지가 {warning_dpi}dpi 미만입니다. "
                          f"일반 인쇄에는 문제가 있을 수 있습니다. (최저: {min_found:.0f}dpi)")
            problem_images = warning_images
        
        # 모든 문제 이미지 합치기
        all_problem_images = critical_images + warning_images
        pages = sorted(set(img['page'] for img in all_problem_images))
        
        issue = QualityIssue(
            category=self.category,
            severity=severity,
            title=title,
            description=description,
            pages=pages,
            details={
                'critical_count': len(critical_images),
                'warning_count': len(warning_images),
                'min_dpi': min_dpi,
                'warning_dpi': warning_dpi,
                'optimal_dpi': optimal_dpi,
                'problem_images': problem_images[:10],  # 최대 10개만
                'total_problem_images': len(all_problem_images)
            }
        )
        
        # 수정 옵션 (위험도 높음)
        issue.add_fix_option(
            method="upscale_images",
            description="저해상도 이미지 업스케일링 (품질 손실 가능)",
            parameters={'target_dpi': warning_dpi},
            risk_level="high"
        )
        
        return issue
    
    def get_description(self) -> str:
        return "인쇄 품질을 위한 이미지 해상도 검사"


class ImageCompressionRule(CheckRule):
    """이미지 압축 품질 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="image_compression",
            category=IssueCategory.IMAGE_COMPRESSION,
            default_severity=IssueSeverity.WARNING
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """이미지 압축 품질 검사"""
        # PDF 경로 필요
        pdf_path = analysis_result.document.path
        
        # 압축 품질 분석
        compression_info = self._analyze_compression_quality(pdf_path, analysis_result.images)
        
        if not compression_info['low_quality_images']:
            return None
        
        issue = QualityIssue(
            category=self.category,
            severity=self.get_severity(context),
            title="과도한 이미지 압축",
            description=(f"{len(compression_info['low_quality_images'])}개 이미지가 "
                        "과도하게 압축되어 있습니다. 인쇄 시 품질 저하가 예상됩니다."),
            pages=[img['page'] for img in compression_info['low_quality_images']],
            details={
                'count': len(compression_info['low_quality_images']),
                'total_jpeg': compression_info['jpeg_count'],
                'low_quality_details': compression_info['low_quality_images'][:5]  # 최대 5개
            }
        )
        
        return issue
    
    def _analyze_compression_quality(self, pdf_path, images: List[ImageInfo]) -> Dict[str, Any]:
        """v1 로직을 참고한 압축 품질 분석"""
        compression_info = {
            'jpeg_count': 0,
            'low_quality_images': []
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            # 이미지별로 압축 품질 확인
            for img_info in images:
                if img_info.filter == 'DCTDecode' or 'JPEG' in img_info.filter:
                    compression_info['jpeg_count'] += 1
                    
                    # 압축률 추정 (간단한 휴리스틱)
                    # 파일 크기 / (픽셀 수 * 색상 채널)
                    if img_info.file_size > 0 and img_info.width > 0 and img_info.height > 0:
                        pixel_count = img_info.width * img_info.height
                        bytes_per_pixel = img_info.file_size / pixel_count
                        
                        # 0.3 바이트/픽셀 미만이면 과도한 압축으로 판단
                        if bytes_per_pixel < 0.3:
                            compression_info['low_quality_images'].append({
                                'page': img_info.page,
                                'size': f"{img_info.width}x{img_info.height}",
                                'compression_ratio': bytes_per_pixel,
                                'filter': img_info.filter
                            })
            
            doc.close()
            
        except Exception as e:
            # 압축 품질 분석 중 오류 발생
            pass
        
        return compression_info
    
    def get_description(self) -> str:
        return "과도한 이미지 압축으로 인한 품질 저하 검사"


class ImageColorModeRule(CheckRule):
    """이미지 색상 모드 검사 규칙"""
    
    def __init__(self):
        super().__init__(
            name="image_color_mode",
            category=IssueCategory.IMAGE_COLOR,
            default_severity=IssueSeverity.WARNING
        )
    
    def check(self, analysis_result: AnalysisResult, context: CheckerContext) -> Optional[QualityIssue]:
        """이미지 내 RGB 색상 검사"""
        # RGB 검사 설정 확인
        check_rgb = context.profile_settings.get('check_rgb', True)
        allow_rgb = context.profile_settings.get('allow_rgb', False)
        check_images = context.profile_settings.get('check_images', True)
        
        if not check_rgb or not check_images:
            return None
        
        # RGB 이미지 찾기
        rgb_images = []
        for img in analysis_result.images:
            if img.color_space.value == 'RGB':
                rgb_images.append({
                    'page': img.page,
                    'size': f"{img.width}x{img.height}",
                    'location': f"({img.x:.1f}, {img.y:.1f})"
                })
        
        if not rgb_images:
            return None
        
        # RGB 허용 여부에 따라 심각도 결정
        severity = IssueSeverity.INFO if allow_rgb else self.get_severity(context)
        
        issue = QualityIssue(
            category=self.category,
            severity=severity,
            title="RGB 색상 이미지",
            description=(f"{len(rgb_images)}개 이미지가 RGB 색상 공간을 사용합니다. "
                        "인쇄용으로는 CMYK 변환이 필요할 수 있습니다."),
            pages=sorted(set(img['page'] for img in rgb_images)),
            details={
                'count': len(rgb_images),
                'allow_rgb': allow_rgb,
                'rgb_images': rgb_images[:10]  # 최대 10개
            }
        )
        
        if not allow_rgb:
            issue.add_fix_option(
                method="convert_image_rgb_to_cmyk",
                description="이미지를 CMYK로 변환",
                parameters={'profile': 'ISO Coated v2'},
                risk_level="low"
            )
        
        return issue
    
    def get_description(self) -> str:
        return "이미지의 색상 모드 (RGB/CMYK) 검사"


class ImageChecker(BaseChecker):
    """
    이미지 품질 검사기
    
    해상도, 압축 품질, 색상 모드 등을 종합적으로 검사합니다.
    """
    
    def __init__(self):
        super().__init__("Image")
    
    def _initialize_rules(self):
        """이미지 관련 검사 규칙 초기화"""
        # 해상도 검사
        self.add_rule(ImageResolutionRule())
        
        # 압축 품질 검사
        self.add_rule(ImageCompressionRule())
        
        # 색상 모드 검사
        self.add_rule(ImageColorModeRule())
    
    def get_description(self) -> str:
        return "이미지 해상도, 압축 품질, 색상 모드 등을 검사합니다."
    
    def get_resolution_statistics(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """이미지 해상도 통계 반환"""
        stats = {
            'total_images': len(analysis_result.images),
            'resolution_distribution': {
                'critical': 0,     # < 72 DPI
                'warning': 0,      # 72-150 DPI
                'acceptable': 0,   # 150-300 DPI
                'optimal': 0       # >= 300 DPI
            },
            'avg_resolution': 0,
            'min_resolution': float('inf'),
            'max_resolution': 0
        }
        
        valid_dpis = []
        
        for img in analysis_result.images:
            if img.effective_dpi > 0:
                valid_dpis.append(img.effective_dpi)
                
                # 분류
                if img.effective_dpi < 72:
                    stats['resolution_distribution']['critical'] += 1
                elif img.effective_dpi < 150:
                    stats['resolution_distribution']['warning'] += 1
                elif img.effective_dpi < 300:
                    stats['resolution_distribution']['acceptable'] += 1
                else:
                    stats['resolution_distribution']['optimal'] += 1
                
                # 최소/최대
                stats['min_resolution'] = min(stats['min_resolution'], img.effective_dpi)
                stats['max_resolution'] = max(stats['max_resolution'], img.effective_dpi)
        
        # 평균 계산
        if valid_dpis:
            stats['avg_resolution'] = sum(valid_dpis) / len(valid_dpis)
            
        if stats['min_resolution'] == float('inf'):
            stats['min_resolution'] = 0
        
        return stats