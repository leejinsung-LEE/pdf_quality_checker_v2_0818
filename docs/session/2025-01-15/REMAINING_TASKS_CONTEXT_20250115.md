# PDF Quality Checker v2.0 - 남은 기술 부채 작업 컨텍스트
*작성일: 2025-01-15*
*작성자: Claude*
*목적: 새 세션에서 작업을 이어받을 수 있도록 상세 가이드 제공*

## 📋 프로젝트 개요
- **프로젝트명**: PDF Quality Checker v2.0
- **주요 기능**: PDF 파일의 인쇄 품질 자동 검사 및 수정
- **기술 스택**: Python 3.10+, CustomTkinter, pikepdf, PyMuPDF
- **아키텍처**: MVC 패턴, 파이프라인 기반 처리, 모듈화 구조

## ✅ 완료된 작업 (2025-01-16 세션 3)

### 1. Bare except 제거 - 우선순위 중간
- **처리된 파일** (5개):
  - `src/data/backup_manager/storage.py:175`: OSError, PermissionError 처리
  - `src/data/backup_manager/cleanup.py:181`: ValueError, TypeError 처리
  - `src/data/backup_manager/compression.py:139`: OSError, PermissionError 처리
  - `src/processing/batch_scheduler/manager.py:239`: ValueError, TypeError 처리
  - `src/data/history_manager/search_engine.py:125`: JSONDecodeError 처리 (3곳)

### 2. 싱글톤 패턴 단위 테스트 작성
- **파일**: `tests/unit/test_singleton_patterns.py` (219줄)
- **테스트 내용**:
  - 5개 싱글톤 매니저 테스트 (queue, data, processor, batch_scheduler, alarm)
  - 멀티스레드 안전성 테스트 (10 스레드)
  - 동시 접근 스트레스 테스트 (20 스레드)
  - LRU 캐시 동작 검증
  - **결과**: 11개 테스트 모두 통과 ✅

### 3. 문서 정확성 검증
- QualityProfile @property가 이미 구현되어 있음 확인
- user_settings.json 타입 문제 해결 확인

## ✅ 완료된 작업 (2025-01-15 세션 2)

### 1. 싱글톤 패턴 완전 통일 (@lru_cache)
- **처리된 매니저들**:
  - `data_manager`: ✅ 전역 변수 → @lru_cache
  - `processor`: ✅ 전역 변수 → @lru_cache
  - `batch_scheduler`: ✅ 더블 체크 락킹 → @lru_cache
  - `alarm_manager`: ✅ 더블 체크 락킹 → @lru_cache

### 2. Bare except 제거 - 우선순위 높음
- **처리된 파일**:
  - `batch_processor.py:312`: queue.Empty로 구체화
  - `alarm_manager/manager.py:338`: queue.Empty와 Exception 분리
  - `print_checker.py:32,190`: ImportError, AttributeError 구체화
  - `color_checker.py:190`: ValueError, RuntimeError 구체화

### 3. 설정 파일 정리
- `user_settings.json`: "test_value_12345" → "ko" 변경

### 4. 불필요한 파일 정리
- **cleanup_backup_20250115/ 폴더로 이동**:
  - 루트의 test_*.py 파일들 (8개)
  - test_*.db 파일들 (2개)
  - temp_files/ 폴더 (36개 테스트 파일)
  - src/ui/views/*.backup 파일들 (2개)
  - .pytest_cache 폴더

### 5. TODO 기능 구현 완료
- **Report Generation**: src/reporting/report_generator 모듈 연동
- **Auto-fix**: src/core/fixers/auto_fixer 모듈 연동
- **Pause 기능**: FileController에 pause/resume 메서드 추가

### 6. 워커 풀 최적화
- **CPU 코어 기반 동적 설정 구현**:
  - CPU 코어 수 - 1 (최소 2, 최대 8)
  - 환경 변수 PDF_CHECKER_WORKERS로 오버라이드 가능
  - 테스트 결과: 16코어 CPU → 8개 워커 자동 설정

## ✅ 이전 완료 작업 (2025-01-15 세션 1)

### 1. 리소스 정리 중복 해결
- **파일**: `main.py`, `src/processing/queue_manager/worker_manager.py`
- **변경 내용**: 
  - cleanup_resources()에 중복 방지 플래그 추가
  - worker_manager의 atexit 등록 제거
  - finally 블록 정리

### 2. Bare except 일부 제거
- **처리된 파일**:
  - `main.py`: locale 설정 예외 구체화
  - `src/ui/windows/main_window/base.py`: 아이콘 설정
  - `src/ui/app.py`: 아이콘 설정

### 3. 싱글톤 패턴 일부 통일 (@lru_cache)
- **처리된 매니저**:
  - `queue_manager`: ✅ 완료
  - `settings_controller`: ✅ 완료
  - `profile_manager`: ✅ 완료
  - `tool_manager`: ✅ 완료 (이전에 처리됨)
  - `file_controller`: ✅ 완료 (이전에 처리됨)
  - `profile_controller`: ✅ 완료 (이전에 처리됨)

### 4. 백업 파일 정리
- 이동된 파일들: `docs/old_docs/backup_20250115/`
  - process_monitor_view_backup.py (1,079줄)
  - backup_20250110/ 폴더
  - batch_process_view_backup.py (715줄)
  - alarm_manager_backup.py (402줄)

## 🔴 남은 Critical 작업

~~### 1. 싱글톤 패턴 통일~~ ✅ 완료 (2025-01-15)
모든 매니저가 @lru_cache 패턴으로 통일됨

### 2. Bare except 제거 - 나머지 파일들
아직 처리되지 않은 bare except 위치:

#### ~~우선순위 높음~~ ✅ 완료 (2025-01-15)

#### ~~우선순위 중간~~ ✅ 완료 (2025-01-16)

**수정 방법**:
```python
# 잘못된 코드
try:
    some_operation()
except:
    pass

# 올바른 코드
try:
    some_operation()
except (SpecificException, AnotherException) as e:
    logger.error(f"작업 실패: {e}")
    # 또는 최소한
except Exception as e:
    logger.error(f"예상치 못한 오류: {e}")
```

## 🟡 중요 작업

### ~~3. TODO 구현~~ ✅ 완료 (2025-01-15)
모든 TODO 기능 구현 완료:
- Report Generation: ReportGenerator 모듈 연동
- Auto-fix: AutoFixer 모듈 연동
- Pause 기능: FileController에 pause/resume 추가

### ~~4. 중복 파일/폴더 정리~~ ✅ 완료 (2025-01-15)
모든 불필요한 파일을 cleanup_backup_20250115/로 이동
- **주의**: src/ui/controllers/*.py 파일들은 호환성 래퍼로 유지 필요

### ~~5. 설정 파일 정리~~ ✅ 완료 (2025-01-15)
`user_settings.json`의 테스트 값을 "ko"로 변경 완료

## 🟢 개선 작업

### 6. 성능 최적화

#### ~~6.1 워커 풀 개선~~ ✅ 완료 (2025-01-15)
CPU 코어 기반 동적 설정 구현:
- CPU 코어 수 - 1 (최소 2, 최대 8)
- 환경 변수 PDF_CHECKER_WORKERS로 오버라이드 가능

#### 6.2 동적 import 제거
**문제**: 함수 내부에서 매번 import
```python
# 잘못된 코드
def process_file():
    from ...core.profiles import ProfileManager  # 매번 import

# 개선된 코드 - 파일 상단에서 한 번만
from ...core.profiles import ProfileManager
```

### 7. 테스트 작성

#### ~~7.1 싱글톤 패턴 단위 테스트~~ ✅ 완료 (2025-01-16)
- `tests/unit/test_singleton_patterns.py` 작성 완료
- 11개 테스트 모두 통과

#### 7.2 통합 테스트
```python
# tests/integration/test_pdf_processing.py
def test_full_pipeline():
    """PDF 처리 파이프라인 전체 테스트"""
```

## 🏗️ 장기 아키텍처 개선

### 8. 의존성 주입 패턴 도입
```python
# src/core/container.py (새 파일)
class DIContainer:
    """의존성 주입 컨테이너"""
    def __init__(self):
        self._services = {}
    
    def register(self, name: str, factory: Callable):
        self._services[name] = factory
    
    def get(self, name: str):
        if name not in self._services:
            raise KeyError(f"Service {name} not registered")
        return self._services[name]()

# 사용 예
container = DIContainer()
container.register('profile_manager', lambda: ProfileManager())
container.register('file_controller', 
                  lambda: FileController(container.get('profile_manager')))
```

### 9. 이벤트 버스 구현
```python
# src/core/event_bus.py (새 파일)
class EventBus:
    """이벤트 기반 통신 시스템"""
    def __init__(self):
        self._handlers = defaultdict(list)
    
    def on(self, event: str, handler: Callable):
        self._handlers[event].append(handler)
    
    def emit(self, event: str, data: Any = None):
        for handler in self._handlers[event]:
            handler(data)

# 사용 예
bus = EventBus()
bus.on('file.processed', lambda data: print(f"파일 처리 완료: {data}"))
bus.emit('file.processed', {'file': 'test.pdf', 'status': 'success'})
```

## 📝 작업 우선순위 가이드

### ✅ 즉시 (1-2일) - 완료 (2025-01-15)
1. ✅ 싱글톤 패턴 통일 (모든 매니저)
2. ✅ Bare except 제거 (우선순위 높음)
3. ✅ user_settings.json 테스트 값 정리
4. ✅ TODO 기능 구현 (report, auto-fix, pause)
5. ✅ 중복 파일/폴더 정리
6. ✅ 워커 풀 최적화

### 단기 (1주)
7. ✅ Bare except 제거 (우선순위 중간) - 완료 (2025-01-16)
8. ⬜ 동적 import 제거 - 분석 결과 불필요 (TYPE_CHECKING 블록 유지)
9. ✅ 싱글톤 패턴 단위 테스트 작성 - 완료 (2025-01-16)

### 중기 (2-4주)
10. ⬜ 통합 테스트 구축
11. ⬜ CI/CD 파이프라인 설정

### 장기 (1-3개월)
12. ⬜ 의존성 주입 패턴 도입
13. ⬜ 이벤트 버스 구현
14. ⬜ 전체 리팩토링

## 🛠️ 작업 시작 방법

### 1. 환경 설정
```bash
cd C:\Users\wp\Desktop\pdf_quality_checker_v2
pip install -r requirements.txt
```

### 2. 테스트 실행
```bash
# 싱글톤 패턴 테스트
python -c "from src.processing import get_queue_manager; print(get_queue_manager())"

# 앱 실행 테스트
python main.py --fast
```

### 3. 변경사항 확인
```bash
# Git 상태 확인
git status

# 변경된 파일 목록
git diff --name-only
```

## ⚠️ 주의사항

1. **모듈화 추가 금지**: 이미 과도한 모듈화 상태, 더 이상 분리하지 말 것
2. **기능 유지**: 기존 기능이 깨지지 않도록 주의
3. **점진적 개선**: 한 번에 많은 변경 피하기
4. **테스트 우선**: 변경 전 테스트 작성
5. **백업 필수**: 큰 변경 전 백업

## 📚 참고 문서
- `CLAUDE.md`: 프로젝트 작업 지침
- `TECHNICAL_DEBT_CONTEXT_20250115.md`: 이전 기술 부채 분석
- `PDF Quality Checker v2.0 - 확장형 프로젝트 설계 명세서.md`: 원래 설계

## 💡 도움말

### 싱글톤 패턴 변경 템플릿
```python
# 1. import 추가
from functools import lru_cache

# 2. 전역 변수 제거
# _manager = None  # 삭제

# 3. 함수 변경
@lru_cache(maxsize=1)
def get_manager():
    return Manager()

# 4. reset 함수 수정
def reset_manager():
    get_manager.cache_clear()
```

### Bare except 수정 템플릿
```python
# 1. 구체적 예외 찾기
try:
    operation()
except Exception as e:
    print(f"오류 타입: {type(e).__name__}")  # 실제 예외 확인

# 2. 구체적 예외로 변경
try:
    operation()
except (FileNotFoundError, PermissionError) as e:
    logger.error(f"파일 작업 실패: {e}")
```

---

**작성 완료**: 2025-01-15
**최종 업데이트**: 2025-01-16
**다음 리뷰**: 2025-01-22

이 문서를 참고하여 남은 작업을 체계적으로 진행하세요. 각 작업 완료 시 체크박스를 표시하여 진행 상황을 추적하세요.