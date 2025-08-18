# 📚 PDF Quality Checker v2.0 - 세션 가이드 문서 활용법
*작성일: 2025-01-15*

## 🎯 새로운 Claude 세션 시작 가이드

### 📋 준비된 문서들

#### 1. **NEXT_SESSION_CONTEXT_20250115.md** (메인 컨텍스트)
- **용도**: 새 세션의 첫 번째 참조 문서
- **내용**: 프로젝트 현황, 다음 작업 우선순위, 주의사항
- **언제 사용**: 세션 시작 시 가장 먼저 읽기

#### 2. **QUICK_START_COMMANDS_20250115.md** (실행 명령어)
- **용도**: 복사-붙여넣기로 즉시 실행 가능한 명령어
- **내용**: 테스트, 분석, 수정을 위한 구체적 명령어
- **언제 사용**: 실제 작업 시 참조

#### 3. **TECHNICAL_ANALYSIS_20250115.md** (기술 분석)
- **용도**: 코드베이스 깊은 이해가 필요할 때
- **내용**: 아키텍처, 패턴, 성능, 보안 분석
- **언제 사용**: 복잡한 문제 해결 시 참조

#### 4. **REMAINING_TASKS_CONTEXT_20250115.md** (전체 작업 현황)
- **용도**: 전체 기술 부채와 작업 목록 확인
- **내용**: 완료/미완료 작업 상세 목록
- **언제 사용**: 작업 우선순위 결정 시

## 🚀 새 세션 시작 순서

### Step 1: Claude에게 첫 메시지
```
안녕하세요! PDF Quality Checker v2.0 프로젝트 작업을 진행하려고 합니다.

프로젝트 경로: C:\Users\wp\Desktop\pdf_quality_checker_v2

다음 문서들을 참고해주세요:
1. NEXT_SESSION_CONTEXT_20250115.md - 메인 가이드
2. CLAUDE.md - 작업 지침

현재 최우선 작업은 "Bare except 제거 - 우선순위 중간 파일들" 입니다.
천천히 깊게 생각하며 작업해주세요.
```

### Step 2: 작업 시작 전 확인
```bash
# 1. 프로젝트 상태 확인
cd C:\Users\wp\Desktop\pdf_quality_checker_v2
git status

# 2. 앱 실행 테스트
python main.py --fast

# 3. 변경된 파일 확인
git diff --name-only
```

### Step 3: 구체적 작업 요청
```
QUICK_START_COMMANDS_20250115.md의 "Bare except 제거 작업" 섹션을 참고하여
다음 5개 파일의 bare except를 수정해주세요:

1. src/data/backup_manager/storage.py:175
2. src/data/backup_manager/cleanup.py:181
3. src/data/backup_manager/compression.py:139
4. src/processing/batch_scheduler/manager.py:239
5. src/data/history_manager/search_engine.py:125

각 파일을 수정한 후 테스트를 실행해주세요.
```

## 📝 작업별 참조 문서

### Bare except 제거 작업
- **메인**: NEXT_SESSION_CONTEXT_20250115.md의 "다음 작업 우선순위" 섹션
- **명령어**: QUICK_START_COMMANDS_20250115.md의 "Bare except 제거 작업" 섹션
- **패턴**: TECHNICAL_ANALYSIS_20250115.md의 "주요 패턴과 안티패턴" 섹션

### 동적 import 제거 작업
- **메인**: NEXT_SESSION_CONTEXT_20250115.md의 "동적 import 제거" 섹션
- **명령어**: QUICK_START_COMMANDS_20250115.md의 "동적 import 제거 작업" 섹션
- **분석**: TECHNICAL_ANALYSIS_20250115.md의 "성능 최적화 포인트" 섹션

### 테스트 작성
- **메인**: NEXT_SESSION_CONTEXT_20250115.md의 "기본 단위 테스트 작성" 섹션
- **명령어**: QUICK_START_COMMANDS_20250115.md의 "테스트 작성 및 실행" 섹션
- **전략**: TECHNICAL_ANALYSIS_20250115.md의 "테스트 전략" 섹션

## ⚡ 빠른 참조

### 현재 상태 요약
- ✅ **완료**: 싱글톤 패턴 통일, TODO 구현, 워커 풀 최적화
- 🔄 **진행 중**: Bare except 제거 (우선순위 높음 완료, 중간 대기)
- ⏳ **대기**: 동적 import 제거, 테스트 작성

### 주요 파일 위치
```
src/
├── core/           # 분석기, 검사기, 수정기
├── processing/     # 큐, 파이프라인, 워커
├── ui/            # MVC 구조 UI
├── data/          # 데이터 관리, 히스토리
├── config/        # 설정, 상수
└── utils/         # 유틸리티, 알람
```

### Git 작업 흐름
```bash
# 1. 작업 시작
git pull origin master

# 2. 수정 작업
# ... 코드 수정 ...

# 3. 테스트
python main.py --fast

# 4. 커밋
git add -p
git commit -m "refactor: [작업 내용]"

# 5. 푸시 (필요시)
git push origin master
```

## 🔍 문제 해결

### "파일을 찾을 수 없음" 오류
```bash
# 전체 경로 사용
cd C:\Users\wp\Desktop\pdf_quality_checker_v2
```

### Import 오류
```python
# 절대 경로로 변경
from src.core.profiles import ProfileManager
```

### 테스트 실패
```bash
# 디버그 모드로 실행
python main.py --fast --log-level DEBUG
```

## 💬 Claude와의 효과적인 대화

### DO ✅
- 구체적인 파일명과 라인 번호 제공
- 에러 메시지 전체 복사
- 작업 전후 git status 공유
- "천천히 깊게 생각하며" 요청

### DON'T ❌
- 여러 작업 동시 요청
- 테스트 없이 많은 변경
- 백업 없이 큰 리팩토링
- 컨텍스트 없이 작업 요청

## 📌 중요 참고사항

1. **호환성 래퍼 유지**: `src/ui/controllers/*.py` 파일들은 삭제 금지
2. **워커 수 제한**: 최대 8개 (시스템 안정성)
3. **Classic UI 전용**: Modern UI 코드는 백업에만 존재
4. **한국어 주석**: CLAUDE.md 지침에 따라 한국어 사용

---

### 🎯 오늘의 목표
1. Bare except 5개 파일 수정
2. 각 수정 후 테스트 실행
3. 의미 있는 단위로 커밋

### 📅 이번 주 목표
1. Bare except 완전 제거
2. 동적 import 제거
3. 기본 테스트 작성

### 🚀 이번 달 목표
1. 테스트 커버리지 50% 달성
2. CI/CD 파이프라인 구축
3. 성능 최적화 완료

---

**화이팅! 깊게 생각하고 꼼꼼하게 작업하세요!** 💪