"""
PDF 분석 결과 모델 - PDF 분석 결과를 담는 종합 객체

이 모듈은 PDF 파일 분석 후 생성되는 모든 정보를 체계적으로 관리합니다.
폰트, 색상, 이미지 정보와 발견된 품질 이슈들을 포함합니다.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any
from datetime import datetime
from enum import Enum

from .pdf_document import PDFDocument, PageInfo
from .quality_issue import QualityIssue


class ColorSpace(Enum):
    """색상 공간 정의"""
    RGB = "RGB"
    CMYK = "CMYK"
    GRAYSCALE = "Grayscale"
    LAB = "Lab"
    SPOT = "Spot"
    DEVICE_N = "DeviceN"
    INDEXED = "Indexed"
    PATTERN = "Pattern"
    SEPARATION = "Separation"


class FontType(Enum):
    """폰트 타입 정의"""
    TYPE1 = "Type1"
    TYPE3 = "Type3"
    TRUETYPE = "TrueType"
    TYPE0 = "Type0"  # CID 폰트
    CID_TYPE0 = "CIDFontType0"
    CID_TYPE2 = "CIDFontType2"
    OPENTYPE = "OpenType"
    UNKNOWN = "Unknown"


@dataclass
class FontInfo:
    """폰트 정보"""
    name: str
    type: FontType
    is_embedded: bool
    is_subset: bool
    encoding: str
    pages_used: List[int] = field(default_factory=list)
    
    # 추가 정보
    is_standard_14: bool = False  # PDF 표준 14개 폰트 중 하나인지
    has_unicode_map: bool = True
    char_count: int = 0  # 사용된 문자 수
    size_range: Tuple[float, float] = (0.0, 0.0)  # 최소/최대 크기
    
    @property
    def is_type3(self) -> bool:
        """Type3 폰트인지 확인"""
        return self.type == FontType.TYPE3
    
    @property
    def is_cid_font(self) -> bool:
        """CID 폰트인지 확인"""
        return self.type in [FontType.TYPE0, FontType.CID_TYPE0, FontType.CID_TYPE2]
    
    @property
    def needs_embedding(self) -> bool:
        """임베딩이 필요한지 확인"""
        return not self.is_embedded and not self.is_standard_14
    
    @property
    def page_count(self) -> int:
        """폰트가 사용된 페이지 수"""
        return len(set(self.pages_used))
    
    def get(self, key: str, default=None):
        """딕셔너리 스타일 접근 지원 (호환성용)"""
        return getattr(self, key, default)
    
    def __str__(self) -> str:
        """문자열 표현"""
        embed_status = "embedded" if self.is_embedded else "not embedded"
        subset_status = " (subset)" if self.is_subset else ""
        return f"{self.name}{subset_status} - {self.type.value} - {embed_status}"


@dataclass
class ColorInfo:
    """색상 정보"""
    color_spaces_used: Set[ColorSpace] = field(default_factory=set)
    spot_colors: List[str] = field(default_factory=list)
    has_transparency: bool = False
    has_overprint: bool = False
    
    # 색상 통계
    dominant_color_space: Optional[ColorSpace] = None
    rgb_object_count: int = 0
    cmyk_object_count: int = 0
    spot_color_count: int = 0
    
    # 잉크 커버리지 정보
    max_ink_coverage: float = 0.0  # 최대 잉크량 (%)
    avg_ink_coverage: float = 0.0  # 평균 잉크량 (%)
    over_limit_areas: List[Dict[str, Any]] = field(default_factory=list)  # 초과 영역
    
    # 호환성을 위한 속성 추가
    @property
    def color_spaces(self) -> List[str]:
        """색상 공간 리스트 (호환성용)"""
        return [cs.value if hasattr(cs, 'value') else str(cs) for cs in self.color_spaces_used]
    
    @property
    def has_rgb(self) -> bool:
        """RGB 사용 여부 (호환성용)"""
        return self.uses_rgb
    
    @property
    def has_cmyk(self) -> bool:
        """CMYK 사용 여부 (호환성용)"""
        return self.uses_cmyk
    
    @property
    def has_spot_colors(self) -> bool:
        """별색 사용 여부 (호환성용)"""
        return self.uses_spot_colors
    
    @property
    def uses_rgb(self) -> bool:
        """RGB 색상 사용 여부"""
        return ColorSpace.RGB in self.color_spaces_used
    
    @property
    def uses_cmyk(self) -> bool:
        """CMYK 색상 사용 여부"""
        return ColorSpace.CMYK in self.color_spaces_used
    
    @property
    def uses_spot_colors(self) -> bool:
        """별색 사용 여부"""
        return len(self.spot_colors) > 0
    
    @property
    def is_print_ready(self) -> bool:
        """인쇄 준비 상태 (CMYK만 사용)"""
        return self.uses_cmyk and not self.uses_rgb and self.max_ink_coverage <= 320
    
    @property
    def color_mode_summary(self) -> str:
        """색상 모드 요약"""
        modes = []
        if self.uses_cmyk:
            modes.append("CMYK")
        if self.uses_rgb:
            modes.append("RGB")
        if self.uses_spot_colors:
            modes.append(f"Spot({len(self.spot_colors)})")
        return " + ".join(modes) if modes else "Unknown"


@dataclass
class ImageInfo:
    """이미지 정보"""
    page: int
    width: int
    height: int
    color_space: ColorSpace
    bits_per_component: int
    filter: str  # 압축 방식
    
    # 추가 정보
    dpi_x: float = 0.0
    dpi_y: float = 0.0
    file_size: int = 0  # 바이트
    has_transparency: bool = False
    is_compressed: bool = True
    compression_ratio: float = 0.0
    
    # 위치 정보
    x: float = 0.0
    y: float = 0.0
    display_width: float = 0.0  # mm
    display_height: float = 0.0  # mm
    
    @property
    def effective_dpi(self) -> float:
        """유효 DPI (x, y 중 작은 값)"""
        if self.dpi_x > 0 and self.dpi_y > 0:
            return min(self.dpi_x, self.dpi_y)
        return max(self.dpi_x, self.dpi_y)
    
    @property
    def is_low_resolution(self) -> bool:
        """저해상도 이미지인지 (300dpi 미만)"""
        return self.effective_dpi < 300 and self.effective_dpi > 0
    
    @property
    def is_very_low_resolution(self) -> bool:
        """매우 낮은 해상도인지 (150dpi 미만)"""
        return self.effective_dpi < 150 and self.effective_dpi > 0
    
    @property
    def pixel_count(self) -> int:
        """총 픽셀 수"""
        return self.width * self.height
    
    @property
    def aspect_ratio(self) -> float:
        """가로세로 비율"""
        return self.width / self.height if self.height > 0 else 0
    
    def __str__(self) -> str:
        """문자열 표현"""
        return (f"Image on page {self.page}: {self.width}x{self.height} "
                f"@ {self.effective_dpi:.0f}dpi ({self.color_space.value})")


# ImpositionReadiness 스텁 (Phase 1에서는 기본 구조만)
@dataclass
class ImpositionReadiness:
    """판짜기 준비 상태 정보 (향후 구현)"""
    is_ready: bool = False
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # 페이지 정보
    total_pages: int = 0
    uniform_page_size: bool = True
    
    # 재단선 정보
    all_pages_have_bleed: bool = False
    minimum_bleed: float = 0.0
    
    def add_issue(self, message: str):
        """문제 추가"""
        self.issues.append(message)
        self.is_ready = False
    
    def add_warning(self, message: str):
        """경고 추가"""
        self.warnings.append(message)


@dataclass
class AnalysisResult:
    """PDF 분석 결과를 담는 종합 객체"""
    document: PDFDocument
    pages: List[PageInfo]
    fonts: Dict[str, FontInfo]
    colors: ColorInfo
    images: List[ImageInfo]
    issues: List[QualityIssue] = field(default_factory=list)
    
    # 분석 메타데이터
    analysis_duration: float = 0.0
    analyzer_version: str = "2.0"
    profile_used: str = "default"
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    # 판짜기 준비 상태 (Phase 1에서는 기본값만)
    imposition_readiness: Optional[ImpositionReadiness] = None
    
    # 추가 통계 정보
    total_fonts: int = 0
    embedded_fonts: int = 0
    total_images: int = 0
    low_res_images: int = 0
    
    def __post_init__(self):
        """생성 후 통계 계산"""
        self._calculate_statistics()
    
    def _calculate_statistics(self):
        """통계 정보 계산"""
        # 폰트 통계
        self.total_fonts = len(self.fonts)
        self.embedded_fonts = sum(1 for font in self.fonts.values() if font.is_embedded)
        
        # 이미지 통계
        self.total_images = len(self.images)
        self.low_res_images = sum(1 for img in self.images if img.is_low_resolution)
    
    @property
    def has_errors(self) -> bool:
        """오류 존재 여부"""
        return any(issue.severity == 'error' for issue in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        """경고 존재 여부"""
        return any(issue.severity == 'warning' for issue in self.issues)
    
    @property
    def error_count(self) -> int:
        """오류 개수"""
        return sum(1 for issue in self.issues if issue.severity == 'error')
    
    @property
    def warning_count(self) -> int:
        """경고 개수"""
        return sum(1 for issue in self.issues if issue.severity == 'warning')
    
    @property
    def info_count(self) -> int:
        """정보 개수"""
        return sum(1 for issue in self.issues if issue.severity == 'info')
    
    @property
    def quality_score(self) -> float:
        """
        품질 점수 계산 (0-100)
        
        점수 계산 방식:
        - 시작 점수: 100점
        - 오류당 -10점
        - 경고당 -3점
        - 정보당 -1점
        """
        if not self.issues:
            return 100.0
        
        deductions = {
            'error': 10,
            'warning': 3,
            'info': 1
        }
        
        total_deduction = sum(
            deductions.get(issue.severity, 0) 
            for issue in self.issues
        )
        
        return max(0, 100 - total_deduction)
    
    @property
    def is_imposition_ready(self) -> bool:
        """판짜기 가능 상태인지 확인"""
        if not self.imposition_readiness:
            return False
        return self.imposition_readiness.is_ready
    
    @property
    def font_embedding_rate(self) -> float:
        """폰트 임베딩 비율 (%)"""
        if self.total_fonts == 0:
            return 100.0
        return (self.embedded_fonts / self.total_fonts) * 100
    
    @property
    def has_font_issues(self) -> bool:
        """폰트 관련 이슈 존재 여부"""
        return self.embedded_fonts < self.total_fonts
    
    @property
    def has_color_issues(self) -> bool:
        """색상 관련 이슈 존재 여부"""
        return self.colors.uses_rgb or self.colors.max_ink_coverage > 320
    
    @property
    def has_image_issues(self) -> bool:
        """이미지 관련 이슈 존재 여부"""
        return self.low_res_images > 0
    
    def get_issues_by_category(self, category: str) -> List[QualityIssue]:
        """카테고리별 이슈 필터링"""
        return [issue for issue in self.issues if issue.category == category]
    
    def get_issues_by_severity(self, severity: str) -> List[QualityIssue]:
        """심각도별 이슈 필터링"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_page(self, page_number: int) -> List[QualityIssue]:
        """페이지별 이슈 필터링"""
        return [issue for issue in self.issues if page_number in issue.pages]
    
    def add_issue(self, issue: QualityIssue):
        """이슈 추가"""
        self.issues.append(issue)
    
    def get_summary(self) -> Dict[str, Any]:
        """분석 결과 요약"""
        return {
            'document': self.document.full_filename,
            'pages': self.document.page_count,
            'quality_score': self.quality_score,
            'errors': self.error_count,
            'warnings': self.warning_count,
            'fonts': {
                'total': self.total_fonts,
                'embedded': self.embedded_fonts,
                'embedding_rate': f"{self.font_embedding_rate:.1f}%"
            },
            'colors': {
                'mode': self.colors.color_mode_summary,
                'has_transparency': self.colors.has_transparency,
                'max_ink_coverage': f"{self.colors.max_ink_coverage:.0f}%"
            },
            'images': {
                'total': self.total_images,
                'low_resolution': self.low_res_images
            },
            'imposition_ready': self.is_imposition_ready,
            'analysis_time': f"{self.analysis_duration:.2f}s"
        }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return (f"AnalysisResult({self.document.full_filename}: "
                f"Score={self.quality_score:.0f}, "
                f"Errors={self.error_count}, "
                f"Warnings={self.warning_count})")