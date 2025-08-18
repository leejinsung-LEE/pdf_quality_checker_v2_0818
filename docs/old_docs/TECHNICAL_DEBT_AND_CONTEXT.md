# 📋 PDF Quality Checker v2.0 - 기술 부채 및 컨텍스트 문서

> **작성일**: 2025-08-07  
> **목적**: 프로젝트의 현재 상태, 기술 부채, AI 코딩 주의사항 정리

---

## 🚨 현재 기술 부채 현황

### 1. **인코딩 및 유니코드 문제**
```python
# 문제: Windows 환경에서 cp949 인코딩 오류 발생
# 위치: 여러 분석기의 print 문에서 이모지 사용 시
UnicodeEncodeError: 'cp949' codec can't encode character
```

**영향 범위**:
- `src/core/analyzers/*.py` - 이모지 포함 출력
- `src/processing/folder_watcher.py` - 로그 메시지
- 보고서 생성 시 특수 문자 처리

**해결 방안**:
- 모든 파일 열기 시 `encoding='utf-8'` 명시
- print 문에서 이모지 제거 또는 조건부 사용
- 로깅 시스템 UTF-8 설정 강제

### 2. **워커 시스템 종료 오류**
```python
# 문제: ThreadPoolExecutor 종료 시 _futures 속성 오류
AttributeError: 'ThreadPoolExecutor' object has no attribute '_futures'
```

**영향 범위**:
- `src/processing/queue_manager.py`
- `src/processing/processing_worker.py`

**임시 해결**:
- try-except로 감싸서 오류 무시
- 하지만 제대로 된 cleanup이 안 될 수 있음

### 3. **중복 폴더 설정 저장**
```json
// 문제: folder_watch_config.json에 같은 폴더가 중복 저장됨
{
  "folders": [
    {"path": "test_rgb_fix", ...},  // 중복 1
    {"path": "test_rgb_fix", ...},  // 중복 2
  ]
}
```

**영향 범위**:
- `src/processing/folder_watcher.py`
- 폴더 감시 시 중복 처리 가능

**필요한 수정**:
- 폴더 추가 시 중복 체크 로직
- 절대 경로로 통일하여 비교

### 4. **프로파일 로딩 실패**
```
[Warning] Failed to load profile quality_profiles.json: 'name'
```

**영향 범위**:
- `src/core/profiles/profile_manager.py`
- 기본 프로파일로 폴백되지만 사용자 정의 프로파일 사용 불가

### 5. **DashboardView matplotlib 폰트 경고**
```
UserWarning: Glyph 45936 (\N{HANGUL SYLLABLE DE}) missing from font(s)
```

**영향 범위**:
- `src/ui/views/dashboard_view.py`
- 차트 한글 표시 문제

---

## ⚠️ AI 코딩 시 주의사항

### 1. **타입 힌트 일관성**
```python
# 나쁜 예 - AI가 자주 실수
def process_file(file_path):  # 타입 힌트 누락
    return result

# 좋은 예
def process_file(file_path: Path) -> ProcessingResult:
    return result
```

### 2. **import 정리**
AI는 종종 불필요한 import를 추가하거나 순환 참조를 만듦:
```python
# 주의: 순환 참조 가능성
from ..processing import *  # 와일드카드 import 피하기
from .folder_watcher import FolderWatcher  # 같은 모듈 내 순환 참조 체크
```

### 3. **경로 처리**
```python
# AI가 자주 실수하는 부분
path = "data/files"  # 상대 경로 하드코딩

# 올바른 방법
path = Path(__file__).parent / "data" / "files"
# 또는
path = Path.cwd() / "data" / "files"
```

### 4. **에러 처리 누락**
AI는 happy path만 고려하는 경향:
```python
# 위험한 코드
def read_file(path):
    with open(path) as f:
        return f.read()

# 안전한 코드
def read_file(path: Path) -> Optional[str]:
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except (IOError, UnicodeDecodeError) as e:
        logger.error(f"파일 읽기 실패: {e}")
        return None
```

### 5. **메모리 누수 가능성**
```python
# 문제: 대용량 PDF 처리 시 메모리 해제 안 됨
class PDFProcessor:
    def __init__(self):
        self.cache = {}  # 계속 쌓임
    
    def process(self, pdf):
        self.cache[pdf.id] = pdf  # 메모리 누수

# 해결: 명시적 cleanup
def cleanup(self):
    self.cache.clear()
```

---

## 🔧 현재 시스템 구조 컨텍스트

### 핵심 처리 흐름
```
1. UI (FileController) 
   ↓
2. QueueManager (작업 큐)
   ↓
3. WorkerPool (멀티스레드)
   ↓
4. ProcessingPipeline
   ↓
5. Analyzer → Checker → Fixer → Reporter
```

### 폴더별 설정 구조 (2025-08-07 구현)
```python
@dataclass
class FolderConfig:
    path: Path
    profile: str  # 프로파일
    check_settings: Dict[str, bool]  # 검사 항목
    auto_fix_settings: Dict[str, bool]  # 자동 수정
    auto_process: bool  # 자동 처리 여부
    generate_report: bool  # 보고서 생성
    report_formats: List[str]  # 보고서 형식
```

### 파일 상태 관리
```python
class FileStatus(Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"
```

---

## 📊 성능 고려사항

### 1. **워커 풀 크기**
- 현재: 2개 워커 (하드코딩)
- 권장: CPU 코어 수 기반 동적 설정
```python
worker_count = min(os.cpu_count() or 2, 4)  # 최대 4개
```

### 2. **파일 크기 제한**
- 현재: 제한 없음
- 문제: 500MB 이상 PDF 처리 시 메모리 부족
- 해결: 스트리밍 처리 또는 청크 단위 처리 필요

### 3. **폴더 감시 폴링 간격**
- 현재: 5초 (하드코딩)
- 개선: 설정 가능하게 변경 필요

---

## 🎯 향후 개선 로드맵

### 단기 (1-2주)
1. [ ] 인코딩 문제 전체 해결
2. [ ] 워커 종료 오류 수정
3. [ ] 중복 폴더 체크 로직
4. [ ] 프로파일 로딩 오류 해결

### 중기 (1개월)
1. [ ] 메모리 관리 개선
2. [ ] 성능 프로파일링 및 최적화
3. [ ] 에러 복구 메커니즘 강화
4. [ ] 로깅 시스템 개선

### 장기 (3개월)
1. [ ] 판짜기(Imposition) 기능 구현 (Phase 6)
2. [ ] 웹 인터페이스 개발
3. [ ] 클라우드 연동
4. [ ] API 서버 구축

---

## 💡 개발 시 체크리스트

### 새 기능 추가 시
- [ ] PROMPTS.md 참조하여 품질 체크
- [ ] 타입 힌트 추가
- [ ] 에러 처리 구현
- [ ] 로깅 추가
- [ ] 테스트 코드 작성
- [ ] 문서화 업데이트

### 버그 수정 시
- [ ] 근본 원인 분석
- [ ] 영향 범위 확인
- [ ] 회귀 테스트
- [ ] 관련 모듈 체크

### 리팩토링 시
- [ ] 기존 테스트 통과 확인
- [ ] 성능 영향 평가
- [ ] 의존성 체크
- [ ] 문서 업데이트

---

## 🔍 디버깅 팁

### 로그 확인
```bash
# 메인 로그
tail -f logs/pdf_checker_*.log

# 워커 로그
tail -f logs/test_worker.log

# GUI 로그
tail -f logs/test_gui.log
```

### 자주 발생하는 오류와 해결
1. **"No module named 'src'"**
   - 실행 위치가 프로젝트 루트가 아님
   - 해결: `cd pdf_quality_checker_v2`

2. **"Ghostscript not found"**
   - 외부 도구 경로 문제
   - 해결: `gs/bin/gswin64c.exe` 존재 확인

3. **"Worker not responding"**
   - 워커 데드락 또는 무한 루프
   - 해결: 타임아웃 설정, 강제 종료 메커니즘

---

## 📝 참고 문서

- `CLAUDE.md` - AI 작업 지침
- `PROMPTS.md` - 코드 품질 체크리스트
- `PDF_Quality_Checker_v2.0_최종설계명세서.md` - 전체 설계
- `구현_검증_보고서.md` - 구현 상태 (85% 완료)

---

**마지막 업데이트**: 2025-08-07  
**작성자**: Claude (Anthropic)  
**검토 필요**: 인간 개발자의 검토 및 보완 필요