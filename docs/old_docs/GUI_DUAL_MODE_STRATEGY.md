# GUI 이중화 전략 문서
> PDF Quality Checker v2.0 - Classic/Modern UI 병행 운영 계획

## 📋 개요
기존 CustomTkinter GUI(Classic)와 현대적인 Flet GUI(Modern)를 병행 운영하여 안정성을 유지하면서 점진적으로 UI를 개선합니다.

## 🎯 목표
1. **무중단 전환**: 기존 기능 손상 없이 새 UI 테스트
2. **사용자 선택권**: 상황에 따라 UI 모드 선택 가능
3. **점진적 마이그레이션**: 기능별로 단계적 이전
4. **코드 재사용**: 비즈니스 로직 100% 재활용

## 🏗️ 아키텍처

### 디렉토리 구조
```
src/
├── core/           # 비즈니스 로직 (공통)
├── processing/     # 처리 엔진 (공통)
├── config/         # 설정 관리 (공통)
├── utils/          # 유틸리티 (공통)
├── ui/
│   ├── classic/    # CustomTkinter GUI (기존)
│   │   ├── windows/
│   │   ├── views/
│   │   ├── components/
│   │   └── controllers/
│   └── modern/     # Flet GUI (신규)
│       ├── windows/
│       ├── views/
│       ├── components/
│       └── controllers/
└── main.py         # 진입점 (UI 선택 로직)
```

### UI 모드 선택 방식
```python
# 1. 커맨드라인 인자
python main.py --ui classic  # 기존 GUI
python main.py --ui modern   # 새 GUI

# 2. 설정 파일 (config/settings.json)
{
    "ui_mode": "classic",  // 또는 "modern"
    "allow_ui_switch": true
}

# 3. 환경 변수
PDF_CHECKER_UI=modern python main.py

# 4. 첫 실행 시 선택 다이얼로그
```

## 📊 기능 매핑 테이블

| 기능 | Classic (CustomTkinter) | Modern (Flet) | 상태 |
|------|-------------------------|---------------|------|
| **레이아웃** |
| 사이드바 | ✅ Sidebar 컴포넌트 | NavigationRail | 🔄 |
| 메뉴바 | ✅ MenuBar | AppBar + Menu | 🔄 |
| 상태바 | ✅ StatusBar | BottomBar | 🔄 |
| 탭 전환 | ✅ CTkTabview | NavigationBar | 🔄 |
| **주요 뷰** |
| 대시보드 | ✅ DashboardView | DashboardView | 🔄 |
| 파일 처리 | ✅ ProcessingView | ProcessingView | 🔄 |
| 히스토리 | ✅ HistoryView | HistoryView | 🔄 |
| 폴더 관리 | ✅ FolderManagerView | FolderManagerView | 🔄 |
| **기능** |
| 드래그앤드롭 | ✅ tkinterdnd2 | Flet DragTarget | 🔄 |
| 파일 선택 | ✅ filedialog | FilePicker | 🔄 |
| 실시간 업데이트 | ✅ after() | async update | 🔄 |
| 차트/그래프 | ✅ matplotlib | Flet Charts | 🔄 |
| 썸네일 | ✅ CTkImage | Image widget | 🔄 |
| **설정** |
| 프로파일 관리 | ✅ | 동일 구현 필요 | ⏳ |
| 품질 기준 설정 | ✅ | 동일 구현 필요 | ⏳ |
| 외부 도구 경로 | ✅ | 동일 구현 필요 | ⏳ |
| 테마 설정 | ✅ Dark/Light | Material You | 🔄 |

상태: ✅ 완료 | 🔄 진행중 | ⏳ 대기 | ❌ 미구현

## 🔄 전환 단계

### Phase 1: 기반 구축 (현재)
- [x] UI 모드 전환 시스템 설계
- [ ] main.py 수정 (UI 선택 로직)
- [ ] 기본 Modern UI 프레임 구축
- [ ] 컨트롤러 인터페이스 통일

### Phase 2: 읽기 전용 뷰
- [ ] 대시보드 (통계 표시)
- [ ] 히스토리 조회
- [ ] 리포트 뷰어
- [ ] 설정 보기

### Phase 3: 기본 상호작용
- [ ] 파일 선택/드래그앤드롭
- [ ] 프로파일 선택
- [ ] 설정 변경 및 저장
- [ ] 검색/필터링

### Phase 4: 핵심 기능
- [ ] 실시간 파일 처리
- [ ] 폴더 감시
- [ ] 배치 처리
- [ ] 자동 수정

### Phase 5: 고급 기능
- [ ] 차트/통계 분석
- [ ] 리포트 생성
- [ ] 내보내기/가져오기
- [ ] 플러그인 시스템

## 🧪 테스트 전략

### A/B 테스트 항목
1. **성능 비교**
   - 시작 시간
   - 메모리 사용량
   - CPU 사용률
   - 렌더링 속도

2. **기능 동등성**
   - 모든 기능 작동 확인
   - 결과 일치성 검증
   - 에러 처리 동일성

3. **사용성 테스트**
   - 직관성
   - 반응 속도
   - 시각적 피드백
   - 접근성

### 롤백 시나리오
```python
# 자동 폴백 로직
try:
    if ui_mode == "modern":
        from ui.modern import ModernApp
        app = ModernApp()
except Exception as e:
    logger.warning(f"Modern UI 실패: {e}")
    logger.info("Classic UI로 자동 전환")
    from ui.classic import ClassicApp
    app = ClassicApp()
```

## 💡 핵심 고려사항

### 데이터 흐름
```
User Input → UI Layer (Classic/Modern)
              ↓
         Controller (공통 인터페이스)
              ↓
         Business Logic (core/processing)
              ↓
         Data Layer (파일, DB)
```

### 설정 호환성
- 두 UI 모드는 동일한 설정 파일 사용
- 설정 변경은 양쪽에 즉시 반영
- UI별 특수 설정은 별도 섹션으로 관리

### 이벤트 처리
```python
# 공통 이벤트 인터페이스
class UIEventHandler(ABC):
    @abstractmethod
    def on_file_dropped(self, files: List[str]): pass
    
    @abstractmethod
    def on_process_start(self): pass
    
    @abstractmethod
    def on_process_complete(self, results): pass
```

## 🚀 구현 우선순위

1. **즉시 구현** (오늘)
   - main.py UI 선택 로직
   - Modern UI 기본 프레임
   - 설정 파일 UI 모드 옵션

2. **단기 구현** (이번 주)
   - 대시보드 뷰 (읽기 전용)
   - 파일 드래그앤드롭
   - 기본 설정 화면

3. **중기 구현** (이번 달)
   - 파일 처리 기능
   - 폴더 감시
   - 리포트 생성

4. **장기 구현**
   - 성능 최적화
   - 고급 차트/분석
   - 플러그인 시스템

## 📝 개발 규칙

1. **모든 비즈니스 로직은 UI와 독립적으로**
2. **컨트롤러는 UI 중립적 인터페이스 제공**
3. **UI별 특수 기능은 별도 모듈로 격리**
4. **테스트는 양쪽 UI 모두 수행**
5. **커밋 시 UI 모드 명시**

## 🔍 모니터링 지표

- UI 모드별 사용 통계
- 에러 발생률 비교
- 성능 메트릭 수집
- 사용자 피드백 추적

## 📅 마일스톤

- **M1** (1주): 기본 이중화 구조 완성
- **M2** (2주): 읽기 전용 기능 구현
- **M3** (1개월): 핵심 기능 동등성 달성
- **M4** (2개월): 전체 기능 구현
- **M5** (3개월): 최적화 및 안정화

---

*이 문서는 지속적으로 업데이트됩니다.*
*최종 수정: 2025-08-08*