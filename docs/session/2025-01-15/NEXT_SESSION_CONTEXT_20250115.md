# PDF Quality Checker v2.0 - 다음 세션 작업 가이드
*작성일: 2025-01-15*
*작성자: Claude*
*목적: 새로운 Claude 세션에서 작업을 이어받기 위한 상세 컨텍스트*

## 🎯 빠른 시작 가이드

### 새 세션에서 첫 메시지 예시:
```
안녕하세요. PDF Quality Checker v2.0 프로젝트의 다음 단계 작업을 진행하려고 합니다.
NEXT_SESSION_CONTEXT_20250115.md 파일을 참고하여 작업을 진행해주세요.
현재 우선순위는 "Bare except 제거 - 우선순위 중간 파일들" 작업입니다.
```

## 📋 프로젝트 현황 요약

### 프로젝트 정보
- **경로**: `C:\Users\wp\Desktop\pdf_quality_checker_v2`
- **주요 기능**: PDF 파일 인쇄 품질 자동 검사 및 수정
- **기술 스택**: Python 3.10+, CustomTkinter (Classic UI), pikepdf, PyMuPDF
- **아키텍처**: MVC 패턴, 파이프라인 기반, 모듈화 구조
- **현재 브랜치**: master

### 최근 완료 작업 (2025-01-15)
1. ✅ 모든 싱글톤을 @lru_cache 패턴으로 통일
2. ✅ 우선순위 높은 bare except 제거
3. ✅ TODO 기능 3개 모두 구현 (Report, Auto-fix, Pause)
4. ✅ 워커 풀 CPU 코어 기반 동적 설정
5. ✅ 불필요한 파일 48개+ 정리

## 🔥 다음 작업 우선순위

### 1. Bare except 제거 - 우선순위 중간 (권장 첫 작업)

#### 작업 대상 파일과 라인 번호:
```python
# 1. src/data/backup_manager/storage.py:175
# 2. src/data/backup_manager/cleanup.py:181  
# 3. src/data/backup_manager/compression.py:139
# 4. src/processing/batch_scheduler/manager.py:239
# 5. src/data/history_manager/search_engine.py:125
```

#### 작업 방법:
```python
# 잘못된 코드 예시
try:
    some_operation()
except:  # bare except
    pass

# 올바른 수정 예시
try:
    some_operation()
except (FileNotFoundError, PermissionError) as e:
    logger.error(f"파일 작업 실패: {e}")
# 또는 최소한
except Exception as e:
    logger.error(f"예상치 못한 오류: {e}")
```

#### 수정 시 체크리스트:
1. 먼저 어떤 예외가 발생할 수 있는지 코드 분석
2. 가능한 구체적인 예외 타입 사용
3. 로거가 있다면 에러 로깅 추가
4. pass만 있다면 최소한 로그 메시지 추가

### 2. 동적 import 제거 - 성능 개선

#### 문제가 되는 패턴 찾기:
```bash
# 동적 import 패턴 검색 명령
grep -r "def.*:" --include="*.py" | xargs grep -l "from\|import" | head -20
```

#### 수정 예시:
```python
# 잘못된 코드 - 함수 내부에서 import
def process_file():
    from ...core.profiles import ProfileManager  # 매번 import
    manager = ProfileManager()
    
# 올바른 코드 - 파일 상단에서 import
from ...core.profiles import ProfileManager

def process_file():
    manager = ProfileManager()
```

#### 주의사항:
- 순환 참조 문제가 있는 경우 TYPE_CHECKING 활용
- 지연 import가 필요한 경우는 유지

### 3. 기본 단위 테스트 작성

#### 테스트 작성 대상:
```python
# tests/unit/test_singleton_patterns.py (새 파일)
import unittest
import threading
from src.processing import get_queue_manager
from src.data.data_manager import get_data_manager

class TestSingletonPatterns(unittest.TestCase):
    def test_singleton_thread_safety(self):
        """싱글톤이 스레드 안전한지 테스트"""
        instances = []
        
        def get_instance():
            instances.append(get_queue_manager())
        
        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        # 모든 인스턴스가 동일해야 함
        self.assertTrue(all(inst is instances[0] for inst in instances))
    
    def test_singleton_reset(self):
        """싱글톤 리셋 기능 테스트"""
        from src.data.data_manager import get_data_manager, reset_data_manager
        
        manager1 = get_data_manager()
        reset_data_manager()
        manager2 = get_data_manager()
        
        # 리셋 후에는 다른 인스턴스여야 함
        self.assertIsNot(manager1, manager2)
```

#### 테스트 실행 방법:
```bash
# 단위 테스트 실행
python -m pytest tests/unit/test_singleton_patterns.py -v

# 전체 테스트 실행
python -m pytest tests/ -v
```

## 📁 중요 파일 위치 및 역할

### 설정 및 문서
- `CLAUDE.md`: Claude 작업 지침 (한국어 설정, 코딩 규칙)
- `REMAINING_TASKS_CONTEXT_20250115.md`: 전체 작업 현황
- `user_settings.json`: 사용자 설정 (language: "ko")
- `requirements.txt`: 의존성 패키지

### 핵심 모듈 (싱글톤 패턴 적용됨)
- `src/processing/queue_manager/`: 작업 큐 관리 (@lru_cache)
- `src/data/data_manager/`: 데이터 관리 (@lru_cache)
- `src/processing/processor/`: PDF 처리 (@lru_cache)
- `src/processing/batch_scheduler/`: 배치 스케줄러 (@lru_cache)
- `src/utils/alarm_manager/`: 알람 관리 (@lru_cache)

### UI 구조 (Classic UI)
- `src/ui/app.py`: 메인 앱 (159줄, 모듈화 하지 않음)
- `src/ui/controllers/`: MVC 컨트롤러 (호환성 래퍼 포함)
- `src/ui/views/`: 뷰 컴포넌트
- `src/ui/windows/main_window/`: 메인 윈도우

### 새로 구현된 기능 위치
- **Report Generation**: `src/processing/processing_worker/task_handlers.py:184-266`
- **Auto-fix**: `src/processing/processing_worker/task_handlers.py:268-358`
- **Pause/Resume**: `src/ui/controllers/file_controller/file_operations.py:333-399`

## ⚠️ 주의사항 및 함정

### 1. 호환성 래퍼 유지 필수
```
src/ui/controllers/file_controller.py  # 삭제하면 안 됨!
src/ui/controllers/profile_controller.py  # 삭제하면 안 됨!
src/ui/controllers/settings_controller.py  # 삭제하면 안 됨!
```
이 파일들은 구 버전과의 호환성을 위한 래퍼입니다.

### 2. 워커 수 제한
- 최대 8개로 제한됨 (시스템 안정성)
- 환경 변수: `PDF_CHECKER_WORKERS`

### 3. 백업 폴더
- `cleanup_backup_20250115/`: 정리된 파일들
- `docs/old_docs/`: 이전 문서들

### 4. Modern UI 관련
- Modern UI는 제거됨
- Classic UI(CustomTkinter)만 사용
- Modern UI 코드는 `docs/old_docs/modern_ui_backup/`에 백업

## 🛠️ 작업 환경 설정

### 1. 가상환경 활성화
```bash
cd C:\Users\wp\Desktop\pdf_quality_checker_v2
# Windows
venv\Scripts\activate
# 또는
python -m venv venv  # 가상환경이 없는 경우
```

### 2. 의존성 확인
```bash
pip install -r requirements.txt
```

### 3. 앱 실행 테스트
```bash
# 빠른 실행 (도구 검사 생략)
python main.py --fast

# 일반 실행
python main.py
```

### 4. Git 상태 확인
```bash
git status
git diff --name-only  # 변경된 파일 목록
```

## 💡 작업 팁

### 1. Bare except 찾기
```bash
# Windows PowerShell
Select-String -Pattern "except:" -Path "src\**\*.py" -Recurse | Select-Object -Unique Path

# Git Bash
grep -r "except:" --include="*.py" src/
```

### 2. 동적 import 찾기
```bash
# 함수 내부의 import 찾기
grep -r "^    from\|^    import" --include="*.py" src/ | head -30
```

### 3. 테스트 실행
```bash
# 특정 모듈 테스트
python -c "from src.processing import get_queue_manager; qm = get_queue_manager(); print('큐 매니저 OK')"

# 싱글톤 테스트
python -c "
from src.processing import get_queue_manager
qm1 = get_queue_manager()
qm2 = get_queue_manager()
print(f'싱글톤 체크: {qm1 is qm2}')  # True여야 함
"
```

## 📊 프로젝트 통계

### 코드 규모
- 전체 Python 파일: 200+ 개
- 전체 코드 라인: 30,000+ 줄
- 모듈화된 컴포넌트: 15+ 개

### 최근 개선 사항
- 싱글톤 패턴 통일: 5개 매니저
- Bare except 제거: 8개 파일
- TODO 구현: 3개 기능
- 파일 정리: 48+ 개 제거

## 🎯 권장 작업 순서

### Day 1 (2-3시간)
1. **Bare except 제거 - 우선순위 중간**
   - 5개 파일의 bare except 수정
   - 각 파일당 10-15분 예상

### Day 2 (3-4시간)
2. **동적 import 제거**
   - 성능에 영향을 주는 동적 import 찾기
   - 파일 상단으로 이동
   - 순환 참조 확인

### Day 3 (4-5시간)
3. **기본 단위 테스트 작성**
   - 싱글톤 패턴 테스트
   - 핵심 기능 테스트
   - 에러 처리 테스트

### Day 4-5 (선택적)
4. **코드 리뷰 및 최적화**
   - 성능 프로파일링
   - 메모리 사용량 체크
   - 로깅 개선

## 📝 체크리스트

### 작업 시작 전
- [ ] NEXT_SESSION_CONTEXT_20250115.md 읽기
- [ ] CLAUDE.md 읽기 (작업 지침)
- [ ] git status로 현재 상태 확인
- [ ] main.py --fast로 실행 테스트

### 작업 중
- [ ] 각 수정 후 즉시 테스트
- [ ] git diff로 변경사항 확인
- [ ] 주요 변경사항은 커밋 메시지에 상세히 기록

### 작업 완료 후
- [ ] 전체 테스트 실행
- [ ] 문서 업데이트 (이 파일 또는 REMAINING_TASKS_CONTEXT_20250115.md)
- [ ] Git 커밋 (의미 있는 단위로)

## 🆘 문제 해결

### Import 에러 발생 시
```python
# 상대 경로 문제인 경우
from ...core.profiles import ProfileManager  # 실패하면
from src.core.profiles import ProfileManager  # 절대 경로로 시도
```

### 싱글톤 리셋이 필요한 경우
```python
from src.processing.queue_manager import reset_queue_manager
reset_queue_manager()  # 캐시 초기화
```

### 테스트 실패 시
```bash
# 로그 레벨 상세히
python main.py --fast --log-level DEBUG

# 특정 모듈만 테스트
python -m pytest tests/unit/test_specific.py::TestClass::test_method -v
```

## 📌 마지막 조언

1. **작은 단위로 작업**: 한 번에 하나의 파일만 수정
2. **즉시 테스트**: 수정 후 바로 실행 확인
3. **문서화**: 중요한 변경사항은 코멘트 추가
4. **백업**: 큰 변경 전 파일 백업 (*.backup)
5. **질문하기**: 확실하지 않으면 먼저 분석

---

**작성 완료**: 2025-01-15
**다음 리뷰**: 작업 완료 후
**문의사항**: 이 문서를 업데이트하여 다음 세션에 전달

화이팅! 🚀