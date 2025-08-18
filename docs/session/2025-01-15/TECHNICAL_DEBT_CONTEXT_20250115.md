# PDF Quality Checker v2.0 - 기술 부채 및 모듈화 이슈 컨텍스트
*작성일: 2025-01-15*
*작성자: Claude*

## 📋 요약
이 문서는 PDF Quality Checker v2.0의 모듈화 과정(Phase 1-7)에서 발생한 기술 부채와 아키텍처 불일치를 체계적으로 정리한 것입니다. 
새로운 개발자나 AI 어시스턴트가 프로젝트를 이어받을 때 즉시 현황을 파악하고 작업할 수 있도록 작성되었습니다.

## 🚨 즉시 수정이 필요한 Critical Issues

### 1. ✅ QualityProfile 인터페이스 불일치 (해결 완료 - 2025-01-16)
**문제**: UI 컨트롤러가 존재하지 않는 속성에 직접 접근

**해결 내역**:
- src/core/profiles/profile_manager/models.py:82-95에 @property 추가 완료
- quality_standards, check_options, description 속성 접근자 구현
- 모든 UI 컨트롤러에서 정상 동작 확인

```python
# 해결된 코드 (models.py:82-95)
@property
def quality_standards(self) -> Dict[str, Any]:
    """품질 기준 속성 접근자"""
    return self.data.get('quality_standards', {})

@property
def check_options(self) -> Dict[str, Any]:
    """검사 옵션 속성 접근자"""
    return self.data.get('check_options', {})

@property
def description(self) -> str:
    """설명 속성 접근자"""
    return self.data.get('description', '')
```

### 2. ✅ SettingsController의 _tool_manager 속성 오류 (해결됨)
**문제**: 존재하지 않는 인스턴스 변수 참조
```python
# 잘못된 코드
if self._tool_manager is None:  # AttributeError!

# 올바른 코드
from src.external import get_tool_manager
tool_manager = get_tool_manager()
```

**영향 범위**:
- src/ui/controllers/settings_controller/external_tools.py:79

### 3. 타입 불일치 경고 ⚠️
**문제**: 설정값 타입 불일치
- `auto_start_watching`: bool 예상, int 실제
- 원인: JSON 저장/로드 시 타입 변환 누락

## 🏗️ 아키텍처 레벨 이슈

### 1. 모듈화 일관성 부족
**과도하게 모듈화된 영역**:
- history_manager: 658줄 → 1486줄 (227% 증가)
- data_manager: 396줄 → 1074줄 (271% 증가)
- main_window: 693줄 → 973줄 (140% 증가)

**모듈화가 필요한데 안 된 영역**:
- src/ui/components/menubar.py (500+ 줄)
- src/external/tool_manager.py (332줄, 복잡한 로직)

### 2. 순환 의존성 위험
```
ProfileController → ProfileManager → QualityProfile
         ↑                                    ↓
    ProfileInfo ← _create_profile_info ← to_dict()
```

### 3. 싱글톤 패턴 불일치
- ProfileManager: 전역 변수 방식 (`_profile_manager`)
- HistoryManager: @lru_cache 방식 (스레드 안전)
- ToolManager: 전역 변수 방식 (`_tool_manager`)

**통일 필요**: 모두 @lru_cache 방식으로 통일 권장

## ✅ 해결 완료 사항 (2025-01-15)

### 메서드 인터페이스 불일치
1. **QualityProfile 속성 접근**:
   - 해결: @property 데코레이터 추가 (models.py)
   - quality_standards, check_options, description 속성 접근 가능

2. **SettingsController tool_manager**:
   - 해결: 동적 속성 접근 로직 추가 (external_tools.py)
   - hasattr() 체크 후 get_tool_manager() 폴백

3. **ProfileInfo 문자열 변환**:
   - 해결: ProfileInfo 객체를 name 속성으로 변환 (ui_builder.py, profile_selector.py)
   - OptionMenu에 전달 시 문자열 리스트로 변환

## 📝 발견된 메서드 호출 오류 (수정 완료)

### ✅ 수정 완료 목록
1. **ProfileManager**: 
   - `get_all_profiles()` → `profiles.values()` 
   - 수정 파일: profile_controller/*.py (3개)

2. **HistoryManager**:
   - `get_history_by_date_range()` → `search_history()`
   - 수정 파일: statistics_dashboard/data_processor.py

## 🔄 리팩토링 필요 사항

### 1. 단기 (1-2주)
- [ ] QualityProfile 클래스에 property 데코레이터 추가
- [ ] SettingsController의 tool_manager 접근 방식 수정
- [ ] 타입 힌트 불일치 수정 (mypy 실행 필요)
- [ ] 중복된 ProfileManager 클래스명 정리
  - src/core/profiles/profile_manager/manager.py
  - src/ui/controllers/profile_controller/profile_manager.py
  - src/ui/views/profile_settings/profile_manager.py

### 2. 중기 (1개월)
- [ ] 모듈 간 인터페이스 명세 문서화
- [ ] 단위 테스트 작성 (현재 0% 커버리지)
- [ ] 통합 테스트 작성
- [ ] 과도한 모듈화 롤백 검토
  - 특히 10개 이상 파일로 분리된 모듈

### 3. 장기 (3개월)
- [ ] MVC 패턴 일관성 개선
- [ ] 이벤트 버스 패턴 도입 (모듈 간 통신)
- [ ] 의존성 주입 컨테이너 도입
- [ ] 플러그인 아키텍처 완성

## 🧪 테스트 전략

### 우선순위 1: 핵심 기능 테스트
```python
# tests/test_profile_manager.py
def test_profile_property_access():
    """QualityProfile 속성 접근 테스트"""
    profile = QualityProfile("test", {
        "quality_standards": {"min_dpi": 300},
        "check_options": {"allow_rgb": False}
    })
    assert profile.quality_standards["min_dpi"] == 300
    assert profile.check_options["allow_rgb"] == False

# tests/test_history_manager.py  
def test_search_history_date_range():
    """날짜 범위 검색 테스트"""
    manager = get_history_manager()
    results = manager.search_history(
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now()
    )
    assert isinstance(results, list)
```

### 우선순위 2: 통합 테스트
- GUI 컴포넌트 간 상호작용
- 파일 처리 파이프라인
- 프로파일 적용 및 검사

## 📊 모듈 의존성 그래프

```
src/
├── core/
│   ├── profiles/
│   │   └── profile_manager/ (모듈화됨)
│   │       ├── models.py ← 인터페이스 불일치 주의!
│   │       ├── manager.py
│   │       └── crud_operations.py
│   └── checkers/
├── data/
│   ├── history_manager/ (모듈화됨)
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── search_engine.py ← search_history() 메서드
│   └── data_manager/ (모듈화됨)
├── ui/
│   ├── controllers/
│   │   ├── profile_controller/ (모듈화됨)
│   │   │   └── base.py ← QualityProfile 속성 직접 접근 오류
│   │   └── settings_controller/
│   │       └── external_tools.py ← _tool_manager 오류
│   └── views/
│       └── statistics_dashboard/
│           └── data_processor.py ← 수정 완료
└── external/
    └── tool_manager.py ← 싱글톤 패턴
```

## 🔍 디버깅 가이드

### 실행 시 발생하는 경고/오류 처리
1. **QualityProfile 속성 오류**: 
   - 로그: `'QualityProfile' object has no attribute 'quality_standards'`
   - 임시 해결: try-except로 감싸기
   - 근본 해결: property 추가

2. **SettingsController 오류**:
   - 로그: `'SettingsController' object has no attribute '_tool_manager'`
   - 해결: self.tool_manager 또는 get_tool_manager() 사용

3. **타입 불일치 경고**:
   - 로그: `타입 불일치: auto_start_watching 예상=bool, 실제=int`
   - 해결: JSON 로드 시 타입 변환 로직 추가

## 💡 권장 작업 순서

1. **즉시 (오늘)**: 
   - QualityProfile에 property 추가
   - SettingsController의 tool_manager 수정

2. **이번 주**:
   - 타입 힌트 검증 (mypy)
   - 기본 단위 테스트 작성

3. **다음 주**:
   - 모듈 간 인터페이스 문서화
   - 중복 코드 제거

4. **이번 달**:
   - 과도한 모듈화 검토 및 조정
   - 통합 테스트 구축

## 📚 참고 문서
- `CLAUDE.md`: 프로젝트 작업 지침
- `PDF Quality Checker v2.0 - 확장형 프로젝트 설계 명세서.md`: 원래 설계
- `MODULARIZATION_STATUS_REPORT.md`: 모듈화 진행 상황 (삭제됨)
- `docs/MIGRATION_GUIDE.md`: 마이그레이션 가이드

## ⚡ Quick Fix 스크립트

```python
# quick_fix.py - 즉시 실행 가능한 수정 스크립트
import sys
sys.path.insert(0, 'C:\\Users\\wp\\Desktop\\pdf_quality_checker_v2')

# 1. QualityProfile 속성 추가
def patch_quality_profile():
    from src.core.profiles.profile_manager.models import QualityProfile
    
    # Property 동적 추가
    QualityProfile.quality_standards = property(
        lambda self: self.data.get('quality_standards', {})
    )
    QualityProfile.check_options = property(
        lambda self: self.data.get('check_options', {})
    )
    QualityProfile.description = property(
        lambda self: self.data.get('description', '')
    )
    print("✅ QualityProfile 패치 완료")

# 2. 실행
if __name__ == "__main__":
    patch_quality_profile()
    print("Quick fix 적용 완료!")
```

## 🎯 성공 지표
- [x] main.py 실행 시 오류 없음 ✅
- [x] 모든 뷰 정상 표시 ✅
- [x] 프로파일 전환 정상 작동 ✅
- [x] 통계 대시보드 데이터 표시 ✅
- [x] 외부 도구 설정 접근 가능 ✅
- [ ] 메모리 누수 없음 (1시간 실행) - 테스트 필요
- [ ] 응답 시간 < 100ms (UI 작업) - 측정 필요

---

**마지막 업데이트**: 2025-01-15
**다음 리뷰**: 2025-01-22

이 문서를 참고하여 작업하시면 현재 프로젝트의 모든 기술 부채와 이슈를 파악하고 체계적으로 해결할 수 있습니다.