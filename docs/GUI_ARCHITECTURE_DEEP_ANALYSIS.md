# PDF Quality Checker v2.0 - GUI 아키텍처 심층 분석 및 개선 계획

## 📅 작성일: 2025-01-17

## 1. 현재 아키텍처 심층 분석

### 1.1 전체 UI 컴포넌트 구조

```
PDF Quality Checker v2.0
│
├── main.py (195줄) - 진입점
│   └── MainWindow (tkinterdnd2.Tk 상속)
│
├── src/ui/app.py (161줄) - 애플리케이션 클래스
│   ├── PDFQualityCheckerApp
│   ├── 백그라운드 처리 스레드
│   └── 큐 시스템 관리
│
└── src/ui/windows/main_window/ (8개 모듈)
    ├── base.py - MainWindow 클래스
    ├── ui_builder.py - UI 생성
    ├── event_handler.py - 이벤트 처리
    ├── file_manager.py - 파일 관리
    ├── folder_watcher_manager.py - 폴더 감시
    ├── dialog_manager.py - 대화상자
    └── view_manager.py - 뷰 전환
```

### 1.2 메뉴 시스템 분석

#### 현재 메뉴 구조
```
파일 메뉴
├── 파일 열기 (Ctrl+O)
├── 폴더 열기 (Ctrl+Shift+O)
├── 최근 파일 →
└── 종료 (Ctrl+Q)

편집 메뉴
├── 환경설정 (Ctrl+,)
└── 프로파일 관리

보기 메뉴
├── 처리 화면 (F1)
├── 대시보드 (F2)
├── 통계 분석 (F3)
├── 프로파일 설정 (F4)
├── [체크] 사이드바
└── [체크] 상태바

도구 메뉴
├── 일괄 처리 (Ctrl+B)
├── 폴더 감시 설정
├── 배치 스케줄러 (Ctrl+S)
├── 백업 관리자 (Ctrl+R)
└── 보고서 내보내기

도움말 메뉴
├── 사용 설명서 (F1)
├── 업데이트 확인
└── 정보
```

### 1.3 이벤트 처리 구조 분석

#### 현재 이벤트 흐름
```
사용자 액션
    ↓
MenuBar/Sidebar/UI Component
    ↓
콜백 함수 (직접 바인딩)
    ↓
EventHandler (event_handler.py)
    ↓
각 Manager 클래스
    ↓
Controller 레이어
    ↓
비즈니스 로직
```

#### 문제점
1. **강한 결합**: 컴포넌트가 직접 콜백 참조
2. **순환 참조 위험**: 양방향 참조 존재
3. **테스트 어려움**: 모킹이 복잡
4. **확장성 부족**: 새 이벤트 추가 시 여러 파일 수정 필요

### 1.4 모듈화 수준 재평가

#### 적절한 모듈화 (유지)
✅ **Core 모듈들**: 비즈니스 로직 분리 적절
✅ **Processing 모듈들**: 대용량 처리에 필요
✅ **Data 모듈들**: 데이터 관리 책임 명확
✅ **Controllers**: MVC 패턴 준수

#### 과도한 모듈화 (검토 필요)
⚠️ **Settings 뷰**: 9개 파일 → 탭별 분리가 과도
⚠️ **Main Window**: 8개 파일 → 일부 통합 가능
⚠️ **작은 헬퍼들**: 100줄 미만 파일들

#### 부족한 부분
❌ **이벤트 시스템**: 중앙화된 이벤트 관리 부재
❌ **상태 관리**: 전역 상태 관리 체계 없음
❌ **플러그인 시스템**: 확장성 고려 부족

## 2. Phase 1: 메뉴 시스템 및 이벤트 아키텍처 개선

### 2.1 이벤트 버스 시스템 도입

#### 새로운 이벤트 시스템 설계
```python
# src/ui/events/event_bus.py
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    """이벤트 타입 정의"""
    # 파일 관련
    FILE_OPEN = "file.open"
    FILE_DROPPED = "file.dropped"
    FILE_PROCESSED = "file.processed"
    FILE_ERROR = "file.error"
    
    # 프로파일 관련
    PROFILE_CHANGED = "profile.changed"
    PROFILE_SAVED = "profile.saved"
    
    # UI 관련
    VIEW_CHANGED = "view.changed"
    SIDEBAR_TOGGLED = "sidebar.toggled"
    STATUSBAR_TOGGLED = "statusbar.toggled"
    
    # 폴더 감시
    FOLDER_WATCH_STARTED = "folder.watch.started"
    FOLDER_WATCH_STOPPED = "folder.watch.stopped"
    
    # 설정
    SETTINGS_CHANGED = "settings.changed"
    SETTINGS_SAVED = "settings.saved"

@dataclass
class Event:
    """이벤트 데이터 클래스"""
    type: EventType
    data: Dict[str, Any]
    source: str = ""
    timestamp: float = None

class EventBus:
    """중앙 이벤트 버스"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._listeners = {}
        return cls._instance
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """이벤트 구독"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def publish(self, event: Event):
        """이벤트 발행"""
        for callback in self._listeners.get(event.type, []):
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """구독 해제"""
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)
```

### 2.2 메뉴 시스템 재설계

#### 개선된 메뉴 액션 시스템
```python
# src/ui/components/menu/menu_actions.py
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class MenuAction:
    """메뉴 액션 정의"""
    id: str
    label: str
    event_type: EventType
    accelerator: Optional[str] = None
    icon: Optional[str] = None
    enabled: bool = True

class MenuDefinitions:
    """메뉴 정의 중앙화"""
    
    FILE_MENU = [
        MenuAction("file.open", "파일 열기...", EventType.FILE_OPEN, "Ctrl+O", "📁"),
        MenuAction("file.open_folder", "폴더 열기...", EventType.FILE_OPEN, "Ctrl+Shift+O", "📂"),
        # ... 더 많은 액션
    ]
    
    EDIT_MENU = [
        MenuAction("edit.preferences", "환경설정...", EventType.SETTINGS_CHANGED, "Ctrl+,", "⚙️"),
        MenuAction("edit.profiles", "프로파일 관리...", EventType.PROFILE_CHANGED, None, "👤"),
    ]
    
    # ... 다른 메뉴들

# src/ui/components/menu/menubar.py
class ImprovedMenuBar(tk.Menu):
    """개선된 메뉴바"""
    
    def __init__(self, parent, event_bus: EventBus):
        super().__init__(parent)
        self.event_bus = event_bus
        self.actions = {}
        self._build_menus()
    
    def _build_menus(self):
        """메뉴 구성"""
        for menu_name, actions in [
            ("파일", MenuDefinitions.FILE_MENU),
            ("편집", MenuDefinitions.EDIT_MENU),
            # ...
        ]:
            menu = tk.Menu(self, tearoff=0)
            self.add_cascade(label=menu_name, menu=menu)
            
            for action in actions:
                self._add_menu_item(menu, action)
    
    def _add_menu_item(self, menu: tk.Menu, action: MenuAction):
        """메뉴 아이템 추가"""
        menu.add_command(
            label=action.label,
            accelerator=action.accelerator,
            command=lambda: self._trigger_action(action),
            state=tk.NORMAL if action.enabled else tk.DISABLED
        )
        self.actions[action.id] = action
    
    def _trigger_action(self, action: MenuAction):
        """액션 트리거"""
        event = Event(
            type=action.event_type,
            data={"action_id": action.id},
            source="menubar"
        )
        self.event_bus.publish(event)
```

### 2.3 UI 컴포넌트 통합 전략

#### 현재 vs 개선안 비교

| 컴포넌트 | 현재 상태 | 개선안 | 이유 |
|---------|----------|--------|------|
| **MenuBar** | 단일 파일 (303줄) ✅ | 유지 + 이벤트 버스 | 적절한 크기 |
| **StatusBar** | 단일 파일 (174줄) ✅ | 유지 | 적절한 크기 |
| **Sidebar** | 5개 모듈 (800줄+) ⚠️ | 3개로 통합 | 과도한 분리 |
| **Settings** | 9개 모듈 (1370줄) ⚠️ | 4-5개로 통합 | 탭별 분리 과도 |
| **MainWindow** | 8개 모듈 (973줄) ⚠️ | 5개로 통합 | 일부 통합 가능 |

### 2.4 구체적 구현 계획

#### Step 1: 이벤트 버스 구현 (1일)
```
작업 내용:
1. src/ui/events/ 디렉토리 생성
2. event_bus.py - 이벤트 버스 구현
3. event_types.py - 이벤트 타입 정의
4. event_handlers.py - 핸들러 베이스 클래스
```

#### Step 2: 메뉴 시스템 개선 (1일)
```
작업 내용:
1. menu_actions.py - 액션 정의
2. menubar.py 리팩토링 - 이벤트 버스 통합
3. 단축키 매니저 구현
4. 컨텍스트 메뉴 지원
```

#### Step 3: MainWindow 통합 (2일)
```
현재 구조:
main_window/
├── base.py (144줄)
├── ui_builder.py (180줄)
├── view_manager.py (120줄)
├── event_handler.py (150줄)
├── file_manager.py (110줄)
├── folder_watcher_manager.py (95줄)
├── dialog_manager.py (130줄)
└── __init__.py (44줄)

개선안:
main_window/
├── main_window.py (300줄) - base + 핵심 로직
├── window_ui.py (250줄) - ui_builder + view_manager
├── window_managers.py (300줄) - file + folder + dialog
├── window_events.py (150줄) - 이벤트 버스 연동
└── __init__.py (20줄)
```

#### Step 4: 설정창 선택적 통합 (2일)
```
현재 구조:
settings/
├── base.py (190줄)
├── general_tab.py (120줄)
├── processing_tab.py (130줄)
├── folders_tab.py (100줄)
├── interface_tab.py (140줄)
├── alarm_tab.py (220줄)
├── advanced_tools_tab.py (200줄)
├── handlers.py (180줄)
└── __init__.py (150줄)

개선안:
settings/
├── settings_window.py (250줄) - base + 핵심
├── basic_tabs.py (350줄) - general + interface + folders
├── advanced_tabs.py (420줄) - processing + alarm + tools
├── settings_controller.py (350줄) - handlers + 로직
└── __init__.py (20줄)
```

## 3. 시각적 아키텍처 다이어그램

### 3.1 현재 이벤트 흐름
```
┌─────────────────────────────────────────────────┐
│                사용자 인터랙션                    │
└─────────────┬───────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│     UI 컴포넌트 (MenuBar, Sidebar, etc.)        │
│  ┌──────────────────────────────────────────┐   │
│  │   직접 콜백 참조 (강한 결합)              │   │
│  │   - menubar.callbacks['open_files']      │   │
│  │   - sidebar.on_files_dropped             │   │
│  └──────────────────────────────────────────┘   │
└─────────────┬───────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│         각 Manager 클래스들                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ File     │ │ Folder   │ │ Dialog   │       │
│  │ Manager  │ │ Watcher  │ │ Manager  │       │
│  └──────────┘ └──────────┘ └──────────┘       │
└─────────────┬───────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│              Controllers                         │
└──────────────────────────────────────────────────┘

문제: 컴포넌트 간 직접 참조, 순환 의존성 위험
```

### 3.2 개선된 이벤트 버스 아키텍처
```
┌─────────────────────────────────────────────────┐
│                사용자 인터랙션                    │
└─────────────┬───────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│     UI 컴포넌트 (이벤트 발행자)                 │
│  ┌──────────────────────────────────────────┐   │
│  │   이벤트 발행만 수행                      │   │
│  │   - event_bus.publish(FILE_OPEN)         │   │
│  │   - event_bus.publish(PROFILE_CHANGED)   │   │
│  └──────────────────────────────────────────┘   │
└─────────────┬───────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│            EVENT BUS (중앙 허브)                 │
│  ┌──────────────────────────────────────────┐   │
│  │  • 이벤트 라우팅                         │   │
│  │  • 구독/발행 관리                        │   │
│  │  • 비동기 처리 지원                      │   │
│  └──────────────────────────────────────────┘   │
└────────┬──────────┬──────────┬─────────────────┘
         ↓          ↓          ↓
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Handler1 │ │ Handler2 │ │ Handler3 │
│ (구독자) │ │ (구독자) │ │ (구독자) │
└──────────┘ └──────────┘ └──────────┘

장점: 느슨한 결합, 확장 용이, 테스트 가능
```

## 4. 예상 효과 및 리스크

### 4.1 예상 효과

#### 정량적 효과
- **파일 수**: 30% 감소 (UI 레이어)
- **코드 중복**: 20% 감소
- **import 깊이**: 평균 1-2단계 감소
- **테스트 커버리지**: 30% 향상 가능

#### 정성적 효과
- **유지보수성**: 관련 코드가 한 곳에
- **확장성**: 새 기능 추가 용이
- **가독성**: 명확한 이벤트 흐름
- **테스트**: 모킹과 단위 테스트 용이

### 4.2 리스크 및 대응

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|-----------|
| 기존 기능 누락 | 높음 | 체크리스트 작성, 단계별 테스트 |
| 이벤트 버스 성능 | 중간 | 프로파일링, 필요시 최적화 |
| 학습 곡선 | 낮음 | 문서화, 예제 코드 제공 |
| 롤백 필요성 | 중간 | 브랜치 작업, 백업 유지 |

## 5. 실행 로드맵

### Week 1: 기반 구축
- [ ] Day 1: 이벤트 버스 시스템 구현
- [ ] Day 2: 이벤트 타입 정의 및 테스트
- [ ] Day 3: 메뉴 시스템 이벤트 통합
- [ ] Day 4-5: MainWindow 모듈 통합

### Week 2: UI 개선
- [ ] Day 6-7: 설정창 선택적 통합
- [ ] Day 8: 사이드바 리팩토링
- [ ] Day 9: 통합 테스트
- [ ] Day 10: 문서화 및 최적화

## 6. 결론

### 핵심 전략
1. **모듈화는 유지하되 과도한 부분만 통합**
   - Core 비즈니스 로직: 현재 유지 ✅
   - UI 레이어: 선택적 통합 ⚡
   
2. **이벤트 버스로 느슨한 결합 달성**
   - 직접 참조 제거
   - 확장성 확보
   
3. **단계적 접근으로 리스크 최소화**
   - 백업 유지
   - 기능별 테스트
   - 롤백 가능한 구조

### 다음 단계
1. 이 분석 문서 검토
2. 우선순위 결정
3. Phase 1 시작 승인
4. 구현 시작

이 계획이 현재 프로젝트의 향후 확장성을 고려하면서도 
현실적인 개선을 제공한다고 판단됩니다.