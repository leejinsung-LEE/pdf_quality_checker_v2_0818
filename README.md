# PDF Quality Checker v2.1

> **인쇄용 PDF 파일의 품질을 자동으로 검사하고 수정하는 통합 시스템**  
> **버전**: 2.1.0 | **상태**: ✅ 100% 구현 완료 | **최종 업데이트**: 2025-01-11

---

## 🎉 최신 업데이트 (v2.1.0) - 대규모 기능 업데이트

### 🆕 새로운 핵심 기능 (6개)
1. **SQLite 기반 작업 이력 관리**: JSON에서 SQLite로 업그레이드, 고급 검색 및 통계
2. **통계 대시보드**: 일/주/월별 처리 통계, 타임라인 차트, 품질 분석
3. **배치 스케줄러**: Cron-like 자동 실행, 다양한 주기 설정
4. **백업/롤백 시스템**: 자동 백업, ZIP 압축, 버전 관리, 무결성 검증
5. **프로파일 가져오기/내보내기**: JSON 형식, 프로파일 공유 지원
6. **프로파일 상세 설정 UI**: 탭 기반 설정, 실시간 미리보기, 프로파일 상속

### 이전 업데이트 (v2.0.2)
- **성능**: 시작 속도 71% 개선, 메모리 50% 감소, 배치 처리 30% 향상
- **안정성**: 알람 시스템 개선, 워커 풀 오류 수정, 인코딩 문제 해결
- **사용성**: 드래그앤드롭 UX 강화, 설정 자동 저장, 향상된 오류 처리

---

## 📋 목차
- [주요 기능](#-주요-기능)
- [시스템 아키텍처](#-시스템-아키텍처)
- [설치 방법](#-설치-방법)
- [사용법](#-사용법)
- [프로젝트 구조](#-프로젝트-구조)
- [기술 스택](#-기술-스택)
- [품질 검사 기준](#-품질-검사-기준)
- [개발 가이드](#-개발-가이드)
- [로드맵](#-로드맵)

---

## 🎯 주요 기능

### 1. PDF 종합 분석
- **메타데이터 분석**: 문서 정보, 생성일, 수정일, 작성자
- **페이지 분석**: 크기, 방향, 재단선(Bleed), 미디어박스
- **폰트 분석**: 임베딩 상태, Type3 폰트, 누락 폰트 검출
- **색상 분석**: RGB/CMYK/별색, 투명도, 오버프린트, 잉크 커버리지
- **이미지 분석**: 해상도(DPI), 압축률, 색상 모드

### 2. 품질 검사 및 점수 산정
- **품질 점수**: 0-100점 자동 계산
- **인쇄 적합성 평가**: Critical/Warning/Info 레벨 이슈 분류
- **5개 전문 체커**: ColorChecker, FontChecker, ImageChecker, BleedChecker, MetadataChecker
- **커스텀 프로파일**: quick/default/strict 프리셋 제공

### 3. 자동 수정 기능
- **RGB→CMYK 변환**: Ghostscript 활용 자동 변환
- **폰트 처리**: 임베딩 또는 아웃라인 변환
- **이미지 최적화**: 해상도 조정, 압축 최적화
- **재단선 추가**: 3mm 기본 재단선 자동 생성

### 4. 자동화 시스템
- **폴더 감시**: 실시간 파일 감지 및 자동 처리
- **배치 처리**: 대량 PDF 동시 처리 (동적 워커 스케일링)
- **스트리밍 처리**: 대용량 PDF 메모리 효율적 처리
- **우선순위 큐**: 파일 크기 기반 처리 순서 최적화

### 5. 보고서 생성
- **4가지 형식**: HTML(대시보드), JSON(기계판독), PDF(인쇄용), TXT(간단)
- **상세 분석**: 페이지별 이슈, 개선 제안, 처리 시간
- **시각화**: 차트, 그래프, 썸네일 포함

### 6. GUI 인터페이스
- **모던 UI**: CustomTkinter 기반 다크 테마
- **MVC 패턴**: 체계적인 코드 구조
- **실시간 모니터링**: 처리 진행 상황, 워커 상태
- **드래그 앤 드롭**: 파일 및 폴더 간편 추가 (향상된 피드백)

---

## 🏗 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                    GUI Layer (MVC)                   │
│  ┌─────────┐  ┌──────────┐  ┌─────────────────┐   │
│  │  Views  │◄─│Controllers│◄─│   Components    │   │
│  └─────────┘  └──────────┘  └─────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Processing Pipeline                     │
│                                                      │
│  입력 → 분석 → 검사 → 수정 → 보고서 → 출력        │
│   PDF   Data   Check   Fix    Report   Fixed PDF    │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Analyzer │─►│  Checker │─►│  Fixer   │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│    Dynamic Worker Pool & Streaming Processor        │
│  ┌──────────────┐  ┌──────────────┐               │
│  │Dynamic Workers│  │Stream Process│               │
│  │  (1-N cores) │  │ (Chunk-based)│               │
│  └──────────────┘  └──────────────┘               │
└──────────────────────────────────────────────────────┘
```

---

## 📦 설치 방법

### 시스템 요구사항
- Python 3.10 이상
- Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)
- 최소 4GB RAM (8GB 권장)
- 500MB 디스크 공간

### 빠른 설치

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/pdf_quality_checker_v2.git
cd pdf_quality_checker_v2

# 2. 가상환경 생성 및 활성화
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 외부 도구 설치 (선택사항이지만 권장)
# Windows: Ghostscript와 Poppler 설치
# macOS: brew install ghostscript poppler
# Linux: sudo apt-get install ghostscript poppler-utils
```

---

## 🚀 사용법

### GUI 실행 (권장)
```bash
# 일반 실행
python main.py

# 최적화 버전 (빠른 시작)
python main_optimized.py
```

### CLI 실행
```bash
# 단일 파일 검사
python cli.py check input.pdf

# 배치 처리
python cli.py batch /path/to/pdfs --output /path/to/output

# 폴더 감시
python cli.py watch /path/to/watch --auto-fix
```

### Python 코드에서 사용
```python
from src.core.quality_checker import PDFQualityChecker
from src.core.streaming_processor import StreamingPDFProcessor

# 일반 처리
checker = PDFQualityChecker()
result = checker.check_pdf("input.pdf")
print(f"품질 점수: {result.quality_score}")

# 대용량 PDF 스트리밍 처리
processor = StreamingPDFProcessor(chunk_size=10, max_memory_mb=500)
for chunk_result in processor.process_pdf_streaming("large.pdf"):
    print(f"청크 {chunk_result.chunk_index} 처리 완료")
```

---

## 📁 프로젝트 구조

```
pdf_quality_checker_v2/
├── main.py                 # GUI 메인 진입점
├── main_optimized.py       # 최적화된 빠른 시작 버전
├── cli.py                  # CLI 인터페이스
├── requirements.txt        # 의존성 목록
│
├── src/
│   ├── core/              # 핵심 기능
│   │   ├── analyzers/     # PDF 분석기
│   │   ├── checkers/      # 품질 검사기
│   │   ├── fixers/        # 자동 수정기
│   │   ├── quality_checker.py
│   │   └── streaming_processor.py  # 스트리밍 처리
│   │
│   ├── processing/        # 처리 시스템
│   │   ├── batch_processor.py
│   │   ├── dynamic_batch_processor.py  # 동적 스케일링
│   │   ├── folder_watcher.py
│   │   └── pipeline.py
│   │
│   ├── ui/               # GUI 인터페이스
│   │   ├── views/        # MVC 뷰
│   │   ├── controllers/  # MVC 컨트롤러
│   │   └── components/   # UI 컴포넌트
│   │
│   ├── config/           # 설정
│   │   ├── constants.py
│   │   └── alarm_config.py
│   │
│   └── utils/            # 유틸리티
│       ├── logger.py
│       ├── alarm_manager.py  # 개선된 알람 시스템
│       └── converters.py
│
├── data/                 # 데이터 저장소
│   ├── profiles/        # 품질 프로파일
│   ├── cache/          # 캐시
│   └── output/         # 출력 파일
│
├── tests/               # 테스트
│   ├── unit/           # 단위 테스트
│   └── integration/    # 통합 테스트
│
└── docs/               # 문서
    ├── IMPROVEMENT_COMPLETION_REPORT_20250111.md
    ├── IMPOSITION_MODULE_DESIGN.md
    └── REALTIME_COLLABORATION_DESIGN.md
```

---

## 🛠 기술 스택

### 핵심 라이브러리
- **pikepdf**: PDF 분석 및 수정 (qpdf 기반)
- **PyMuPDF (fitz)**: 빠른 PDF 렌더링 및 조작
- **customtkinter**: 모던 GUI 프레임워크
- **Pillow**: 이미지 처리

### 외부 도구
- **Ghostscript**: PDF 변환 및 최적화
- **Poppler (pdffonts)**: 폰트 분석
- **pdftk** (예정): 판짜기 기능
- **pdfnup** (예정): N-up 레이아웃

### 개발 도구
- **Python 3.10+**: 타입 힌트, dataclass
- **psutil**: 시스템 리소스 모니터링
- **watchdog**: 파일 시스템 감시
- **plyer**: 크로스 플랫폼 알림

---

## 📊 품질 검사 기준

### Critical (치명적)
- RGB 색상 사용
- 폰트 미임베딩
- 이미지 해상도 < 300 DPI
- 재단선 없음

### Warning (경고)
- 잉크 커버리지 > 320%
- Type3 폰트 사용
- 이미지 해상도 300-600 DPI
- 재단선 < 3mm

### Info (정보)
- 메타데이터 누락
- 비표준 페이지 크기
- 압축 가능한 이미지

---

## 💻 개발 가이드

### 코딩 표준
- PEP 8 준수
- 타입 힌트 필수
- 한국어 주석, 영어 변수명
- 테스트 커버리지 80% 목표

### 기여 방법
1. 이슈 생성 또는 선택
2. 기능 브랜치 생성 (`feature/issue-number`)
3. 변경사항 커밋
4. 테스트 작성 및 실행
5. Pull Request 생성

### 테스트 실행
```bash
# 모든 테스트
python -m pytest tests/

# 새 기능 테스트
python tests/integration/test_new_features.py

# 커버리지 확인
python -m pytest --cov=src tests/
```

---

## 🗺 로드맵

### 완료 ✅
- [x] Phase 1: 핵심 기능 구현
- [x] Phase 2: GUI 인터페이스
- [x] Phase 3: 자동화 시스템
- [x] Phase 4: 성능 최적화
- [x] Phase 5: 안정성 강화

### 진행 중 🚧
- [ ] 테스트 커버리지 80% 달성 (현재 ~40%)
- [ ] 문서 완성도 향상
- [ ] CI/CD 파이프라인 구축

### 예정 📋
- [ ] 판짜기(Imposition) 모듈 구현
- [ ] 실시간 협업 기능
- [ ] 클라우드 버전
- [ ] AI 기반 품질 예측

---

## 📝 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 🤝 기여자

프로젝트에 기여해주신 모든 분들께 감사드립니다!

---

## 📞 문의

- 이슈: [GitHub Issues](https://github.com/your-username/pdf_quality_checker_v2/issues)
- 이메일: your-email@example.com

---

*PDF Quality Checker v2.0 - 인쇄 품질의 새로운 기준*