# 📚 PDF Quality Checker v2.0 - 문서 인덱스
*최종 업데이트: 2025-01-16*

## 🗂️ 문서 구조

### 📁 [session/2025-01-15/](session/2025-01-15/)
**최신 세션 작업 컨텍스트**
- [NEXT_SESSION_CONTEXT_20250115.md](session/2025-01-15/NEXT_SESSION_CONTEXT_20250115.md) - 다음 세션 시작 가이드
- [QUICK_START_COMMANDS_20250115.md](session/2025-01-15/QUICK_START_COMMANDS_20250115.md) - 빠른 시작 명령어 모음
- [REMAINING_TASKS_CONTEXT_20250115.md](session/2025-01-15/REMAINING_TASKS_CONTEXT_20250115.md) - 남은 작업 상세 목록
- [TECHNICAL_ANALYSIS_20250115.md](session/2025-01-15/TECHNICAL_ANALYSIS_20250115.md) - 기술 분석 보고서
- [TECHNICAL_DEBT_CONTEXT_20250115.md](session/2025-01-15/TECHNICAL_DEBT_CONTEXT_20250115.md) - 기술 부채 분석

### 📁 [prompts/](prompts/)
**프롬프트 및 템플릿**
- [PROMPTS.md](prompts/PROMPTS.md) - 코드 품질 관리 프롬프트 모음

### 📁 [guides/](guides/)
**사용 가이드**
- [SESSION_GUIDE_README.md](guides/SESSION_GUIDE_README.md) - 세션 가이드 활용법
- [NEW_FEATURES_GUIDE.md](NEW_FEATURES_GUIDE.md) - 새 기능 가이드
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - 마이그레이션 가이드

### 📁 [technical/](technical/)
**기술 문서**
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API 문서
- [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md) - 기술 노트
- [TECHNICAL_DEBT_REVIEW_20250109.md](TECHNICAL_DEBT_REVIEW_20250109.md) - 기술 부채 리뷰

### 📁 [design/](design/)
**설계 문서**
- [IMPOSITION_MODULE_DESIGN.md](IMPOSITION_MODULE_DESIGN.md) - 판짜기 모듈 설계
- [REALTIME_COLLABORATION_DESIGN.md](REALTIME_COLLABORATION_DESIGN.md) - 실시간 협업 설계

### 📁 [reports/](reports/)
**분석 및 보고서**
- [COMPREHENSIVE_ANALYSIS_REPORT_20250111_UPDATED.md](COMPREHENSIVE_ANALYSIS_REPORT_20250111_UPDATED.md) - 종합 분석 보고서
- [IMPROVEMENT_COMPLETION_REPORT_20250111.md](IMPROVEMENT_COMPLETION_REPORT_20250111.md) - 개선 완료 보고서
- [2025-01-09_PROJECT_IMPROVEMENT_REPORT.md](2025-01-09_PROJECT_IMPROVEMENT_REPORT.md) - 프로젝트 개선 보고서

### 📁 [modularization/](modularization/)
**모듈화 진행 문서** (40개 문서)
- 모듈화 Phase 1-7 진행 상황
- 교훈 및 롤백 기록
- [README.md](modularization/README.md) - 모듈화 문서 인덱스

### 📁 [old_docs/](old_docs/)
**이전 버전 문서 및 백업**
- 초기 설계 명세서
- v1 백업 참조
- Modern UI 백업
- 이전 작업 컨텍스트

## 🔍 빠른 참조

### 🚀 새 세션 시작하기
1. [NEXT_SESSION_CONTEXT](session/2025-01-15/NEXT_SESSION_CONTEXT_20250115.md) 읽기
2. [QUICK_START_COMMANDS](session/2025-01-15/QUICK_START_COMMANDS_20250115.md) 참조
3. 루트의 [CLAUDE.md](../CLAUDE.md) 지침 확인

### 📋 현재 작업 상태
- **완료**: 싱글톤 패턴 통일, Bare except 제거 (높음/중간), 문서 정리
- **진행 중**: 테스트 작성
- **대기**: 성능 테스트, UI 응답 시간 측정

### 🛠️ 주요 명령어
```bash
# 프로젝트 실행
cd C:\Users\wp\Desktop\pdf_quality_checker_v2
python main.py --fast

# 테스트 실행
python -m pytest tests/unit/test_singleton_patterns.py -v

# Git 상태 확인
git status
```

## 📌 중요 문서 위치

| 문서 | 위치 | 설명 |
|------|------|------|
| **CLAUDE.md** | 루트 디렉토리 | Claude Code 작업 지침 |
| **README.md** | 루트 디렉토리 | 프로젝트 개요 |
| **세션 컨텍스트** | docs/session/2025-01-15/ | 최신 작업 상태 |
| **프롬프트** | docs/prompts/ | 코드 품질 관리 |
| **모듈화 기록** | docs/modularization/ | Phase 1-7 진행 기록 |

## 🔄 업데이트 이력

- **2025-01-16**: 문서 구조 재정리 완료
  - 세션 컨텍스트 파일들을 session/2025-01-15/로 이동
  - PROMPTS.md를 prompts/로 이동
  - SESSION_GUIDE_README.md를 guides/로 이동
  - INDEX.md 생성

## 💡 팁

- 새 세션 시작 시 항상 세션 컨텍스트 문서를 먼저 확인
- 작업 전 CLAUDE.md의 지침 준수
- 모듈화 관련 작업 시 modularization/ 폴더의 교훈 참고
- 기술 부채 해결 시 session/2025-01-15/의 분석 문서 활용

---

**네비게이션**: [프로젝트 루트](../) | [CLAUDE.md](../CLAUDE.md) | [README.md](../README.md)