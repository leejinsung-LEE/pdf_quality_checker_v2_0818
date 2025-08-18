# 📚 PDF Quality Checker v2.0 - UI 리뉴얼 컨텍스트 문서

## 🎯 프로젝트 개요

**PDF Quality Checker v2.0**의 GUI를 전면 리뉴얼한 프로젝트입니다.
환경설정 UI를 현대적으로 개선하고, 메뉴바를 정리하여 사용성을 향상시켰습니다.

### 주요 목표
- 환경설정을 7개 탭에서 4개 카테고리로 통합
- 언어 설정 제거 (한국어 전용)
- 사이드바 네비게이션 도입
- 즉시 적용 모드 구현
- 기존 UI와의 호환성 유지

## 🏗️ 아키텍처 구조

### 1. 새로운 컴포넌트 구조

```
src/ui/
├── views/
│   ├── settings/              # 기존 환경설정 (레거시)
│   └── settings_v2/           # 새로운 환경설정
│       ├── __init__.py
│       ├── settings_view_v2.py    # 메인 뷰 클래스
│       ├── navigation.py          # 사이드바 네비게이션
│       ├── search_bar.py          # 설정 검색 기능
│       ├── base_category.py       # 카테고리 기본 클래스
│       └── categories/
│           ├── general_category.py      # 일반 설정
│           ├── processing_category.py   # 처리 설정
│           ├── notification_category.py # 알림 설정
│           └── advanced_category.py     # 고급 설정
└── components/
    ├── menubar.py             # 기존 메뉴바 (레거시)
    └── menubar_v2.py          # 새로운 메뉴바
```

### 2. 통합 메커니즘

#### 환경변수 기반 전환
```python
# 환경변수로 UI 버전 제어
os.environ['USE_NEW_UI'] = 'true'  # 새 UI 사용
os.environ['USE_NEW_UI'] = 'false' # 기존 UI 사용
```

#### DialogManager 통합
```python
# src/ui/windows/main_window/dialog_manager.py
class DialogManager:
    def __init__(self, window):
        self.use_new_ui = self._check_new_ui_preference()
    
    def show_preferences(self):
        if self.use_new_ui and SETTINGS_V2_AVAILABLE:
            self._show_preferences_v2()  # 새 UI
        else:
            self._show_preferences_legacy()  # 기존 UI
```

#### UIBuilder 통합
```python
# src/ui/windows/main_window/ui_builder.py
def _create_menubar(self):
    use_new_ui = self._check_use_new_ui()
    
    if use_new_ui and MENUBAR_V2_AVAILABLE:
        self.window.menubar = MenuBarV2(self.window)
    else:
        self.window.menubar = MenuBar(self.window)
```

## 🔧 기술적 세부사항

### 1. SettingsViewV2 특징

#### 즉시 적용 모드
```python
def _on_setting_change(self, setting_key: str, value: Any):
    """설정 변경 시 즉시 적용"""
    # 변경사항 추적
    self.modified_fields.add(setting_key)
    
    # 즉시 적용
    self.settings_controller.update_setting(setting_key, value)
    
    # 이벤트 발행
    self.event_bus.emit(EventType.SETTING_CHANGED, data={...})
```

#### 4개 카테고리 구조
```python
CATEGORIES = [
    CategoryInfo(id="general", name="일반 설정", icon="🔧"),
    CategoryInfo(id="processing", name="처리 설정", icon="⚙️"),
    CategoryInfo(id="notification", name="알림 설정", icon="🔔"),
    CategoryInfo(id="advanced", name="고급 설정", icon="🛠️")
]
```

#### 검색 기능
```python
# 설정 검색 구현
def _on_search(self, query: str):
    for category in self.CATEGORIES:
        if query in category.keywords:
            self.category_widgets[category.id].search_settings(query)
```

### 2. 데이터 호환성

#### user_settings.json 구조
```json
{
  "theme": "dark",
  "language": "ko",  // 무시됨 (한국어 전용)
  "auto_start_watching": false,
  "minimize_to_tray": false,
  "sidebar_width": 216,
  "alarm_settings": {...},
  "column_visibility": {...}
}
```

#### 설정 마이그레이션
- 기존 설정 파일과 100% 호환
- 새로운 설정 항목은 기본값 사용
- 언어 설정은 무시하고 한국어 고정

### 3. 이벤트 시스템

```python
# 이벤트 타입
EventType.SETTING_CHANGED
EventType.SETTINGS_APPLIED
EventType.SETTINGS_CLOSED
EventType.UI_VERSION_TOGGLED
```

## 🚀 사용 가이드

### 1. 새 UI 활성화

#### 방법 1: 환경변수
```bash
# Windows
set USE_NEW_UI=true
python main.py

# Linux/Mac
export USE_NEW_UI=true
python main.py
```

#### 방법 2: 프로그램 내에서
```
메뉴 > 도움말 > UI 버전 전환
```

### 2. 테스트 실행

```bash
# 테스트 스크립트 실행
python test_new_ui.py
```

### 3. 개발자 API

#### SettingsViewV2 사용
```python
from src.ui.views.settings_v2 import SettingsViewV2

# 환경설정 창 열기
settings = SettingsViewV2(parent_window)

# 콜백 설정 (옵션)
settings.on_close = lambda: print("설정 창 닫힘")
```

#### 새 카테고리 추가
```python
class CustomCategory(BaseCategory):
    def _create_ui(self):
        section = self.create_section("커스텀 설정", "🎨")
        self.create_option_row(section, "옵션:", "switch", "custom_option")
```

## 📊 구현 상태

### ✅ 완료된 기능
1. **환경설정 리뉴얼**
   - 사이드바 네비게이션
   - 4개 카테고리 통합
   - 언어 설정 제거
   - 검색 기능
   - 즉시 적용 모드

2. **메뉴바 개선**
   - 미구현 기능 제거
   - 일관된 아이콘 사용
   - UI 버전 전환 메뉴

3. **통합 및 호환성**
   - 조건부 UI 로딩
   - 기존 설정 파일 호환
   - 레거시 UI 폴백

### ⚠️ 미완성 기능
1. **UI 일관성 (20%)**
   - 디자인 시스템 미구현
   - 컴포넌트 표준화 필요
   - 전체 앱 적용 필요

2. **사용성 개선 (25%)**
   - 컨텍스트 메뉴 없음
   - 툴팁 시스템 없음
   - 키보드 단축키 미완성

3. **테스트 (60%)**
   - 단위 테스트 없음
   - 통합 테스트 부분적
   - 성능 테스트 필요

## 🐛 알려진 이슈

1. **성능 이슈**
   - 대량 설정 변경 시 지연 가능
   - 이벤트 버스 최적화 필요

2. **UI 이슈**
   - 다크 모드에서 일부 색상 부적절
   - 고DPI 디스플레이 스케일링 문제

3. **호환성 이슈**
   - 일부 커스텀 설정 미지원
   - 외부 도구 경로 검증 불완전

## 🔄 향후 개발 계획

### Phase 1: 안정화 (1주)
- [ ] 버그 수정
- [ ] 성능 최적화
- [ ] 에러 처리 강화

### Phase 2: 완성 (2주)
- [ ] UI 일관성 개선
- [ ] 사용성 기능 추가
- [ ] 테스트 커버리지 확대

### Phase 3: 확장 (1개월)
- [ ] 플러그인 시스템
- [ ] 테마 커스터마이징
- [ ] 다국어 지원 (선택적)

## 📝 개발 노트

### 주요 결정 사항
1. **언어 설정 제거**: 한국어만 사용하므로 불필요
2. **즉시 적용**: 사용자 경험 향상을 위해 채택
3. **레거시 호환**: 점진적 마이그레이션 지원

### 기술 부채
1. 과도한 모듈화로 인한 복잡도
2. 이벤트 시스템 의존성
3. 테스트 부족

### 교훈
- "단순함이 복잡함보다 낫다" - Python의 Zen
- 완벽한 리팩토링보다 점진적 개선
- 사용자 피드백 기반 개발 중요

## 🤝 기여 가이드

### 코드 스타일
- PEP 8 준수
- 타입 힌트 필수
- 한국어 주석 사용

### 커밋 메시지
```
feat: 새 기능 추가
fix: 버그 수정
refactor: 코드 개선
docs: 문서 업데이트
test: 테스트 추가
```

### 테스트 요구사항
- 새 기능은 테스트 필수
- 기존 테스트 통과 확인
- UI 테스트는 선택적

## 📞 연락처

- 프로젝트: PDF Quality Checker v2.0
- 팀: PDF Quality Checker Team
- 작성일: 2025-01-17
- 최종 수정: 2025-01-17

---

**이 문서는 Claude에게 전달하여 프로젝트 컨텍스트를 빠르게 이해할 수 있도록 작성되었습니다.**