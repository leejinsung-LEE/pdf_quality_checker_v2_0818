# Claude Code 지침 - PDF Quality Checker v2.0

## 기본 동작 설정
- **모든 작업에 대해 항상 심층 분석 수행**
- 코드 작성, 수정, 분석 전 충분한 사고 과정 거치기
- 의사 결정 시 여러 대안 고려 후 최적안 선택

## 언어 설정
- 항상 한국어로 대화하고 응답하기
- 코드 주석은 한국어로 작성
- 변수명, 함수명, 클래스명은 영어로 작성

## UI 정보
- **Classic UI(CustomTkinter) 전용 시스템**
- Modern UI 관련 코드는 docs/old_docs/modern_ui_backup에 백업됨

## 프로젝트 구조
- 모듈 경로: src/core/, src/processing/, src/ui/, src/external/, src/config/, src/utils/
- MVC 패턴 준수 (ui/views/, ui/controllers/, ui/components/)
- 파이프라인 아키텍처 활용
- 향후 판짜기(Imposition) 기능 확장을 고려한 설계 유지

## 코딩 스타일
- Python 3.10+ 기능 활용
- PEP 8 준수
- 타입 힌트 필수 (typing 모듈 활용)
- dataclass 적극 활용
- 추상 클래스와 인터페이스 활용 (base_analyzer.py, base_checker.py 패턴)

## 작업 방식
- **기본값**: 모든 작업에서 자동으로 심층 분석 수행
  - 아키텍처 영향도 평가
  - 모듈 간 의존성 고려
  - 잠재적 버그 및 엣지 케이스 검토
  - 성능 영향 분석
  - 향후 확장성 고려
- **필수**: 작업 전 반드시 기존 코드와의 연동성 및 통일성 검토
  - 설계 명세서 참조 (PDF Quality Checker v2.0 - 확장형 프로젝트 설계 명세서.md)
  - 기존 모듈의 패턴과 스타일 분석
  - 의존성 관계 확인 (requirements.txt 참조)
  - 모듈 간 인터페이스 일관성 유지
- **품질 관리 필수 적용**: 
  - 코드 작성/수정 시작 시 반드시 PROMPTS.md 파일을 읽고 해당 상황에 맞는 프롬프트 적용
  - 특히 중요한 작업 시 적용할 프롬프트:
    * 새 기능 추가: #1 (아키텍처 영향도), #2 (기술 부채 방지)
    * 리팩토링: #4 (리팩토링 안전성), #10 (기술 부채 탐지)
    * 버그 수정: #5 (코드 리뷰), #7 (에러 처리)
    * 성능 개선: #6 (성능 최적화), #8 (확장성 검증)
- 작업 전 TodoWrite 도구로 계획 수립 및 추적
- 핵심 기능과 복잡한 로직에 대한 테스트 코드 작성
  - tests/unit/: 단위 테스트
  - tests/integration/: 통합 테스트  
  - tests/fixtures/: 테스트용 PDF 파일
- 에러 처리와 로깅 철저히 (src/utils/logger.py 활용)

## 기술 스택
- GUI: CustomTkinter (모던 UI)
- PDF 처리: pikepdf, PyMuPDF (fitz)
- 외부 도구: Ghostscript, pdffonts (poppler)
- 파일 감시: watchdog
- 향후: pdftk, pdfnup (판짜기용)

## 품질 기준 (src/config/constants.py 참조)
- 최소 이미지 DPI: 300
- 표준 재단선: 3mm
- 최대 잉크 커버리지: 320%
- 최소 텍스트 크기: 6pt

## 개발 우선순위
1. Phase 1: 핵심 데이터 모델과 기본 분석기
2. Phase 2: 품질 검사기와 프로파일 시스템
3. Phase 3: GUI 구현 (MVC 패턴)
4. Phase 4: 자동 수정과 배치 처리
5. Phase 5: 성능 최적화와 에러 처리
6. Phase 6: 판짜기 기능 (향후)

## 모듈화 지침

### 모듈화 결정 기준 (2025-01-15 업데이트)
- **파일 크기별 기준**:
  - **200줄 미만**: 모듈화 불필요 (단일 파일 유지)
  - **200-500줄**: 복잡도에 따라 선택적 모듈화
    - 단순 로직: 모듈화 불필요
    - 복잡한 비즈니스 로직: 모듈화 고려
  - **500-1000줄**: 모듈화 권장 (명확한 책임 분리 시)
  - **1000줄 이상**: 모듈화 필수
  
- **복잡도별 기준**:
  - 단일 책임만 가진 클래스: 모듈화 불필요
  - 3개 이상의 명확한 책임: 모듈화 권장
  - 외부 의존성이 많은 경우: 모듈화 권장
  - 독립적 테스트가 필요한 경우: 모듈화 권장

- **과도한 모듈화 방지**:
  - ❌ 100줄 미만 파일을 별도 모듈로 분리 금지
  - ❌ 단순 enum, constants만 있는 파일 분리 금지
  - ❌ 유틸리티 함수 3-4개만 있는 파일 분리 금지
  - ✅ 명확한 책임 분리가 있을 때만 모듈화
  - ✅ 코드 재사용성이 높을 때만 모듈화

- **권장 원칙**: 새로운 기능 추가 시 가능한 한 모듈 단위로 구현
  - 단일 책임 원칙(SRP) 준수
  - 각 모듈은 독립적으로 테스트 가능하도록 설계
  - 모듈 간 느슨한 결합(Loose Coupling) 유지
  - 인터페이스 기반 설계로 의존성 주입 활용
  - 단, 간단한 유틸리티나 헬퍼 함수는 기존 모듈에 통합 가능
  
- **모듈 구조 패턴**:
  ```
  module_name/
  ├── __init__.py          # 공개 인터페이스 정의
  ├── base.py              # 추상 클래스/인터페이스
  ├── implementation.py    # 구체적 구현
  ├── models.py           # 데이터 모델 (dataclass)
  ├── utils.py            # 모듈 전용 유틸리티
  └── tests/              # 모듈 테스트
  ```

- **모듈 생성 체크리스트**:
  1. 기존 모듈과의 중복 기능 확인
  2. 파일 크기와 복잡도 기준 충족 여부 확인
  3. 추상 베이스 클래스 정의 (ABC 활용)
  4. 타입 힌트와 docstring 완성
  5. 단위 테스트 작성
  6. __init__.py에 공개 API 명시
  7. 의존성 최소화 및 순환 참조 방지
  8. 원본 파일 백업 유지 (.py.backup)
  9. 모듈화 후 즉시 import 테스트 수행
  
- **모듈 통합 규칙**:
  - 기존 파이프라인과의 호환성 확인
  - 설정 파일(config.yaml)에 모듈 설정 추가
  - 에러 처리 및 로깅 표준 준수
  - 성능 영향도 평가 후 최적화

### 모듈화 교훈 및 주의사항 (실제 경험 기반)
- **성공 사례**:
  - history_manager.py (658줄): 복잡한 DB 작업 분리로 유지보수성 향상
  - main_window.py (693줄): UI 컴포넌트별 분리로 협업 용이
  - streaming_processor.py (1000줄+): 대용량 처리 로직 분리로 테스트 개선
  
- **실패 사례 (롤백됨)**:
  - app.py (159줄 → 646줄): 과도한 분리로 복잡도만 증가
  - priority_manager.py (30줄): 너무 작은 파일 분리는 비효율적
  - enums.py (45줄): 단순 enum은 원본 파일에 유지
  
- **핵심 교훈**:
  - 코드량 증가 자체는 문제가 아니지만, 명확한 이익이 있어야 함
  - "단순함이 복잡함보다 낫다" - Python의 Zen
  - 모듈화는 수단이지 목적이 아님
  - 팀 협업과 테스트 용이성을 우선 고려

## 프로젝트 현황 (2025-01-15 업데이트)
### 완료된 작업
- **모듈화 Phase 1-7 완료**:
  - 핵심 모듈들을 독립적인 패키지로 분리
  - MVC 패턴 적용 및 컨트롤러 레이어 구현
  - 파이프라인 아키텍처 확립
  - 과도한 모듈화 4개 롤백 완료 (app.py, tool_manager.py, alarm_config.py, batch_processor.py)
  
### 현재 브랜치 상태
- **브랜치**: feature/modularization
- **모듈화 유지 (적절함)**:
  - src/data/history_manager/ (658줄 → 1486줄, 복잡한 DB 작업)
  - src/data/data_manager/ (396줄 → 1074줄, 데이터 관리)
  - src/processing/folder_watcher/ (589줄 → 825줄, 파일 감시)
  - src/processing/pipeline/ (441줄 → 701줄, 파이프라인 처리)
  - src/processing/processor/ (349줄 → 490줄, PDF 처리)
  - src/processing/queue_manager/ (큐 관리)
  - src/reporting/html_builder/ (HTML 리포트 생성)
  - src/ui/components/sidebar/ (사이드바 컴포넌트)
  - src/ui/controllers/*_controller/ (MVC 컨트롤러)
  - src/ui/views/folder_manager/ (폴더 관리 뷰)
  - src/ui/views/statistics_dashboard/ (통계 대시보드)
  - src/ui/windows/main_window/ (693줄 → 973줄, 메인 윈도우)
  
- **단일 파일 유지 (롤백됨)**:
  - src/ui/app.py (159줄)
  - src/external/tool_manager.py (332줄)
  - src/config/alarm_config.py (292줄)
  - src/processing/batch_processor.py (493줄)

### 주요 아키텍처 특징
- **파이프라인 기반 처리**: PDF 분석, 검사, 수정이 파이프라인으로 연결
- **MVC 패턴**: UI 레이어가 View-Controller-Model로 분리
- **이벤트 기반 통신**: 모듈 간 EventBus 패턴 활용
- **플러그인 아키텍처**: 새 기능을 플러그인으로 추가 가능
- **설정 중앙화**: config.yaml과 settings.json으로 통합 관리

### 다음 단계 고려사항
- 판짜기(Imposition) 기능 모듈 설계
- 성능 프로파일링 및 최적화
- 통합 테스트 스위트 구축
- CI/CD 파이프라인 설정


## 성능 고려사항
- 대용량 PDF 파일 처리 최적화
- 메모리 효율적인 스트리밍 처리
- 멀티스레딩 활용 (폴더 감시, 배치 처리)
- 캐싱 전략 (data/cache/ 활용)