# PDF Quality Checker v2.0 - 검사 항목별 도구 매핑

## 검사 도구 현황

### 외부 도구
| 도구명 | 경로 | 상태 | 용도 |
|--------|------|------|------|
| pdffonts | poppler/pdffonts.exe | ✓ 정상 | 폰트 정보 추출 |
| gs | gs/gswin64c.exe | ✗ 미설치 | 고급 PDF 분석 |
| pdftk | - | 계획됨 | PDF 조작 |
| pdfnup | - | 계획됨 | 판짜기 |

### 내부 라이브러리
| 라이브러리 | 버전 | 용도 |
|------------|------|------|
| PyMuPDF (fitz) | 최신 | PDF 분석 기본 엔진 |
| pikepdf | 최신 | PDF 구조 분석 |
| Pillow | 최신 | 이미지 처리 |

## 검사 항목별 도구 매핑

### 1. 폰트 검사 (FontChecker)

| 검사 항목 | 규칙 ID | 사용 도구 | 구현 상태 |
|----------|---------|----------|-----------|
| 폰트 임베딩 확인 | font_embedding | pdffonts + PyMuPDF | ✓ 구현 (버그 있음) |
| Type3 폰트 검출 | type3_font | PyMuPDF | ✓ 구현 |
| 최소 텍스트 크기 | min_text_size | PyMuPDF | ✓ 구현 |
| 폰트 서브셋 확인 | - | pdffonts | ✓ 부분 구현 |
| 인코딩 검사 | - | pdffonts | ✓ 부분 구현 |

### 2. 색상 검사 (ColorChecker)

| 검사 항목 | 규칙 ID | 사용 도구 | 구현 상태 |
|----------|---------|----------|-----------|
| RGB 색상 검출 | rgb_color | PyMuPDF | ✓ 구현 |
| 별색 검출 | spot_color | PyMuPDF | ✓ 구현 |
| 잉크 도포량 | ink_coverage | PyMuPDF | △ 기본 구현 |
| CMYK 분리 | - | Ghostscript | ✗ 미구현 |
| ICC 프로파일 | - | PyMuPDF | ✗ 미구현 |

### 3. 이미지 검사 (ImageChecker)

| 검사 항목 | 규칙 ID | 사용 도구 | 구현 상태 |
|----------|---------|----------|-----------|
| 해상도 검사 | image_resolution | PyMuPDF | ✓ 구현 |
| 압축 방식 | image_compression | PyMuPDF | ✓ 구현 |
| 색상 모드 | image_color_mode | PyMuPDF | ✓ 구현 |
| 비트 깊이 | - | PyMuPDF | △ 부분 구현 |
| 알파 채널 | - | PyMuPDF | ✗ 미구현 |

### 4. 레이아웃 검사 (LayoutChecker)

| 검사 항목 | 규칙 ID | 사용 도구 | 구현 상태 |
|----------|---------|----------|-----------|
| 재단선 검사 | bleed_check | PyMuPDF | ✓ 구현 |
| 비균일 재단선 | non_uniform_bleed | PyMuPDF | ✓ 구현 |
| 대형 포맷 | large_format_bleed | PyMuPDF | ✓ 구현 |
| 페이지 크기 | - | PyMuPDF | ✓ 구현 |
| 회전 검출 | - | PyMuPDF | ✓ 구현 |

### 5. 인쇄 검사 (PrintChecker)

| 검사 항목 | 규칙 ID | 사용 도구 | 구현 상태 |
|----------|---------|----------|-----------|
| 오버프린트 | overprint | PyMuPDF | △ 기본 구현 |
| 흰색 오버프린트 | white_overprint | PyMuPDF | △ 기본 구현 |
| 트래핑 | - | Ghostscript | ✗ 미구현 |
| 헤어라인 | - | PyMuPDF | ✗ 미구현 |

### 6. 고급 검사 (AdvancedChecker)

| 검사 항목 | 규칙 ID | 사용 도구 | 구현 상태 |
|----------|---------|----------|-----------|
| 오버프린트 상세 | check_overprint | PyMuPDF | △ 속성 없음 |
| 16비트 이미지 | check_16bit_images | PyMuPDF | △ 데이터 없음 |
| JPEG2000 압축 | check_compression | PyMuPDF | △ 부분 구현 |
| JBIG2 압축 | check_compression | PyMuPDF | △ 부분 구현 |
| ICC 프로파일 | check_icc_profile | PyMuPDF | ✗ 속성 없음 |
| DeviceN 색상 | check_devicen | PyMuPDF | △ 데이터 없음 |
| Type3 폰트 | check_type3_fonts | PyMuPDF | ✓ 구현 |

## 프로파일별 검사 활성화

### Default 프로파일
```json
{
  "check_options": {
    "check_rgb": true,
    "check_spot": true,
    "allow_rgb": false,
    "allow_spot": true,
    "ink_coverage": false,
    "check_overprint": false,
    "check_16bit_images": false,
    "check_compression": false,
    "check_icc_profile": false,
    "check_devicen": false,
    "check_type3_fonts": false
  }
}
```

### Print Ready 프로파일
```json
{
  "check_options": {
    "check_rgb": true,
    "check_spot": true,
    "allow_rgb": false,
    "allow_spot": false,
    "ink_coverage": true,
    "check_overprint": true,
    "check_16bit_images": true,
    "check_compression": true,
    "check_icc_profile": true,
    "check_devicen": true,
    "check_type3_fonts": true
  }
}
```

## 도구별 책임 범위

### pdffonts (poppler-utils)
- **주요 역할**: 폰트 메타데이터 추출
- **제공 정보**:
  - 폰트 이름
  - 폰트 타입 (TrueType, Type1, Type1C, CID 등)
  - 인코딩
  - 임베딩 여부
  - 서브셋 여부
  - 유니코드 맵 여부
- **한계**: 폰트 내용 분석 불가

### PyMuPDF (fitz)
- **주요 역할**: PDF 구조 및 내용 분석
- **제공 정보**:
  - 페이지 정보
  - 텍스트 추출
  - 이미지 추출 및 분석
  - 기본 색상 정보
  - 메타데이터
- **한계**: 고급 인쇄 속성 분석 제한적

### Ghostscript (계획)
- **계획된 역할**: 고급 PDF 분석 및 변환
- **예상 기능**:
  - CMYK 분리
  - ICC 프로파일 처리
  - 트래핑 분석
  - PDF/X 검증
- **현재 상태**: 미통합

## 개선 계획

### 단기 (1주일)
1. pdffonts 파싱 버그 수정
2. PyMuPDF 속성 확장 (오버프린트, ICC 등)
3. Ghostscript 통합 시작

### 중기 (1개월)
1. 모든 고급 검사 구현
2. 검사 정확도 향상
3. False positive 제거

### 장기 (3개월)
1. 판짜기 기능 구현
2. PDF/X 표준 검증
3. 자동 수정 기능 확장