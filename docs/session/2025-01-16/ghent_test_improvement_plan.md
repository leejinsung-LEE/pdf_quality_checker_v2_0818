# PDF Quality Checker v2.0 - Ghent 테스트 개선 계획

## 📋 테스트 결과 요약
- **테스트 일시**: 2025-01-16
- **테스트 대상**: Ghent Output Suite V5.0 (공식 PDF 오류 샘플)
- **검출 성공률**: 11.1% (9개 중 1개만 정확히 판정)
- **주요 문제**: 표준 PDF 오류 대부분을 검출하지 못함

## 🔍 검출 실패 원인

### 1. 외부 도구 문제
```
pdffonts 도구를 찾을 수 없습니다
폰트 분석 실패: 'FontInfo' object has no attribute 'get'
```
- **원인**: poppler-utils 미설치 또는 PATH 설정 문제
- **영향**: 폰트 임베딩, 대체 폰트 검출 불가

### 2. 분석 엔진 한계
- PDF 내부 구조 파싱 깊이 부족
- 특수 객체(DeviceN, Spot Color, ICC Profile) 미지원
- 이미지 압축 방식(JPEG2000, JBIG2) 검사 미구현

### 3. 검사 규칙 부재
- 오버프린트 설정 검사 규칙 없음
- 16비트 이미지 검사 규칙 없음
- ICC 프로파일 유효성 검사 없음

## 💡 개선 방안

### Phase 1: 즉시 개선 가능 (1-2일)

#### 1.1 외부 도구 설치 가이드 작성
```python
# src/utils/external_tools_checker.py
def check_external_tools():
    """필수 외부 도구 설치 확인"""
    tools = {
        'pdffonts': 'poppler-utils',
        'gs': 'ghostscript',
        'pdftk': 'pdftk (선택사항)'
    }
    
    missing = []
    for tool, package in tools.items():
        if not shutil.which(tool):
            missing.append(package)
    
    if missing:
        print(f"다음 패키지 설치 필요: {', '.join(missing)}")
        print("설치 방법:")
        print("  Windows: scoop install poppler ghostscript")
        print("  Mac: brew install poppler ghostscript")
        print("  Linux: apt-get install poppler-utils ghostscript")
```

#### 1.2 FontInfo 객체 수정
```python
# src/core/models/font_info.py 수정
@dataclass
class FontInfo:
    name: str
    is_embedded: bool = True
    is_type3: bool = False
    pages_used: List[int] = field(default_factory=list)
    
    @property
    def needs_embedding(self):
        return not self.is_embedded
    
    def get(self, key, default=None):
        """딕셔너리 스타일 접근 지원"""
        return getattr(self, key, default)
```

### Phase 2: 중기 개선 (1주)

#### 2.1 누락된 검사 규칙 추가
```python
# src/core/checkers/advanced_rules.py
class JPEG2000CompressionRule(CheckRule):
    """JPEG2000 압축 검사"""
    def check(self, analysis_result, context):
        for image in analysis_result.images:
            if image.compression == 'JPEG2000':
                return QualityIssue(
                    severity=IssueSeverity.WARNING,
                    title="JPEG2000 압축 사용",
                    description="일부 RIP에서 지원하지 않을 수 있습니다"
                )

class SixteenBitImageRule(CheckRule):
    """16비트 이미지 검사"""
    def check(self, analysis_result, context):
        for image in analysis_result.images:
            if image.bits_per_component > 8:
                return QualityIssue(
                    severity=IssueSeverity.INFO,
                    title="16비트 이미지 발견",
                    description="파일 크기가 클 수 있습니다"
                )

class WhiteOverprintRule(CheckRule):
    """흰색 오버프린트 검사"""
    def check(self, analysis_result, context):
        # PyMuPDF로 오버프린트 설정 검사
        pass
```

#### 2.2 PDF 분석 깊이 향상
```python
# src/core/analyzers/deep_analyzer.py
class DeepPDFAnalyzer:
    """심층 PDF 분석기"""
    
    def analyze_color_spaces(self, pdf_path):
        """색상 공간 상세 분석"""
        doc = fitz.open(pdf_path)
        color_spaces = set()
        
        for page in doc:
            # 페이지 리소스에서 ColorSpace 추출
            resources = page.get_resources()
            if resources:
                cs = resources.get('ColorSpace', {})
                color_spaces.update(cs.keys())
        
        return color_spaces
    
    def analyze_overprint(self, pdf_path):
        """오버프린트 설정 분석"""
        # Ghostscript 활용
        cmd = f"gs -dNOPAUSE -dBATCH -sDEVICE=inkcov {pdf_path}"
        # ... 구현
```

### Phase 3: 장기 개선 (2-4주)

#### 3.1 완전한 PDF/X 표준 지원
- PDF/X-1a, PDF/X-3, PDF/X-4 검증
- ISO 15930 표준 준수 검사
- Ghent Workgroup 권장사항 구현

#### 3.2 AI 기반 오류 패턴 학습
- 오류 샘플 데이터베이스 구축
- 머신러닝 모델로 패턴 인식
- 자동 규칙 생성

## 📈 예상 개선 효과

### 단계별 검출률 향상 예측
1. **Phase 1 완료**: 30-40% 검출률
2. **Phase 2 완료**: 60-70% 검출률  
3. **Phase 3 완료**: 85-95% 검출률

### 우선순위
1. **최우선**: 외부 도구 설치 및 FontInfo 수정
2. **높음**: 오버프린트, ICC 프로파일 검사
3. **중간**: JPEG2000, 16비트 이미지 검사
4. **낮음**: 완전한 PDF/X 검증

## 🎯 액션 아이템

### 즉시 실행 (오늘)
- [ ] poppler-utils 설치 가이드 문서 작성
- [ ] FontInfo 클래스 get 메서드 추가
- [ ] 외부 도구 체크 스크립트 작성

### 이번 주
- [ ] WhiteOverprintRule 구현
- [ ] JPEG2000CompressionRule 구현
- [ ] DeepPDFAnalyzer 프로토타입 개발

### 이번 달
- [ ] 전체 Ghent 테스트 스위트 통과율 70% 달성
- [ ] CI/CD에 Ghent 테스트 통합
- [ ] 성능 최적화

## 📝 참고 자료
- [Ghent Workgroup](https://www.gwg.org/)
- [PDF/X Standards](https://www.iso.org/standard/74449.html)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Ghostscript API](https://www.ghostscript.com/doc/)