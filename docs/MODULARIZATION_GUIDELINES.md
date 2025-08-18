# PDF Quality Checker v2.0 - 모듈화 가이드라인

## 📌 개요
본 문서는 PDF Quality Checker v2.0 프로젝트의 모듈화 기준과 방법론을 정의합니다.
작성일: 2025-01-11

## 🎯 모듈화 목표

### 핵심 원칙
1. **단일 책임 원칙 (SRP)**: 각 모듈은 하나의 명확한 책임만 가짐
2. **AI 처리 최적화**: 100-200줄 단위로 분할하여 AI 도구 효율성 극대화
3. **기능 유지 보장**: 모든 기존 기능이 정상 작동하도록 보장
4. **API 호환성**: 기존 코드와의 호환성 유지

### 목표 지표
- **최대 파일 크기**: 250줄 (권장 150-200줄)
- **최소 파일 크기**: 50줄 (너무 작은 분할 방지)
- **평균 목표**: 150줄

## 📏 모듈화 기준

### 1. 크기 기준
```
50줄 미만     : 분할 불필요 (다른 모듈과 통합 고려)
50-250줄      : 적정 크기 ✅
250-500줄     : 분할 권장 ⚠️
500-1000줄    : 분할 필요 🔶
1000줄 이상   : 즉시 분할 필수 🔴
```

### 2. 복잡도 기준
- **클래스당 메서드 수**: 최대 15개
- **메서드당 라인 수**: 최대 30줄
- **중첩 레벨**: 최대 4단계
- **순환 복잡도**: 10 이하

### 3. 의존성 기준
- **import 수**: 모듈당 최대 10개
- **순환 의존성**: 절대 금지
- **결합도**: 낮게 유지 (느슨한 결합)

## 🏗️ 모듈화 구조

### 표준 디렉토리 구조
```python
module_name/
├── __init__.py      # 공개 API export
├── base.py          # 기본 클래스 (100-150줄)
├── ui_builders.py   # UI 구성 요소 (150-200줄)
├── handlers.py      # 이벤트 핸들러 (150-200줄)
├── actions.py       # 사용자 액션 (150-200줄)
└── utils.py         # 유틸리티 함수 (50-100줄)
```

### 파일별 역할 정의

#### `__init__.py`
```python
"""
모듈명 설명
기능: 주요 기능 요약
최종 수정: YYYY-MM-DD
"""

from .base import MainClass

__all__ = ['MainClass']  # 공개 API 명시
```

#### `base.py`
- 메인 클래스 정의
- 초기화 및 기본 설정
- 헬퍼 클래스 조합
- 150줄 이내 유지

#### `ui_builders.py`
- UI 컴포넌트 생성
- 레이아웃 구성
- 위젯 스타일링
- 200줄 이내 유지

#### `handlers.py`
- 이벤트 처리 로직
- 콜백 함수
- 사용자 입력 처리
- 200줄 이내 유지

#### `actions.py`
- 비즈니스 로직
- 데이터 처리
- 외부 시스템 연동
- 200줄 이내 유지

## 📝 모듈화 프로세스

### Step 1: 분석
```python
# 1. 현재 파일 크기 측정
wc -l target_file.py

# 2. 함수/클래스 개수 확인
grep -c "^def " target_file.py
grep -c "^class " target_file.py

# 3. 의존성 분석
grep "^import\|^from" target_file.py
```

### Step 2: 계획 수립
1. **기능 그룹핑**: 관련 기능끼리 묶기
2. **의존성 매핑**: import 관계 파악
3. **분할 경계 설정**: 논리적 단위로 분리
4. **목표 크기 설정**: 각 모듈 150-200줄

### Step 3: 모듈 생성
```bash
# 디렉토리 생성
mkdir src/ui/views/module_name

# 기본 파일 생성
touch src/ui/views/module_name/__init__.py
touch src/ui/views/module_name/base.py
touch src/ui/views/module_name/ui_builders.py
touch src/ui/views/module_name/handlers.py
touch src/ui/views/module_name/actions.py
```

### Step 4: 코드 이동
1. **base.py**: 클래스 정의, 초기화
2. **ui_builders.py**: UI 생성 메서드
3. **handlers.py**: 이벤트 핸들러
4. **actions.py**: 비즈니스 로직

### Step 5: 헬퍼 클래스 패턴
```python
# base.py
class MainView:
    def __init__(self):
        self.ui_builder = UIBuilder(self)
        self.handler = EventHandler(self)
        self.action = ActionHandler(self)
        
        self._create_ui()
    
    def _create_ui(self):
        self.ui_builder.create_ui()

# ui_builders.py
class UIBuilder:
    def __init__(self, view):
        self.view = view
    
    def create_ui(self):
        # UI 생성 로직
```

### Step 6: API 호환성 유지
```python
# __init__.py에서 기존 클래스 export
from .base import ProcessMonitorView

# 기존 import 방식 유지
# from views.process_monitor_view import ProcessMonitorView
# 이제: from views.process_monitor import ProcessMonitorView
```

## ✅ 체크리스트

### 모듈화 전 체크리스트
- [ ] 백업 생성 (git commit)
- [ ] 현재 파일 크기 측정
- [ ] 기능 그룹 식별
- [ ] 의존성 분석
- [ ] 테스트 케이스 준비

### 모듈화 중 체크리스트
- [ ] 디렉토리 구조 생성
- [ ] 코드 논리적 분리
- [ ] 각 파일 200줄 이하 확인
- [ ] import 정리
- [ ] 순환 참조 검사

### 모듈화 후 체크리스트
- [ ] 모든 import 동작 확인
- [ ] 기능 테스트 실행
- [ ] API 호환성 확인
- [ ] 문서 업데이트
- [ ] 커밋 및 태깅

## 🔍 검증 방법

### 1. Import 테스트
```python
# 모듈 import 테스트
python -c "from src.ui.views.module_name import MainClass; print('Success')"
```

### 2. 기능 테스트
```python
# test_functionality.py 실행
python test_functionality.py
```

### 3. 라인 수 검증
```bash
# 모든 파일이 250줄 이하인지 확인
find src/ui/views/module_name -name "*.py" -exec wc -l {} \; | sort -rn
```

### 4. 순환 참조 검사
```python
# 순환 참조 검사 스크립트
import sys
import importlib

def check_circular_import(module_name):
    try:
        importlib.import_module(module_name)
        return True
    except ImportError as e:
        if "circular import" in str(e):
            return False
        raise
```

## 📊 모듈화 효과

### Before (단일 파일)
- **파일 크기**: 1000+ 줄
- **AI 처리 시간**: 10-15초
- **수정 난이도**: 높음
- **테스트 난이도**: 높음
- **버그 추적**: 어려움

### After (모듈화)
- **파일 크기**: 150-200줄
- **AI 처리 시간**: 2-3초 (5배 향상)
- **수정 난이도**: 낮음
- **테스트 난이도**: 낮음
- **버그 추적**: 쉬움

## 🚨 주의사항

### 1. 과도한 분할 방지
- 50줄 미만의 파일 생성 지양
- 논리적 단위 유지
- 관련 기능은 함께 유지

### 2. 기능 유실 방지
- 모든 public 메서드 유지
- 기존 시그니처 변경 금지
- 테스트로 검증

### 3. 성능 고려
- 과도한 import 방지
- 순환 참조 절대 금지
- 메모리 사용량 모니터링

## 📚 참고 자료

### 성공 사례
1. **process_monitor_view 모듈화**
   - Before: 1079줄 단일 파일
   - After: 5개 모듈 (평균 200줄)
   - 결과: AI 처리 속도 3배 향상

2. **app.py 정리**
   - Before: 1880줄 (중복 포함)
   - After: 166줄
   - 결과: 91% 코드 감소

### 실패 사례 및 교훈
1. **과도한 분할**: 10줄짜리 파일 20개 생성 → 관리 복잡도 증가
2. **순환 참조**: 헬퍼 클래스가 서로 참조 → import 오류
3. **API 변경**: 기존 메서드 시그니처 변경 → 호환성 문제

## 🔄 지속적 개선

### 모니터링 지표
- 평균 파일 크기
- 최대 파일 크기
- import 깊이
- 테스트 커버리지
- AI 처리 시간

### 개선 목표
- 모든 파일 200줄 이하 유지
- 테스트 커버리지 80% 이상
- AI 처리 시간 5초 이내
- 순환 참조 0건

## 📮 문의 및 지원

모듈화 관련 문의사항이나 개선 제안은 프로젝트 이슈 트래커에 등록해주세요.

---
*Last Updated: 2025-01-11*
*Version: 1.0*