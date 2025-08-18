# 기존 GUI 구조 분석
> PDF Quality Checker v2.0 - CustomTkinter 기반 Classic UI 상세 분석

## 📁 현재 구조

```
src/ui/
├── app.py                    # 애플리케이션 진입점
├── windows/
│   └── main_window.py        # 메인 윈도우 (tkinterdnd2.Tk)
├── views/                    # 화면 뷰
│   ├── dashboard_view.py     # 대시보드 (통계, 차트)
│   ├── processing_view.py    # 파일 처리 화면
│   ├── history_view.py       # 히스토리 조회
│   ├── settings_view.py      # 설정 화면
│   └── folder_manager_view.py # 폴더 관리
├── components/               # UI 컴포넌트
│   ├── sidebar.py           # 좌측 사이드바
│   ├── menubar.py           # 상단 메뉴바
│   └── statusbar.py         # 하단 상태바
└── controllers/             # 컨트롤러 (MVC)
    ├── file_controller.py   # 파일 처리 로직
    ├── settings_controller.py # 설정 관리
    └── profile_controller.py  # 프로파일 관리
```

## 🎨 레이아웃 구조

### 메인 윈도우 레이아웃
```
┌─────────────────────────────────────────────┐
│                  MenuBar                     │
├──────┬──────────────────────────────────────┤
│      │                                       │
│  S   │         Content Area                  │
│  i   │    (ProcessingView/DashboardView/     │
│  d   │     HistoryView/SettingsView)         │
│  e   │                                       │
│  b   │                                       │
│  a   │                                       │
│  r   │                                       │
│      │                                       │
├──────┴──────────────────────────────────────┤
│                 StatusBar                    │
└─────────────────────────────────────────────┘
```

## 🔧 주요 컴포넌트

### 1. MainWindow (main_window.py)
- **기반**: `tkinterdnd2.Tk` (드래그앤드롭 지원)
- **크기**: 1400x800 (최소 1200x600)
- **테마**: CustomTkinter Dark Mode

**주요 기능:**
```python
- 윈도우 설정 및 초기화
- 뷰 전환 관리
- 컨트롤러 통합
- 폴더 감시자 관리
- 단축키 바인딩
```

### 2. Sidebar (sidebar.py)
- **위치**: 왼쪽 고정
- **너비**: 200px
- **구성 요소**:
  - 로고/타이틀
  - 네비게이션 버튼 (대시보드, 처리, 히스토리, 폴더, 설정)
  - 빠른 액션 버튼
  - 프로파일 선택

### 3. MenuBar (menubar.py)
**메뉴 구조:**
```
파일
├── 열기 (Ctrl+O)
├── 폴더 열기
├── 최근 파일
├── 설정
└── 종료 (Ctrl+Q)

편집
├── 프로파일 관리
├── 품질 기준 설정
└── 외부 도구 설정

보기
├── 대시보드
├── 파일 처리
├── 히스토리
└── 통계

도구
├── 배치 처리
├── 폴더 감시 시작/중지
├── 캐시 정리
└── 로그 보기

도움말
├── 사용 설명서
├── 단축키
└── 정보
```

### 4. StatusBar (statusbar.py)
- **좌측**: 현재 상태 메시지
- **중앙**: 진행 상황 바
- **우측**: 처리 통계, 시간

## 📊 주요 뷰 상세

### ProcessingView (processing_view.py)
**구성 요소:**
- 드래그앤드롭 영역
- 파일 목록 테이블
- 처리 옵션 패널
- 실시간 로그 출력
- 진행 상황 표시

**기능:**
- 단일/다중 파일 처리
- 실시간 상태 업데이트
- 처리 중단/재시작
- 결과 미리보기

### DashboardView (dashboard_view.py)
**구성 요소:**
- 통계 카드 (총 처리, 성공률, 평균 시간, 오류)
- 차트 영역 (matplotlib)
- 최근 파일 리스트
- 빠른 액션 버튼

**차트 종류:**
- 일간/주간/월간 처리 통계
- 품질 분포 차트
- 오류 유형 분석
- 처리 시간 추이

### HistoryView (history_view.py)
**구성 요소:**
- 검색/필터 바
- 히스토리 테이블
- 상세 정보 패널
- 액션 버튼 (재처리, 삭제, 내보내기)

### SettingsView (settings_view.py)
**설정 카테고리:**
1. **일반 설정**
   - UI 테마
   - 언어
   - 자동 업데이트

2. **처리 설정**
   - 기본 프로파일
   - 병렬 처리 수
   - 캐시 설정

3. **품질 기준**
   - 이미지 DPI
   - 색상 프로파일
   - 폰트 임베딩

4. **외부 도구**
   - Ghostscript 경로
   - pdffonts 경로
   - 임시 폴더

### FolderManagerView (folder_manager_view.py)
**구성 요소:**
- 감시 폴더 목록
- 폴더 설정 패널
- 규칙 편집기
- 실시간 모니터링

## 🎮 컨트롤러 구조

### FileController
```python
class FileController:
    def process_file(self, file_path: str, profile: str)
    def batch_process(self, files: List[str])
    def get_status(self, file_id: str) -> FileStatus
    def cancel_processing(self, file_id: str)
```

### SettingsController
```python
class SettingsController:
    def load_settings() -> Dict
    def save_settings(settings: Dict)
    def get_setting(key: str) -> Any
    def set_setting(key: str, value: Any)
```

### ProfileController
```python
class ProfileController:
    def get_profiles() -> List[str]
    def load_profile(name: str) -> Dict
    def save_profile(name: str, settings: Dict)
    def delete_profile(name: str)
```

## 🔌 이벤트 시스템

### 주요 이벤트
```python
# 파일 처리
on_file_dropped(files: List[str])
on_process_start(file_id: str)
on_process_complete(file_id: str, results: Dict)
on_process_error(file_id: str, error: Exception)

# UI 상태
on_view_change(view_name: str)
on_theme_change(theme: str)
on_window_resize(width: int, height: int)

# 설정
on_settings_change(key: str, value: Any)
on_profile_change(profile_name: str)
```

## 🎨 스타일 시스템

### CustomTkinter 테마
```python
# 색상 팔레트
COLORS = {
    "primary": "#1e88e5",
    "secondary": "#424242",
    "success": "#43a047",
    "warning": "#fb8c00",
    "error": "#e53935",
    "surface": "#2b2b2b",
    "background": "#1e1e1e"
}

# 폰트 설정
FONTS = {
    "default": ("Segoe UI", 10),
    "heading": ("Segoe UI", 14, "bold"),
    "small": ("Segoe UI", 9)
}
```

## 📦 의존성

### 필수 패키지
- `customtkinter`: 모던 UI 컴포넌트
- `tkinterdnd2`: 드래그앤드롭
- `matplotlib`: 차트/그래프
- `Pillow`: 이미지 처리

### 선택적 패키지
- `darkdetect`: 시스템 테마 감지
- `CTkMessagebox`: 향상된 메시지박스
- `CTkTable`: 테이블 위젯

## 🔄 데이터 흐름

```
User Action → View → Controller → Core Logic
                ↑                      ↓
            UI Update ← Event ← Processing Result
```

## ⚡ 성능 최적화

### 현재 적용된 최적화
1. **가상 스크롤**: 큰 리스트 처리
2. **레이지 로딩**: 필요시 컴포넌트 로드
3. **스레드 풀**: 백그라운드 작업
4. **캐싱**: 자주 사용하는 데이터

### 병목 지점
- matplotlib 차트 렌더링
- 대용량 파일 목록 표시
- 실시간 업데이트 시 깜빡임

## 🚀 Modern GUI 이전 시 고려사항

### 1:1 매핑 필요 항목
- [ ] 모든 메뉴 기능
- [ ] 단축키 시스템
- [ ] 드래그앤드롭
- [ ] 실시간 업데이트
- [ ] 설정 저장/불러오기

### 개선 가능 영역
- 애니메이션 추가
- 부드러운 전환 효과
- 더 나은 차트 라이브러리
- 반응형 레이아웃
- 터치 제스처 지원

---

*이 문서는 Modern GUI 구현 시 참조 문서로 활용됩니다.*