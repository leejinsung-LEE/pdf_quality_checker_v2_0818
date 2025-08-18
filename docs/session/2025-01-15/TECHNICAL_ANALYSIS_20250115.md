# PDF Quality Checker v2.0 - 기술 분석 및 아키텍처 가이드
*작성일: 2025-01-15*
*목적: 코드베이스의 깊은 이해를 위한 기술적 분석*

## 🏗️ 아키텍처 개요

### 전체 시스템 구조
```
┌─────────────────────────────────────────────────────┐
│                    UI Layer (MVC)                    │
│  ┌─────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Views  │◄─│  Controllers │◄─│  Components  │  │
│  └─────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│               Processing Layer                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Queue   │◄─│   Pipeline   │◄─│   Workers    │ │
│  │ Manager  │  │   Processor  │  │    Pool      │ │
│  └──────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│                   Core Layer                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │Analyzers │  │   Checkers   │  │    Fixers    │ │
│  └──────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────┘
```

### 데이터 플로우
```
1. UI에서 파일 선택
   ↓
2. FileController가 작업 생성
   ↓
3. QueueManager가 작업 큐에 추가
   ↓
4. WorkerPool이 작업 처리
   ↓
5. Pipeline을 통해 분석/검사/수정
   ↓
6. 결과를 UI에 콜백으로 전달
```

## 🔍 싱글톤 패턴 분석

### 현재 구현 상태 (@lru_cache 패턴)
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_manager() -> Manager:
    """싱글톤 인스턴스 반환"""
    return Manager()

def reset_manager() -> None:
    """싱글톤 리셋 (테스트용)"""
    get_manager.cache_clear()
```

### 싱글톤 매니저 목록
| 매니저 | 파일 위치 | 역할 | 의존성 |
|--------|-----------|------|---------|
| QueueManager | src/processing/queue_manager/ | 작업 큐 관리 | WorkerPool, TaskManager |
| DataManager | src/data/data_manager/ | 데이터 영속성 | HistoryManager, CacheManager |
| Processor | src/processing/processor/ | PDF 처리 | Pipeline, QualityChecker |
| BatchScheduler | src/processing/batch_scheduler/ | 배치 스케줄링 | QueueManager |
| AlarmManager | src/utils/alarm_manager/ | 알람 및 알림 | 없음 |

### 싱글톤 패턴의 장단점
**장점:**
- 전역 접근점 제공
- 메모리 효율성
- 상태 일관성 보장

**단점:**
- 테스트 어려움 (reset 함수로 해결)
- 의존성 숨김
- 멀티스레드 고려 필요 (@lru_cache로 해결)

## 📦 모듈화 구조 분석

### 모듈화 기준
```python
# 모듈화 결정 트리
if 파일_크기 < 200:
    return "모듈화 불필요"
elif 파일_크기 < 500:
    if 복잡도 == "높음":
        return "모듈화 권장"
    else:
        return "단일 파일 유지"
elif 파일_크기 < 1000:
    if 책임_분리_가능:
        return "모듈화 권장"
    else:
        return "리팩토링 후 결정"
else:
    return "모듈화 필수"
```

### 현재 모듈화 상태
| 모듈 | 원본 크기 | 현재 크기 | 모듈화 타입 | 평가 |
|------|-----------|-----------|-------------|------|
| history_manager | 658줄 | 1486줄 | 기능별 분리 | ✅ 적절 |
| data_manager | 396줄 | 1074줄 | 책임별 분리 | ✅ 적절 |
| main_window | 693줄 | 973줄 | 컴포넌트별 | ✅ 적절 |
| app.py | 159줄 | 159줄 | 모듈화 안함 | ✅ 적절 |
| tool_manager | 332줄 | 332줄 | 모듈화 안함 | ✅ 적절 |

### 모듈 구조 패턴
```
module_name/
├── __init__.py       # 공개 API, 싱글톤 함수
├── base.py          # 추상 클래스, 데이터 모델
├── implementation.py # 구체적 구현
├── utils.py         # 헬퍼 함수
└── tests/           # 모듈 테스트
    └── test_module.py
```

## 🔧 핵심 컴포넌트 상세 분석

### 1. QueueManager (작업 큐 관리)
```python
# 구조
queue_manager/
├── __init__.py         # 싱글톤 get_queue_manager()
├── queue_manager.py    # 메인 클래스
├── task_manager.py     # 작업 관리
├── task_tracker.py     # 작업 추적
├── worker_manager.py   # 워커 풀 관리
└── statistics.py       # 통계 수집

# 핵심 기능
- 우선순위 큐 (PriorityQueue)
- 동적 워커 수 조정 (CPU 기반)
- 작업 상태 추적
- 콜백 처리
```

### 2. FileController (UI-Processing 브릿지)
```python
# 구조
file_controller/
├── __init__.py         # FileController 클래스
├── base.py            # FileStatus, FileItem 모델
├── file_operations.py  # 파일 작업 (add, cancel, retry, pause)
├── event_handler.py    # UI 콜백 관리
└── status_tracker.py   # 상태 추적

# 핵심 기능
- 파일 처리 요청 관리
- UI 콜백 처리
- 폴더 감시 연동
- 일시정지/재개 (NEW!)
```

### 3. Pipeline (처리 파이프라인)
```python
# 구조
pipeline/
├── __init__.py
├── base.py            # PipelineStage 추상 클래스
├── stages.py          # 구체적 스테이지 구현
└── orchestrator.py    # 파이프라인 실행

# 처리 단계
1. AnalysisStage    → PDF 분석
2. CheckerStage     → 품질 검사
3. FixerStage       → 자동 수정
4. ReportStage      → 보고서 생성
```

### 4. Profile System (프로파일 관리)
```python
# 구조
profiles/
├── profile_manager/
│   ├── __init__.py     # 싱글톤 get_profile_manager()
│   ├── manager.py      # 프로파일 CRUD
│   ├── models.py       # QualityProfile 모델
│   └── validator.py    # 프로파일 검증

# 프로파일 구조
{
    "name": "print_ready",
    "description": "인쇄용 품질 검사",
    "quality_standards": {
        "min_dpi": 300,
        "max_ink_coverage": 320,
        "min_text_size": 6
    },
    "check_options": {
        "check_fonts": true,
        "check_colors": true,
        "check_images": true
    }
}
```

## 🐛 주요 패턴과 안티패턴

### 현재 사용 중인 패턴
1. **싱글톤 패턴** - @lru_cache 기반
2. **팩토리 패턴** - CheckerFactory, FixerFactory
3. **빌더 패턴** - ReportBuilder, HTMLBuilder
4. **파이프라인 패턴** - 처리 단계 체인
5. **옵저버 패턴** - UI 콜백 시스템
6. **전략 패턴** - 프로파일별 검사 전략

### 발견된 안티패턴과 해결책

#### 1. Bare except (일부 해결됨)
```python
# 안티패턴
try:
    operation()
except:  # 모든 예외 무시
    pass

# 해결책
try:
    operation()
except SpecificException as e:
    logger.error(f"작업 실패: {e}")
```

#### 2. 동적 import (미해결)
```python
# 안티패턴
def process():
    from module import Class  # 매번 import

# 해결책
from module import Class  # 파일 상단

def process():
    instance = Class()
```

#### 3. 순환 의존성 (일부 존재)
```python
# 문제
# A.py imports B
# B.py imports A

# 해결책
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from B import BClass  # 타입 체크 시에만
```

## 📊 성능 최적화 포인트

### 현재 최적화 상태
| 영역 | 현재 상태 | 개선 가능성 | 우선순위 |
|------|-----------|-------------|----------|
| 워커 풀 | CPU 기반 동적 설정 ✅ | - | 완료 |
| 메모리 사용 | 스트리밍 처리 부분 적용 | 대용량 PDF 최적화 필요 | 중간 |
| import 시간 | 동적 import 존재 | 정적 import로 변경 | 높음 |
| 캐싱 | 기본 캐싱 구현 | Redis 연동 가능 | 낮음 |
| DB 쿼리 | 기본 SQLite | 인덱스 최적화 필요 | 중간 |

### 성능 측정 코드
```python
import time
import psutil
import tracemalloc

# 메모리 프로파일링
tracemalloc.start()

# 작업 실행
start_time = time.time()
process = psutil.Process()
start_memory = process.memory_info().rss / 1024 / 1024  # MB

# ... 작업 코드 ...

end_time = time.time()
end_memory = process.memory_info().rss / 1024 / 1024  # MB

print(f"실행 시간: {end_time - start_time:.2f}초")
print(f"메모리 사용: {end_memory - start_memory:.2f}MB")

# 메모리 스냅샷
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

## 🔒 보안 고려사항

### 현재 구현된 보안 기능
1. **경로 검증** - Path 객체 사용으로 경로 주입 방지
2. **SQL 인젝션 방지** - 파라미터화된 쿼리 사용
3. **파일 권한 체크** - 읽기/쓰기 권한 확인
4. **임시 파일 정리** - atexit 핸들러로 자동 정리

### 추가 필요한 보안 조치
```python
# 1. 입력 검증 강화
def validate_pdf_path(path: Path) -> bool:
    if not path.exists():
        return False
    if not path.suffix.lower() == '.pdf':
        return False
    if path.stat().st_size > 500 * 1024 * 1024:  # 500MB 제한
        return False
    return True

# 2. 민감 정보 로깅 방지
def safe_log_path(path: Path) -> str:
    """경로에서 사용자 정보 제거"""
    parts = path.parts
    if len(parts) > 3:
        return f".../{'/'.join(parts[-2:])}"
    return str(path)

# 3. 리소스 제한
import resource
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, -1))  # 2GB 메모리 제한
```

## 🧪 테스트 전략

### 현재 테스트 구조
```
tests/
├── unit/           # 단위 테스트
├── integration/    # 통합 테스트
├── fixtures/       # 테스트용 PDF 파일
└── conftest.py     # pytest 설정
```

### 권장 테스트 커버리지
| 컴포넌트 | 현재 | 목표 | 우선순위 |
|----------|------|------|----------|
| Core (Analyzers/Checkers) | ~30% | 80% | 높음 |
| Processing (Queue/Pipeline) | ~20% | 70% | 높음 |
| UI Controllers | ~10% | 50% | 중간 |
| Utils/Helpers | ~40% | 60% | 낮음 |

### 테스트 작성 템플릿
```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

class TestComponent(unittest.TestCase):
    
    def setUp(self):
        """각 테스트 전 실행"""
        self.component = Component()
        self.mock_logger = Mock()
    
    def tearDown(self):
        """각 테스트 후 실행"""
        # 리소스 정리
        pass
    
    def test_normal_case(self):
        """정상 케이스 테스트"""
        result = self.component.process(valid_input)
        self.assertEqual(result, expected_output)
    
    def test_edge_case(self):
        """경계 케이스 테스트"""
        with self.assertRaises(ValueError):
            self.component.process(invalid_input)
    
    @patch('module.external_dependency')
    def test_with_mock(self, mock_dep):
        """외부 의존성 모킹"""
        mock_dep.return_value = Mock(status='success')
        result = self.component.process_with_dependency()
        mock_dep.assert_called_once()
        self.assertTrue(result)
```

## 🔄 CI/CD 구축 가이드

### GitHub Actions 워크플로우 (권장)
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8
    
    - name: Lint with flake8
      run: |
        flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src --count --exit-zero --max-line-length=120 --statistics
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks (권장)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.10
        
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120', '--ignore=E203,W503']
```

## 📈 향후 개선 로드맵

### Phase 1: 기술 부채 해결 (1-2주)
- [ ] Bare except 완전 제거
- [ ] 동적 import 제거
- [ ] 순환 의존성 해결
- [ ] 기본 테스트 작성

### Phase 2: 성능 최적화 (2-4주)
- [ ] 메모리 프로파일링
- [ ] 대용량 PDF 스트리밍 처리
- [ ] DB 인덱스 최적화
- [ ] 캐싱 전략 개선

### Phase 3: 아키텍처 개선 (1-2개월)
- [ ] 의존성 주입 컨테이너
- [ ] 이벤트 버스 구현
- [ ] 플러그인 시스템 확장
- [ ] 마이크로서비스 준비

### Phase 4: 엔터프라이즈 기능 (2-3개월)
- [ ] 멀티테넌시 지원
- [ ] REST API 서버
- [ ] 웹 UI 개발
- [ ] 클라우드 배포

## 🎓 핵심 학습 포인트

### 이 프로젝트에서 배울 수 있는 것
1. **대규모 Python 애플리케이션 구조**
   - 모듈화 전략
   - 패키지 구조 설계
   - 의존성 관리

2. **디자인 패턴 실전 적용**
   - 싱글톤, 팩토리, 빌더
   - 파이프라인, 전략, 옵저버

3. **PDF 처리 기술**
   - pikepdf, PyMuPDF 활용
   - 인쇄 품질 검사 로직
   - 자동 수정 알고리즘

4. **GUI 애플리케이션 개발**
   - CustomTkinter 활용
   - MVC 패턴 구현
   - 이벤트 기반 프로그래밍

5. **비동기 처리**
   - 멀티스레딩
   - 큐 기반 작업 처리
   - 워커 풀 관리

---

*이 문서는 PDF Quality Checker v2.0의 기술적 측면을 깊이 있게 이해하기 위한 가이드입니다.*
*추가 질문이나 구체적인 구현 방법이 필요하면 해당 섹션을 참조하세요.*

**마지막 업데이트**: 2025-01-15