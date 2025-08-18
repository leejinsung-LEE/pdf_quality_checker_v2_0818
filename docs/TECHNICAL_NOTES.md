# 📋 PDF Quality Checker v2.0 - 기술 노트 및 알려진 이슈

> **최종 업데이트**: 2025-08-08  
> **목적**: 현재 기술 부채, 알려진 이슈, 개선 사항 추적

---

## 🚨 현재 기술 부채

### 1. 인코딩 및 유니코드 문제
**문제**: Windows 환경에서 cp949 인코딩 오류 발생
```python
UnicodeEncodeError: 'cp949' codec can't encode character
```

**영향 범위**:
- `src/core/analyzers/*.py` - 이모지 포함 출력
- `src/processing/folder_watcher.py` - 로그 메시지
- 보고서 생성 시 특수 문자 처리

**해결 방안**:
- 모든 파일 열기 시 `encoding='utf-8'` 명시
- print 문에서 이모지 제거 또는 조건부 사용
- 로깅 시스템 UTF-8 설정 강제

**우선순위**: 높음

---

### 2. 워커 시스템 종료 오류
**문제**: ThreadPoolExecutor 종료 시 속성 오류
```python
AttributeError: 'ThreadPoolExecutor' object has no attribute '_futures'
```

**위치**: 
- `src/processing/queue_manager.py`
- `src/processing/processing_worker.py`

**현재 대응**: try-except로 오류 무시 중

**개선 필요**: 제대로 된 cleanup 로직 구현

**우선순위**: 중간

---

### 3. 중복 폴더 설정 저장
**문제**: `folder_watch_config.json`에 같은 폴더가 중복 저장됨

**영향**: 
- 같은 파일이 여러 번 처리될 가능성
- 불필요한 리소스 사용

**해결 방안**:
- 폴더 추가 시 중복 체크 로직 추가
- 절대 경로로 통일하여 비교

**우선순위**: 중간

---

### 4. 프로파일 로딩 실패
**문제**: 특정 프로파일 로딩 시 KeyError
```
[Warning] Failed to load profile quality_profiles.json: 'name'
```

**위치**: `src/core/profiles/profile_manager.py`

**영향**: 기본 프로파일로 폴백되지만 사용자 정의 프로파일 사용 불가

**우선순위**: 낮음

---

### 5. DashboardView matplotlib 폰트 경고
**문제**: 한글 폰트 렌더링 경고
```
UserWarning: Glyph 45936 (\N{HANGUL SYLLABLE DE}) missing from font(s)
```

**위치**: `src/ui/views/dashboard_view.py`

**영향**: 차트 한글 표시 문제

**해결 방안**: matplotlib 한글 폰트 설정 추가

**우선순위**: 낮음

---

## ⚠️ AI 코딩 시 주의사항

### 1. 타입 힌트 일관성 유지
```python
# 나쁜 예
def process_file(file_path):  # 타입 힌트 누락
    return result

# 좋은 예
from pathlib import Path
from typing import Optional

def process_file(file_path: Path) -> Optional[ProcessingResult]:
    return result
```

### 2. Import 정리
- 와일드카드 import (`from module import *`) 사용 금지
- 순환 참조 주의
- 사용하지 않는 import 제거

### 3. 경로 처리
- 항상 `pathlib.Path` 사용
- 절대 경로와 상대 경로 명확히 구분
- Windows/Unix 호환성 고려

### 4. 에러 처리
- 구체적인 예외 타입 사용
- 로깅 후 재발생 패턴 사용
- 사용자 친화적 에러 메시지

---

## 📈 향후 개선 사항

### 단기 (1-2주)
1. UTF-8 인코딩 문제 완전 해결
2. 워커 시스템 안정화
3. 중복 폴더 체크 로직 추가
4. 테스트 파일 정리 및 구조화

### 중기 (1-2개월)
1. 성능 최적화
   - 대용량 PDF 처리 개선
   - 메모리 사용량 최적화
   - 캐싱 전략 개선
2. UI/UX 개선
   - 다국어 지원
   - 테마 커스터마이징
   - 단축키 추가

### 장기 (3-6개월)
1. 판짜기(Imposition) 기능 완전 구현
2. 플러그인 시스템 도입
3. 웹 버전 개발
4. AI 기반 품질 예측

---

## 🔍 디버깅 팁

### 로그 파일 위치
- `logs/pdf_checker_YYYYMMDD.log`
- `data/logs/` 폴더

### 디버그 모드 활성화
```python
# src/utils/logger.py
logger.setLevel(logging.DEBUG)
```

### 워커 상태 확인
```python
from src.processing.queue_manager import QueueManager
qm = QueueManager.get_instance()
print(qm.get_status())
```

---

## 📚 참고 자료

### 내부 문서
- [CLAUDE.md](../CLAUDE.md) - AI 작업 지침
- [PROMPTS.md](../PROMPTS.md) - 품질 관리 체크리스트

### 외부 리소스
- [pikepdf 문서](https://pikepdf.readthedocs.io/)
- [PyMuPDF 문서](https://pymupdf.readthedocs.io/)
- [Ghostscript 문서](https://www.ghostscript.com/doc/)

---

## 🏷️ 버전 히스토리

### v2.0 (2025-08-07)
- 전체 시스템 재설계 및 구현
- GUI 추가
- 자동 수정 기능 구현
- 폴더 감시 시스템 구현

### v1.0 (2025-01)
- 초기 버전
- 기본 분석 기능
- CLI 인터페이스