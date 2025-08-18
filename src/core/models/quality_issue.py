"""
PDF 품질 이슈 모델 - PDF 검사 중 발견된 문제를 표현하는 객체

이 모듈은 PDF 파일 검사 과정에서 발견되는 다양한 품질 문제들을
체계적이고 일관된 방식으로 표현합니다.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class IssueSeverity(Enum):
    """이슈 심각도 레벨"""
    ERROR = "error"       # 인쇄 불가능하거나 심각한 문제
    WARNING = "warning"   # 품질 저하 가능성이 있는 문제
    INFO = "info"        # 정보성 알림
    SUCCESS = "success"  # 긍정적인 확인 사항
    
    @property
    def emoji(self) -> str:
        """심각도별 이모지"""
        emojis = {
            self.ERROR: "❌",
            self.WARNING: "⚠️",
            self.INFO: "ℹ️",
            self.SUCCESS: "✅"
        }
        return emojis.get(self, "")
    
    @property
    def priority(self) -> int:
        """정렬용 우선순위 (낮을수록 중요)"""
        priorities = {
            self.ERROR: 1,
            self.WARNING: 2,
            self.INFO: 3,
            self.SUCCESS: 4
        }
        return priorities.get(self, 99)


class IssueCategory(Enum):
    """이슈 카테고리"""
    # 폰트 관련
    FONT_EMBEDDING = "font_embedding"
    FONT_TYPE = "font_type"
    FONT_ENCODING = "font_encoding"
    TEXT_SIZE = "text_size"
    
    # 색상 관련
    COLOR_SPACE = "color_space"
    INK_COVERAGE = "ink_coverage"
    SPOT_COLOR = "spot_color"
    TRANSPARENCY = "transparency"
    OVERPRINT = "overprint"
    
    # 이미지 관련
    IMAGE_RESOLUTION = "image_resolution"
    IMAGE_COMPRESSION = "image_compression"
    IMAGE_FORMAT = "image_format"
    IMAGE_COLOR = "image_color"
    
    # 페이지 관련
    PAGE_SIZE = "page_size"
    PAGE_BLEED = "page_bleed"
    PAGE_MARGIN = "page_margin"
    PAGE_ROTATION = "page_rotation"
    
    # 문서 관련
    PDF_VERSION = "pdf_version"
    PDF_ENCRYPTION = "pdf_encryption"
    PDF_SIGNATURE = "pdf_signature"
    METADATA = "metadata"
    
    # 인쇄 관련
    PRINT_MARKS = "print_marks"
    TRAP = "trap"
    HALFTONE = "halftone"
    
    # 기타
    GENERAL = "general"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"
    
    @property
    def display_name(self) -> str:
        """사용자 친화적인 표시 이름"""
        names = {
            self.FONT_EMBEDDING: "폰트 임베딩",
            self.FONT_TYPE: "폰트 타입",
            self.FONT_ENCODING: "폰트 인코딩",
            self.TEXT_SIZE: "텍스트 크기",
            self.COLOR_SPACE: "색상 공간",
            self.INK_COVERAGE: "잉크량",
            self.SPOT_COLOR: "별색",
            self.TRANSPARENCY: "투명도",
            self.OVERPRINT: "오버프린트",
            self.IMAGE_RESOLUTION: "이미지 해상도",
            self.IMAGE_COMPRESSION: "이미지 압축",
            self.IMAGE_FORMAT: "이미지 형식",
            self.IMAGE_COLOR: "이미지 색상",
            self.PAGE_SIZE: "페이지 크기",
            self.PAGE_BLEED: "재단선",
            self.PAGE_MARGIN: "여백",
            self.PAGE_ROTATION: "페이지 회전",
            self.PDF_VERSION: "PDF 버전",
            self.PDF_ENCRYPTION: "PDF 암호화",
            self.PDF_SIGNATURE: "PDF 서명",
            self.METADATA: "메타데이터",
            self.PRINT_MARKS: "인쇄 마크",
            self.TRAP: "트랩",
            self.HALFTONE: "하프톤",
            self.GENERAL: "일반",
            self.PERFORMANCE: "성능",
            self.COMPATIBILITY: "호환성"
        }
        return names.get(self, self.value)


@dataclass
class FixOption:
    """자동 수정 옵션"""
    method: str  # 수정 방법 식별자 (예: "convert_rgb_to_cmyk")
    description: str  # 수정 방법 설명
    parameters: Dict[str, Any] = field(default_factory=dict)  # 수정에 필요한 매개변수
    estimated_time: float = 0.0  # 예상 소요 시간 (초)
    risk_level: str = "low"  # low, medium, high
    
    @property
    def is_safe(self) -> bool:
        """안전한 수정인지 확인"""
        return self.risk_level == "low"


@dataclass
class QualityIssue:
    """PDF 품질 이슈"""
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    pages: List[int] = field(default_factory=list)  # 영향받는 페이지 번호 (빈 리스트는 전체 문서)
    
    # 추가 정보
    details: Dict[str, Any] = field(default_factory=dict)  # 상세 정보
    fix_options: List[FixOption] = field(default_factory=list)  # 가능한 수정 방법
    detected_at: datetime = field(default_factory=datetime.now)  # 검출 시간
    
    # 위치 정보 (옵션)
    location: Optional[Dict[str, Any]] = None  # 페이지 내 위치 정보
    
    # 관련 객체 정보
    related_objects: List[str] = field(default_factory=list)  # 관련 폰트명, 이미지 ID 등
    
    def __post_init__(self):
        """생성 후 처리"""
        # severity와 category를 Enum으로 변환
        if isinstance(self.severity, str):
            self.severity = IssueSeverity(self.severity)
        if isinstance(self.category, str):
            self.category = IssueCategory(self.category)
    
    @property
    def is_fixable(self) -> bool:
        """자동 수정 가능 여부"""
        return len(self.fix_options) > 0
    
    @property
    def safe_fix_available(self) -> bool:
        """안전한 자동 수정 가능 여부"""
        return any(fix.is_safe for fix in self.fix_options)
    
    @property
    def pages_affected(self) -> int:
        """영향받는 페이지 수"""
        return len(self.pages) if self.pages else -1  # -1은 전체 문서
    
    @property
    def page_range_str(self) -> str:
        """페이지 범위 문자열"""
        if not self.pages:
            return "전체 문서"
        elif len(self.pages) == 1:
            return f"페이지 {self.pages[0]}"
        elif len(self.pages) <= 5:
            return f"페이지 {', '.join(map(str, sorted(self.pages)))}"
        else:
            sorted_pages = sorted(self.pages)
            return f"페이지 {sorted_pages[0]}-{sorted_pages[-1]} ({len(self.pages)}개)"
    
    @property
    def full_description(self) -> str:
        """상세 설명 (details 포함)"""
        desc = self.description
        
        # details에서 추가 정보 추출
        if self.details:
            detail_parts = []
            for key, value in self.details.items():
                if key == 'count':
                    detail_parts.append(f"{value}개 발견")
                elif key == 'names':
                    if isinstance(value, list) and len(value) <= 3:
                        detail_parts.append(f"대상: {', '.join(value)}")
                    elif isinstance(value, list):
                        detail_parts.append(f"대상: {', '.join(value[:3])} 외 {len(value)-3}개")
                elif key == 'resolution':
                    detail_parts.append(f"해상도: {value}dpi")
                elif key == 'coverage':
                    detail_parts.append(f"잉크량: {value}%")
            
            if detail_parts:
                desc += f" ({', '.join(detail_parts)})"
        
        return desc
    
    def add_fix_option(self, method: str, description: str, **kwargs):
        """수정 옵션 추가 헬퍼 메서드"""
        fix = FixOption(
            method=method,
            description=description,
            parameters=kwargs.get('parameters', {}),
            estimated_time=kwargs.get('estimated_time', 0.0),
            risk_level=kwargs.get('risk_level', 'low')
        )
        self.fix_options.append(fix)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (JSON 직렬화용)"""
        return {
            'category': self.category.value,
            'category_display': self.category.display_name,
            'severity': self.severity.value,
            'severity_emoji': self.severity.emoji,
            'title': self.title,
            'description': self.description,
            'full_description': self.full_description,
            'pages': self.pages,
            'page_range': self.page_range_str,
            'details': self.details,
            'is_fixable': self.is_fixable,
            'fix_options': [
                {
                    'method': fix.method,
                    'description': fix.description,
                    'risk_level': fix.risk_level
                }
                for fix in self.fix_options
            ],
            'detected_at': self.detected_at.isoformat(),
            'related_objects': self.related_objects
        }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"{self.severity.emoji} [{self.category.display_name}] {self.title}"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return (f"QualityIssue(category={self.category.value}, "
                f"severity={self.severity.value}, "
                f"title='{self.title}', "
                f"pages={self.pages})")
    
    def __lt__(self, other: 'QualityIssue') -> bool:
        """정렬을 위한 비교 (심각도 우선, 그 다음 카테고리)"""
        if self.severity.priority != other.severity.priority:
            return self.severity.priority < other.severity.priority
        return self.category.value < other.category.value


# 미리 정의된 일반적인 이슈들을 생성하는 팩토리 함수들

def create_font_not_embedded_issue(font_name: str, pages: List[int]) -> QualityIssue:
    """폰트 미임베딩 이슈 생성"""
    return QualityIssue(
        category=IssueCategory.FONT_EMBEDDING,
        severity=IssueSeverity.ERROR,
        title="폰트가 임베딩되지 않음",
        description=f"'{font_name}' 폰트가 PDF에 임베딩되지 않았습니다. 다른 시스템에서 글꼴이 변경될 수 있습니다.",
        pages=pages,
        details={'font_name': font_name},
        fix_options=[
            FixOption(
                method="embed_font",
                description="폰트를 PDF에 임베딩",
                risk_level="low"
            ),
            FixOption(
                method="outline_text",
                description="텍스트를 아웃라인으로 변환",
                risk_level="medium"
            )
        ],
        related_objects=[font_name]
    )


def create_rgb_color_issue(page_count: int) -> QualityIssue:
    """RGB 색상 사용 이슈 생성"""
    return QualityIssue(
        category=IssueCategory.COLOR_SPACE,
        severity=IssueSeverity.WARNING,
        title="RGB 색상 공간 사용",
        description="인쇄용 PDF에는 CMYK 색상을 사용해야 합니다. RGB 색상이 발견되었습니다.",
        pages=[],  # 전체 문서
        details={'count': page_count},
        fix_options=[
            FixOption(
                method="convert_rgb_to_cmyk",
                description="RGB를 CMYK로 변환",
                parameters={'profile': 'ISO Coated v2'},
                risk_level="low"
            )
        ]
    )


def create_low_resolution_image_issue(page: int, resolution: float) -> QualityIssue:
    """저해상도 이미지 이슈 생성"""
    severity = IssueSeverity.ERROR if resolution < 150 else IssueSeverity.WARNING
    
    return QualityIssue(
        category=IssueCategory.IMAGE_RESOLUTION,
        severity=severity,
        title="저해상도 이미지",
        description=f"이미지 해상도가 {resolution:.0f}dpi로 인쇄 품질 기준(300dpi)보다 낮습니다.",
        pages=[page],
        details={'resolution': resolution},
        fix_options=[
            FixOption(
                method="resample_image",
                description="이미지 리샘플링 (품질 손실 가능)",
                parameters={'target_dpi': 300},
                risk_level="high"
            )
        ]
    )


def create_high_ink_coverage_issue(page: int, coverage: float) -> QualityIssue:
    """높은 잉크량 이슈 생성"""
    severity = IssueSeverity.ERROR if coverage > 340 else IssueSeverity.WARNING
    
    return QualityIssue(
        category=IssueCategory.INK_COVERAGE,
        severity=severity,
        title="과도한 잉크량",
        description=f"총 잉크량이 {coverage:.0f}%로 권장 기준(320%)을 초과합니다. 인쇄 시 번짐이 발생할 수 있습니다.",
        pages=[page],
        details={'coverage': coverage},
        fix_options=[
            FixOption(
                method="reduce_ink_coverage",
                description="잉크량 감소 (GCR/UCR 적용)",
                parameters={'target_coverage': 300},
                risk_level="medium"
            )
        ]
    )


def create_missing_bleed_issue(pages: List[int]) -> QualityIssue:
    """재단선 누락 이슈 생성"""
    return QualityIssue(
        category=IssueCategory.PAGE_BLEED,
        severity=IssueSeverity.WARNING,
        title="재단선 누락",
        description="재단선(Bleed)이 없거나 부족합니다. 재단 시 흰 여백이 생길 수 있습니다.",
        pages=pages,
        details={'required_bleed': 3.0},
        fix_options=[
            FixOption(
                method="add_bleed",
                description="재단선 추가 (컨텐츠 확장)",
                parameters={'bleed_size': 3.0},
                risk_level="high"
            )
        ]
    )