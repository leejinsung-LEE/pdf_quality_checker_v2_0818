"""
PDF 문서 모델 - PDF 파일의 핵심 정보를 담는 불변 객체

이 모듈은 PDF 문서의 메타데이터와 기본 정보를 관리합니다.
판짜기(Imposition) 기능을 위한 준비 정보도 포함되어 있습니다.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib
from enum import Enum


class PaperSize(Enum):
    """표준 용지 크기 정의"""
    A0 = (841.0, 1189.0)
    A1 = (594.0, 841.0)
    A2 = (420.0, 594.0)
    A3 = (297.0, 420.0)
    A4 = (210.0, 297.0)
    A5 = (148.0, 210.0)
    A6 = (105.0, 148.0)
    LETTER = (215.9, 279.4)
    LEGAL = (215.9, 355.6)
    TABLOID = (279.4, 431.8)
    CUSTOM = (0.0, 0.0)
    
    @classmethod
    def from_dimensions(cls, width_mm: float, height_mm: float, tolerance: float = 2.0) -> 'PaperSize':
        """
        주어진 크기에 해당하는 용지 규격 찾기
        
        Args:
            width_mm: 너비 (mm)
            height_mm: 높이 (mm)
            tolerance: 허용 오차 (mm)
            
        Returns:
            PaperSize: 매칭되는 용지 규격 또는 CUSTOM
        """
        # 가로/세로 모두 확인 (회전된 경우 고려)
        for paper_size in cls:
            if paper_size == cls.CUSTOM:
                continue
                
            std_width, std_height = paper_size.value
            
            # 정방향 확인
            if (abs(width_mm - std_width) <= tolerance and 
                abs(height_mm - std_height) <= tolerance):
                return paper_size
            
            # 회전된 방향 확인
            if (abs(width_mm - std_height) <= tolerance and 
                abs(height_mm - std_width) <= tolerance):
                return paper_size
                
        return cls.CUSTOM


@dataclass
class Rectangle:
    """사각형 영역 정의 (판짜기용)"""
    x: float
    y: float
    width: float
    height: float
    
    def contains(self, other: 'Rectangle') -> bool:
        """다른 사각형을 포함하는지 확인"""
        return (self.x <= other.x and 
                self.y <= other.y and
                self.x + self.width >= other.x + other.width and
                self.y + self.height >= other.y + other.height)
    
    def intersects(self, other: 'Rectangle') -> bool:
        """다른 사각형과 교차하는지 확인"""
        return not (self.x + self.width < other.x or 
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or
                   other.y + other.height < self.y)
    
    @property
    def area(self) -> float:
        """사각형 넓이"""
        return self.width * self.height


@dataclass
class PageSize:
    """페이지 크기 정보"""
    width_mm: float
    height_mm: float
    name: str = "Custom"
    
    def __post_init__(self):
        """생성 후 처리 - 표준 용지 크기 자동 판별"""
        if self.name == "Custom":
            paper_size = PaperSize.from_dimensions(self.width_mm, self.height_mm)
            if paper_size != PaperSize.CUSTOM:
                self.name = paper_size.name
    
    def __eq__(self, other):
        """크기 비교 (1mm 오차 허용)"""
        if not isinstance(other, PageSize):
            return False
        return (abs(self.width_mm - other.width_mm) < 1 and 
                abs(self.height_mm - other.height_mm) < 1)
    
    def __hash__(self):
        """해시 값 생성 (딕셔너리 키로 사용 가능하게)"""
        # 1mm 단위로 반올림하여 해시 생성
        return hash((round(self.width_mm), round(self.height_mm), self.name))
    
    def __repr__(self):
        """개발자용 표현"""
        return f"PageSize(width={self.width_mm}, height={self.height_mm}, name='{self.name}')"
    
    @property
    def orientation(self) -> str:
        """페이지 방향 (portrait/landscape)"""
        return "portrait" if self.height_mm > self.width_mm else "landscape"
    
    def rotated(self) -> 'PageSize':
        """90도 회전된 크기 반환"""
        return PageSize(self.height_mm, self.width_mm, self.name)


@dataclass
class BleedInfo:
    """재단선(Bleed) 정보"""
    top: float = 0.0
    bottom: float = 0.0
    left: float = 0.0
    right: float = 0.0
    
    @property
    def has_proper_bleed(self) -> bool:
        """표준 재단선(3mm 이상) 확인"""
        return all(value >= 3.0 for value in [self.top, self.bottom, self.left, self.right])
    
    @property
    def is_uniform(self) -> bool:
        """모든 방향의 재단선이 동일한지"""
        return len(set([self.top, self.bottom, self.left, self.right])) == 1
    
    @property
    def minimum(self) -> float:
        """가장 작은 재단선 값"""
        return min(self.top, self.bottom, self.left, self.right)
    
    @property
    def average(self) -> float:
        """평균 재단선 값"""
        return (self.top + self.bottom + self.left + self.right) / 4
    
    def __str__(self) -> str:
        """문자열 표현"""
        if self.is_uniform:
            return f"{self.top:.1f}mm (uniform)"
        return f"T:{self.top:.1f} B:{self.bottom:.1f} L:{self.left:.1f} R:{self.right:.1f}mm"


@dataclass
class PageInfo:
    """개별 페이지 정보"""
    page_number: int
    width_mm: float
    height_mm: float
    rotation: int = 0
    has_transparency: bool = False
    has_overprint: bool = False
    bleed_info: Optional[BleedInfo] = None
    
    # 판짜기 관련 정보
    content_bounds: Optional[Rectangle] = None  # 실제 컨텐츠가 있는 영역
    can_be_rotated: bool = True  # 판짜기 시 회전 가능 여부
    
    @property
    def page_size(self) -> PageSize:
        """페이지 크기 객체"""
        return PageSize(self.width_mm, self.height_mm)
    
    @property
    def paper_size(self) -> str:
        """용지 규격 판별 (A4, A3 등)"""
        return self.page_size.name
    
    @property
    def orientation(self) -> str:
        """페이지 방향 (portrait/landscape)"""
        return self.page_size.orientation
    
    @property
    def effective_rotation(self) -> int:
        """유효 회전 각도 (0, 90, 180, 270)"""
        return self.rotation % 360
    
    def get_rotated_size(self) -> Tuple[float, float]:
        """회전을 고려한 실제 크기"""
        if self.effective_rotation in (90, 270):
            return (self.height_mm, self.width_mm)
        return (self.width_mm, self.height_mm)


@dataclass
class PDFDocument:
    """PDF 문서의 핵심 정보를 담는 불변 객체"""
    path: Path
    file_hash: str
    file_size: int
    created_at: datetime
    
    # 분석 후 추가되는 정보
    page_count: int = 0
    pdf_version: str = ""
    is_encrypted: bool = False
    is_signed: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # 페이지 정보
    pages: List[PageInfo] = field(default_factory=list)
    
    # 판짜기 관련 준비 정보
    is_uniform_size: bool = True  # 모든 페이지가 같은 크기인지
    dominant_page_size: Optional[PageSize] = None  # 가장 많이 사용된 페이지 크기
    size_variations: List[PageSize] = field(default_factory=list)  # 사용된 모든 크기
    
    def __post_init__(self):
        """생성 시 유효성 검증"""
        if not isinstance(self.path, Path):
            self.path = Path(self.path)
            
        if not self.path.exists():
            raise ValueError(f"PDF 파일이 존재하지 않습니다: {self.path}")
            
        if not self.path.suffix.lower() == '.pdf':
            raise ValueError(f"PDF 파일이 아닙니다: {self.path}")
    
    @classmethod
    def from_path(cls, pdf_path: str | Path) -> 'PDFDocument':
        """파일 경로로부터 PDFDocument 객체 생성"""
        path = Path(pdf_path) if isinstance(pdf_path, str) else pdf_path
        
        # 파일 해시 계산
        file_hash = cls._calculate_file_hash(path)
        
        # 파일 정보 수집
        stat = path.stat()
        file_size = stat.st_size
        created_at = datetime.fromtimestamp(stat.st_ctime)
        
        return cls(
            path=path,
            file_hash=file_hash,
            file_size=file_size,
            created_at=created_at
        )
    
    @staticmethod
    def _calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
        """파일의 SHA256 해시 계산"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256_hash.update(chunk)
                
        return sha256_hash.hexdigest()
    
    def add_page_info(self, page_info: PageInfo):
        """페이지 정보 추가 및 통계 업데이트"""
        self.pages.append(page_info)
        self.page_count = len(self.pages)
        
        # 페이지 크기 통계 업데이트
        self._update_size_statistics()
    
    def _update_size_statistics(self):
        """페이지 크기 통계 업데이트"""
        if not self.pages:
            return
            
        # 모든 페이지 크기 수집
        size_counts: Dict[PageSize, int] = {}
        
        for page in self.pages:
            page_size = page.page_size
            
            # 동일한 크기 찾기 (1mm 오차 허용)
            found = False
            for existing_size in size_counts:
                if existing_size == page_size:
                    size_counts[existing_size] += 1
                    found = True
                    break
                    
            if not found:
                size_counts[page_size] = 1
        
        # 통계 계산
        self.size_variations = list(size_counts.keys())
        self.is_uniform_size = len(self.size_variations) == 1
        
        # 가장 많이 사용된 크기
        if size_counts:
            self.dominant_page_size = max(size_counts.items(), key=lambda x: x[1])[0]
    
    @property
    def filename(self) -> str:
        """파일명 (확장자 제외)"""
        return self.path.stem
    
    @property
    def full_filename(self) -> str:
        """파일명 (확장자 포함)"""
        return self.path.name
    
    @property
    def file_size_mb(self) -> float:
        """파일 크기 (MB)"""
        return self.file_size / (1024 * 1024)
    
    @property
    def has_mixed_orientations(self) -> bool:
        """혼합된 페이지 방향이 있는지"""
        if not self.pages:
            return False
            
        orientations = {page.orientation for page in self.pages}
        return len(orientations) > 1
    
    @property
    def has_proper_bleed_all_pages(self) -> bool:
        """모든 페이지가 적절한 재단선을 가지고 있는지"""
        if not self.pages:
            return False
            
        return all(
            page.bleed_info and page.bleed_info.has_proper_bleed 
            for page in self.pages
        )
    
    def get_page_size_summary(self) -> str:
        """페이지 크기 요약 문자열"""
        if self.is_uniform_size and self.dominant_page_size:
            return f"{self.dominant_page_size.name} ({self.dominant_page_size.width_mm:.1f}×{self.dominant_page_size.height_mm:.1f}mm)"
        else:
            return f"Mixed sizes ({len(self.size_variations)} variations)"
    
    def __str__(self) -> str:
        """문자열 표현"""
        return (f"PDFDocument('{self.full_filename}', "
                f"{self.page_count} pages, "
                f"{self.file_size_mb:.1f}MB, "
                f"{self.get_page_size_summary()})")
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return (f"PDFDocument(path={self.path!r}, "
                f"page_count={self.page_count}, "
                f"file_size={self.file_size})")