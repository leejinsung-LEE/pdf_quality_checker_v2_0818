# PDF Quality Checker v2.0 - 설정창 이벤트 버스 통합

## 📅 작성일: 2025-01-17

## 🎯 목표
설정창 파일 구조는 유지하되, 이벤트 버스를 통합하여 컴포넌트 간 결합도를 낮춥니다.

## 1. 현재 상태

### 1.1 완료된 작업
- ✅ 이벤트 버스 시스템 구현 (`src/ui/events/`)
- ✅ 메인 윈도우 통합 (8개→3개 파일)
- ✅ 메뉴바 이벤트 버스 적용

### 1.2 설정창 현재 구조 (유지)
```
src/ui/views/settings/
├── __init__.py          # 150줄 - 모듈 통합
├── base.py              # 190줄 - 기본 클래스
├── general_tab.py       # 152줄 - 일반 설정
├── processing_tab.py    # 175줄 - 처리 설정
├── folders_tab.py       # 163줄 - 폴더 설정
├── interface_tab.py     # 202줄 - 인터페이스 설정
├── alarm_tab.py         # 395줄 - 알람 설정
├── advanced_tools_tab.py # 376줄 - 고급/도구 설정
└── handlers.py          # 285줄 - 이벤트 핸들러
총 9개 파일, 2,088줄
```

### 1.3 왜 파일 통합을 하지 않는가?
- **현재 구조가 이미 적절함**: 각 파일 150-400줄로 관리 가능한 크기
- **1200줄 파일의 문제점**: 스크롤 지옥, Git 충돌, 디버깅 어려움
- **CLAUDE.md 기준 준수**: 200-500줄은 "선택적 모듈화" 범위
- **진짜 문제는 구조가 아닌 결합도**

## 2. 작업 계획

### 2.1 Phase 1: 이벤트 타입 추가
```python
# src/ui/events/event_types.py에 추가
SETTINGS_OPENED = "settings_opened"
SETTINGS_CLOSED = "settings_closed"
SETTINGS_CHANGED = "settings_changed"
SETTINGS_APPLIED = "settings_applied"
SETTINGS_RESET = "settings_reset"

PROFILE_SELECTED = "profile_selected"
PROFILE_CREATED = "profile_created"
PROFILE_DELETED = "profile_deleted"

THEME_CHANGED = "theme_changed"
LANGUAGE_CHANGED = "language_changed"

FOLDER_OUTPUT_CHANGED = "folder_output_changed"
FOLDER_COMPLETE_CHANGED = "folder_complete_changed"
FOLDER_WATCH_ADDED = "folder_watch_added"
FOLDER_WATCH_REMOVED = "folder_watch_removed"

ALARM_ENABLED = "alarm_enabled"
ALARM_DISABLED = "alarm_disabled"
ALARM_CONFIG_CHANGED = "alarm_config_changed"

TOOL_PATH_CHANGED = "tool_path_changed"
TOOL_TEST_REQUESTED = "tool_test_requested"
```

### 2.2 Phase 2: 설정창에 이벤트 버스 통합
```python
# settings/base.py 수정
class SettingsViewBase:
    def __init__(self):
        # 이벤트 버스 초기화
        from ...events import EventBus, EventType
        self.event_bus = EventBus()
        
        # 기존 콜백도 유지 (하위 호환성)
        self.callbacks = {}
        
    def emit_event(self, event_type, data=None):
        """이벤트 발행 헬퍼"""
        self.event_bus.emit(event_type, data or {})
        
        # 기존 콜백도 호출 (하위 호환성)
        if event_type in self.callbacks:
            self.callbacks[event_type](data)
```

### 2.3 Phase 3: 각 탭에서 이벤트 발행
```python
# 예시: general_tab.py
def on_theme_change(self, theme):
    # 이벤트 발행
    self.parent.emit_event(EventType.THEME_CHANGED, {
        'theme': theme,
        'source': 'settings.general_tab'
    })
    
    # UI 업데이트
    ctk.set_appearance_mode(theme)
```

### 2.4 Phase 4: 메인 윈도우에서 이벤트 구독
```python
# main_window.py
def setup_event_listeners(self):
    self.event_bus.subscribe(EventType.THEME_CHANGED, self.on_theme_changed)
    self.event_bus.subscribe(EventType.SETTINGS_APPLIED, self.on_settings_applied)
    self.event_bus.subscribe(EventType.FOLDER_WATCH_ADDED, self.on_folder_watch_added)
```

## 3. 예상 개선 효과

### 3.1 결합도 감소
- **이전**: 설정창 ↔ 메인윈도우 직접 참조
- **이후**: 이벤트 버스를 통한 간접 통신

### 3.2 테스트 용이성
- 이벤트 모킹으로 단위 테스트 가능
- 컴포넌트 독립적 테스트

### 3.3 확장성
- 새 기능 추가 시 이벤트만 추가
- 기존 코드 수정 최소화

## 4. 작업 순서

1. **이벤트 타입 정의** (30분)
   - event_types.py에 설정 관련 이벤트 추가

2. **base.py 수정** (30분)
   - EventBus 초기화
   - emit_event 헬퍼 메서드 추가

3. **각 탭 수정** (2시간)
   - 중요한 액션에 이벤트 발행 추가
   - 기존 콜백 유지

4. **메인 윈도우 연동** (1시간)
   - 이벤트 구독 설정
   - 핸들러 구현

5. **테스트** (1시간)
   - 기능 동작 확인
   - 이벤트 흐름 검증

## 5. 새 세션 시작 문구

```markdown
PDF Quality Checker v2.0 프로젝트의 설정창 이벤트 버스 통합 작업을 진행하려고 합니다.

현재 상황:
- 이벤트 버스 시스템 구현 완료 (src/ui/events/)
- 메인 윈도우 통합 완료 (8개→3개 파일)
- 설정창은 현재 구조 유지 (9개 파일, 각 150-400줄)

작업 목표:
- 설정창에 이벤트 버스 통합
- 파일 구조는 그대로 유지 (이미 적절한 크기)
- 컴포넌트 간 느슨한 결합 달성

참고 문서:
- docs/SETTINGS_EVENT_BUS_INTEGRATION.md (작업 가이드)
- docs/PHASE1_EVENT_BUS_IMPLEMENTATION.md (이벤트 버스 구현)
- CLAUDE.md (프로젝트 지침)

브랜치: feature/gui-consolidation

설정창에 이벤트 버스를 통합해주세요. 
Phase 1부터 순서대로 진행하면 됩니다.
```

## 6. 체크리스트

- [ ] event_types.py에 설정 관련 이벤트 추가
- [ ] settings/base.py에 EventBus 통합
- [ ] 각 탭에서 주요 액션에 이벤트 발행
- [ ] 메인 윈도우에서 이벤트 구독
- [ ] 기존 기능 동작 테스트
- [ ] 이벤트 흐름 로깅으로 검증

## 7. 주의사항

1. **기존 콜백 유지**: 하위 호환성 필수
2. **점진적 적용**: 한 번에 모든 것을 바꾸지 말 것
3. **테스트 우선**: 각 단계마다 동작 확인
4. **문서화**: 새로운 이벤트는 반드시 문서화

## 8. 기대 효과

- **유지보수성**: 컴포넌트 간 독립성 증가
- **확장성**: 새 기능 추가 용이
- **테스트**: 모킹과 단위 테스트 가능
- **디버깅**: 이벤트 로그로 추적 용이

---

이 문서를 참고하여 설정창 이벤트 버스 통합을 진행하세요.
파일 구조는 건드리지 않고 이벤트 시스템만 추가하는 것이 핵심입니다.