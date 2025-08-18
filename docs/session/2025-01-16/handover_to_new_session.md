# 새 Claude 세션으로 전달할 내용

## 복사해서 새 Claude에게 전달하세요:

---

PDF Quality Checker v2.0 프로젝트에서 Ghent Output Suite 테스트 관련 긴급 수정이 필요합니다.

## 현재 상황
- Ghent 테스트 40개 파일 모두 감지(100%)하지만, **실제로는 파싱 오류로 인한 오탐지입니다**
- 모든 파일에서 "폰트가 임베디드되지 않음" 이슈만 보고됨
- Good(G) 파일들도 오류로 잘못 판단되고 있음

## 핵심 문제
`src/core/analyzers/font_analyzer/analyzer.py`의 `_parse_pdffonts_output()` 메서드에서:

```python
# 현재 코드 (289-296행)
parts = line.split()
if len(parts) >= 9:
    font_name = parts[0]
    font_type = parts[1]
    encoding = parts[2]
    embedded = parts[3] == 'yes'
    subset = parts[4] == 'yes'
```

**문제**: "Type 1C" 같은 공백 포함 폰트 타입이 split()으로 분리되어 인덱스가 틀어짐

**실제 pdffonts 출력 예시**:
```
RPNMFU+MyriadPro-Regular     Type 1C           WinAnsi          yes yes no     238  0
```
위 라인이 split()되면:
- parts[1] = "Type" (잘못됨)
- parts[2] = "1C" (잘못됨)
- parts[3] = "WinAnsi" (embedded가 아님!)

## 즉시 수정 필요

### 1. pdffonts 파싱 수정
고정폭 컬럼 기반 파싱으로 변경하거나 정규식 사용:

```python
def _parse_pdffonts_output(self, output: str) -> PDFFontsResult:
    # 헤더 라인으로 컬럼 위치 파악
    # name: 0-36
    # type: 37-53  
    # encoding: 54-70
    # emb: 71-74
    # sub: 75-78
    # uni: 79-82
    
    # 또는 정규식:
    # pattern = r'^(.{36})\s+(.{16})\s+(.{16})\s+(yes|no)\s+(yes|no)\s+(yes|no)'
```

### 2. Good 파일 검증
Ghent 파일명 규칙:
- `Patch PS-XXX-YYE.pdf`: Error 파일 (문제 있어야 함)
- `Patch PS-XXX-YYW.pdf`: Warning 파일 (경고 있어야 함)  
- `Patch PS-XXX-YYG.pdf`: Good 파일 (**문제 없어야 함**)

현재 Good 파일들도 오류로 감지되는 것은 잘못된 동작입니다.

### 3. 테스트 명령
```bash
# 수정 후 테스트
python test_ghent.py

# Good 파일 개별 테스트
python -c "
from pathlib import Path
from src.core.analyzers.pdf_analyzer import PDFAnalyzer
from src.core.checkers import create_default_checker, CheckerContext

# Good 파일 테스트
test_file = Path('Ghent Output Suite/Processing-Steps-Test-Suite-V1.0/Patches/Patch PS-001-01G.pdf')
analyzer = PDFAnalyzer()
result = analyzer.analyze(test_file)
checker = create_default_checker()
issues = checker.check(result, CheckerContext())
print(f'{test_file.name}: {len(issues)}개 이슈')
# Good 파일은 0개여야 정상!
"
```

## 참고 문서
- `/docs/session/2025-01-16/ghent_test_analysis_report.md`: 전체 분석 보고서
- `/docs/session/2025-01-16/session_context.md`: 작업 컨텍스트
- `/CLAUDE.md`: 프로젝트 지침

## 기대 결과
수정 후:
- Good(G) 파일: 0개 이슈
- Warning(W) 파일: 경고 수준 이슈만
- Error(E) 파일: 실제 오류 감지
- 전체 감지율: E/W 파일만 감지 (약 65%)

천천히 깊이 생각한 후 pdffonts 파싱을 수정해주세요. 고정폭 컬럼 파싱이 가장 안정적일 것 같습니다.

---

## 추가 정보 (필요시)

### 현재 코드 구조
- FontAnalyzer → tool_manager → pdffonts.exe 실행
- _parse_pdffonts_output() 메서드가 출력 파싱
- PDFFontsResult 객체로 반환
- _process_external_result()에서 FontInfo 객체로 변환

### 완료된 작업
- RuleRegistry 시스템 구축 완료
- GUI 설정 통합 완료
- AdvancedChecker 구현 완료
- CheckerContext 프로파일 연동 완료

### 환경 정보
- Windows 11
- Python 3.13
- poppler/pdffonts.exe 사용 중
- CustomTkinter UI