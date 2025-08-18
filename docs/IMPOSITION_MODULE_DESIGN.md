# 🖨️ PDF Quality Checker v2.0 - 판짜기(Imposition) 모듈 설계서

> **작성일**: 2025-01-11  
> **작성자**: Claude AI Assistant  
> **목적**: 인쇄업계 전문 판짜기 기능 구현을 위한 상세 설계

---

## 📋 목차
1. [개요](#1-개요)
2. [기능 요구사항](#2-기능-요구사항)
3. [시스템 설계](#3-시스템-설계)
4. [구현 명세](#4-구현-명세)
5. [UI/UX 설계](#5-uiux-설계)
6. [기술적 고려사항](#6-기술적-고려사항)
7. [구현 로드맵](#7-구현-로드맵)

---

## 1. 개요

### 1.1 판짜기(Imposition)란?
인쇄 공정에서 여러 페이지를 하나의 큰 용지에 효율적으로 배치하는 작업입니다. 
이를 통해 인쇄 비용을 절감하고 생산 효율을 높일 수 있습니다.

### 1.2 핵심 가치
- **비용 절감**: 용지 사용량 최소화
- **생산성 향상**: 자동화된 레이아웃 생성
- **품질 보장**: 정확한 재단선과 여백 설정
- **유연성**: 다양한 인쇄 방식 지원

---

## 2. 기능 요구사항

### 2.1 기본 기능

#### 2.1.1 N-up 레이아웃
```python
# 2-up, 4-up, 8-up, 16-up 등 지원
def create_nup_layout(
    input_pdf: Path,
    n: int,  # 페이지 수 (2, 4, 8, 16 등)
    sheet_size: Tuple[float, float],  # 용지 크기 (mm)
    orientation: str = 'portrait'  # 방향
) -> Path:
    """N개 페이지를 한 장에 배치"""
```

#### 2.1.2 중철 제본 (Saddle Stitch)
```python
def create_saddle_stitch(
    input_pdf: Path,
    signature_pages: int = 4,  # 한 묶음당 페이지 수
    creep_adjustment: float = 0  # 크리프 보정값
) -> Path:
    """중철 제본용 레이아웃 생성"""
```

#### 2.1.3 무선철 제본 (Perfect Binding)
```python
def create_perfect_binding(
    input_pdf: Path,
    signature_pages: int = 16,  # 시그니처 페이지 수
    spine_width: float = 0  # 책등 두께
) -> Path:
    """무선철 제본용 레이아웃 생성"""
```

### 2.2 고급 기능

#### 2.2.1 재단선 및 표시
```python
@dataclass
class CropMarks:
    """재단선 설정"""
    enabled: bool = True
    length: float = 10.0  # mm
    offset: float = 3.0  # mm
    stroke_width: float = 0.25  # pt
    color: str = 'Registration'  # 레지스트레이션 색상

@dataclass
class RegistrationMarks:
    """맞춤 표시"""
    enabled: bool = True
    style: str = 'cross'  # cross, circle, target
    size: float = 5.0  # mm
    
@dataclass
class ColorBars:
    """색상 바"""
    enabled: bool = True
    type: str = 'CMYK'  # CMYK, Grayscale, Custom
    position: str = 'bottom'  # top, bottom, left, right
```

#### 2.2.2 여백 및 블리드
```python
@dataclass
class BleedSettings:
    """블리드 설정"""
    top: float = 3.0  # mm
    bottom: float = 3.0
    left: float = 3.0
    right: float = 3.0
    
@dataclass
class MarginsSettings:
    """여백 설정"""
    top: float = 10.0
    bottom: float = 10.0
    left: float = 10.0
    right: float = 10.0
    gutter: float = 0  # 제본 여백
```

### 2.3 특수 레이아웃

#### 2.3.1 명함 레이아웃
```python
def create_business_card_layout(
    input_pdf: Path,
    cards_per_sheet: Tuple[int, int] = (3, 3),  # 가로x세로
    card_size: Tuple[float, float] = (90, 50),  # mm
    spacing: float = 2.0  # 카드 간격
) -> Path:
    """명함 다면 레이아웃"""
```

#### 2.3.2 라벨/스티커 레이아웃
```python
def create_label_layout(
    input_pdf: Path,
    label_template: str,  # 템플릿 ID (예: 'Avery5160')
    custom_size: Optional[Tuple[float, float]] = None
) -> Path:
    """라벨/스티커 레이아웃"""
```

---

## 3. 시스템 설계

### 3.1 아키텍처

```
src/
└── core/
    └── imposition/
        ├── __init__.py
        ├── imposition_engine.py    # 메인 엔진
        ├── layout_calculator.py     # 레이아웃 계산
        ├── mark_generator.py        # 인쇄 표시 생성
        ├── page_arranger.py         # 페이지 배치
        ├── templates/               # 레이아웃 템플릿
        │   ├── nup_templates.py
        │   ├── booklet_templates.py
        │   └── label_templates.py
        └── utils/
            ├── geometry.py          # 기하학 계산
            └── units.py             # 단위 변환
```

### 3.2 클래스 다이어그램

```python
class ImpositionEngine:
    """판짜기 엔진 메인 클래스"""
    
    def __init__(self):
        self.layout_calculator = LayoutCalculator()
        self.mark_generator = MarkGenerator()
        self.page_arranger = PageArranger()
        
    def process(self, 
                input_pdf: Path,
                layout_config: LayoutConfig) -> Path:
        """판짜기 처리 실행"""
        
class LayoutCalculator:
    """레이아웃 계산기"""
    
    def calculate_nup(self, n: int, sheet_size: Size) -> Layout:
        """N-up 레이아웃 계산"""
        
    def calculate_booklet(self, page_count: int) -> Layout:
        """북렛 레이아웃 계산"""
        
class MarkGenerator:
    """인쇄 표시 생성기"""
    
    def add_crop_marks(self, page: Page, settings: CropMarks):
        """재단선 추가"""
        
    def add_registration_marks(self, page: Page):
        """맞춤 표시 추가"""
        
    def add_color_bars(self, page: Page):
        """색상 바 추가"""
```

---

## 4. 구현 명세

### 4.1 핵심 알고리즘

#### 4.1.1 N-up 레이아웃 계산
```python
def calculate_nup_layout(n: int, sheet_size: Size, page_size: Size) -> Layout:
    """
    N-up 레이아웃 최적 배치 계산
    
    알고리즘:
    1. 가능한 모든 행/열 조합 계산
    2. 각 조합에 대해 스케일 팩터 계산
    3. 용지 활용률이 최대인 조합 선택
    4. 페이지 위치와 변환 매트릭스 계산
    """
    best_layout = None
    max_utilization = 0
    
    for rows, cols in get_possible_arrangements(n):
        # 페이지당 할당 공간 계산
        cell_width = sheet_size.width / cols
        cell_height = sheet_size.height / rows
        
        # 스케일 팩터 계산
        scale_x = cell_width / page_size.width
        scale_y = cell_height / page_size.height
        scale = min(scale_x, scale_y)
        
        # 용지 활용률 계산
        utilization = (scale * page_size.width * scale * page_size.height * n) / \
                     (sheet_size.width * sheet_size.height)
        
        if utilization > max_utilization:
            max_utilization = utilization
            best_layout = Layout(rows, cols, scale)
            
    return best_layout
```

#### 4.1.2 중철 제본 페이지 순서
```python
def calculate_saddle_stitch_order(total_pages: int) -> List[int]:
    """
    중철 제본용 페이지 순서 계산
    
    예: 8페이지 문서
    출력: [8, 1, 2, 7, 6, 3, 4, 5]
    """
    # 4의 배수로 맞추기
    pages_needed = ((total_pages + 3) // 4) * 4
    order = []
    
    for signature in range(pages_needed // 4):
        start = signature * 4
        # 앞면
        order.append(pages_needed - start)      # 뒷페이지
        order.append(start + 1)                 # 앞페이지
        # 뒷면
        order.append(start + 2)                 # 안쪽 좌
        order.append(pages_needed - start - 1)  # 안쪽 우
        
    return order
```

### 4.2 외부 도구 통합

#### 4.2.1 pdftk 활용
```python
def merge_pages_with_pdftk(pages: List[Path], output: Path):
    """pdftk를 사용한 페이지 병합"""
    cmd = ['pdftk'] + [str(p) for p in pages] + ['cat', 'output', str(output)]
    subprocess.run(cmd, check=True)
```

#### 4.2.2 pdfnup 활용
```python
def create_nup_with_pdfnup(input_pdf: Path, n: int, output: Path):
    """pdfnup을 사용한 N-up 생성"""
    cmd = [
        'pdfnup',
        '--nup', f'{n}',
        '--paper', 'a3paper',
        '--frame', 'true',
        '--delta', '5mm 5mm',
        '--offset', '0mm 0mm',
        input_pdf,
        '-o', output
    ]
    subprocess.run(cmd, check=True)
```

---

## 5. UI/UX 설계

### 5.1 판짜기 설정 다이얼로그

```python
class ImpositionDialog(ctk.CTkToplevel):
    """판짜기 설정 다이얼로그"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("판짜기 설정")
        self.geometry("800x600")
        
        # 레이아웃 선택
        self.layout_type = ctk.StringVar(value="nup")
        
        # 탭 구성
        self.tabview = ctk.CTkTabview(self)
        self.tabview.add("기본 설정")
        self.tabview.add("레이아웃")
        self.tabview.add("인쇄 표시")
        self.tabview.add("미리보기")
```

### 5.2 실시간 미리보기

```python
class ImpositionPreview(ctk.CTkCanvas):
    """판짜기 미리보기"""
    
    def update_preview(self, layout: Layout):
        """레이아웃 미리보기 업데이트"""
        self.delete("all")
        
        # 용지 그리기
        self.draw_sheet()
        
        # 페이지 배치 그리기
        for page in layout.pages:
            self.draw_page(page)
            
        # 재단선 그리기
        if layout.crop_marks_enabled:
            self.draw_crop_marks()
```

---

## 6. 기술적 고려사항

### 6.1 성능 최적화
- **메모리 관리**: 대용량 PDF 처리 시 스트리밍 방식 사용
- **병렬 처리**: 멀티 코어 활용한 페이지 처리
- **캐싱**: 자주 사용되는 레이아웃 템플릿 캐싱

### 6.2 정확도 보장
- **단위 변환**: mm, inch, point 간 정확한 변환
- **색상 관리**: CMYK 색상 공간 유지
- **해상도**: 고해상도 출력 지원 (최소 300 DPI)

### 6.3 호환성
- **PDF 버전**: PDF/X-1a, PDF/X-4 준수
- **폰트 처리**: 모든 폰트 임베딩 또는 아웃라인 변환
- **이미지 처리**: 고해상도 이미지 유지

---

## 7. 구현 로드맵

### Phase 1: 기본 구조 (1주)
- [ ] ImpositionEngine 클래스 구현
- [ ] 기본 N-up 레이아웃 구현
- [ ] 단위 변환 유틸리티

### Phase 2: 핵심 기능 (2주)
- [ ] 중철/무선철 레이아웃
- [ ] 재단선 및 인쇄 표시
- [ ] 여백 및 블리드 처리

### Phase 3: UI 통합 (1주)
- [ ] 설정 다이얼로그 구현
- [ ] 실시간 미리보기
- [ ] 프로파일 저장/불러오기

### Phase 4: 고급 기능 (2주)
- [ ] 명함/라벨 레이아웃
- [ ] 크리프 보정
- [ ] 가변 데이터 처리

### Phase 5: 최적화 및 테스트 (1주)
- [ ] 성능 최적화
- [ ] 단위 테스트
- [ ] 통합 테스트

---

## 📎 부록

### A. 참고 자료
- ISO 12635: Graphic technology - Plates for offset printing
- PDF/X 표준 문서
- 인쇄 업계 표준 용지 크기

### B. 용어 정의
- **Imposition**: 판짜기, 여러 페이지를 한 장에 배치
- **Signature**: 시그니처, 접어서 제본하는 용지 단위
- **Creep**: 크리프, 중철 제본 시 페이지 밀림 현상
- **Gutter**: 제본 여백
- **Registration Mark**: 맞춤 표시, 색판 정렬용 표시

### C. 샘플 코드

```python
# 간단한 2-up 레이아웃 예제
from src.core.imposition import ImpositionEngine

engine = ImpositionEngine()
result = engine.create_nup(
    input_pdf="document.pdf",
    n=2,
    sheet_size=(420, 297),  # A3
    orientation="landscape",
    crop_marks=True,
    bleed=3.0
)
print(f"판짜기 완료: {result}")
```

---

*이 문서는 PDF Quality Checker v2.0의 판짜기 모듈 구현을 위한 상세 설계서입니다.*