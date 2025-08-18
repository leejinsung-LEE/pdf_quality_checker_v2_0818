# PDF Quality Checker v2.0 - 성능 테스트 가이드

*작성일: 2025-01-16*
*목적: 메모리 누수 및 UI 응답 시간 테스트 실행 가이드*

## 🚀 빠른 시작

### 1. 테스트 스위트 실행
```bash
cd C:\Users\wp\Desktop\pdf_quality_checker_v2
python tests/performance/run_performance_tests.py
```

### 2. 개별 테스트 실행

#### 메모리 누수 테스트 (빠른 모드 - 5분)
```bash
python tests/performance/test_memory_leak.py --quick
```

#### 메모리 누수 테스트 (전체 - 1시간)
```bash
python tests/performance/test_memory_leak.py --duration 60
```

#### UI 응답 시간 테스트
```bash
python tests/performance/test_ui_response.py
```

## 📋 테스트 상세 설명

### 1️⃣ 메모리 누수 테스트

#### 목적
- 1시간 동안 앱을 실행하며 메모리 사용량 추적
- 메모리 누수 패턴 감지
- 누수 지점 식별

#### 테스트 시나리오
1. **파일 처리 반복** (100회)
   - PDF 파일 추가/처리
   - 메모리 해제 확인

2. **프로파일 전환** (10회)
   - 프로파일 간 전환
   - UI 업데이트 메모리 추적

3. **대시보드 작업** (20회)
   - 통계 대시보드 열기/닫기
   - 차트 렌더링 메모리 확인

4. **폴더 감시** (10회)
   - 폴더 감시 시작/중지
   - 이벤트 리스너 정리 확인

5. **대용량 파일 처리**
   - 50MB+ PDF 처리
   - 스트리밍 처리 검증

#### 성공 기준
- ✅ 1시간 실행 후 메모리 증가 < 100MB
- ✅ 메모리 증가율 < 2MB/시간
- ✅ 가비지 컬렉션 후 메모리 회수

#### 출력 파일
- `docs/reports/memory_leak_analysis_YYYYMMDD_HHMMSS.md`
- `docs/reports/memory_graph_YYYYMMDD_HHMMSS.png`

### 2️⃣ UI 응답 시간 테스트

#### 목적
- 주요 UI 작업 응답 시간 측정
- 100ms 미만 목표 달성 확인
- 병목 지점 식별

#### 측정 대상

| 작업 | 목표 시간 | 설명 |
|------|-----------|------|
| 단일 파일 드롭 | 50ms | PDF 1개 드래그&드롭 |
| 다중 파일 드롭 | 100ms | PDF 10개 드래그&드롭 |
| 프로파일 전환 | 30ms | 프로파일 선택 변경 |
| 프로파일 UI 업데이트 | 50ms | UI 요소 업데이트 |
| 대시보드 로딩 | 100ms | 통계 대시보드 초기 로딩 |
| 차트 업데이트 | 50ms | 차트 데이터 업데이트 |
| 설정 적용 | 50ms | 설정 변경 적용 |
| 설정 저장 | 100ms | 설정 파일 저장 |
| 파일 목록 업데이트 | 30ms | 파일 목록 새로고침 |
| 상태 업데이트 | 20ms | 상태바 메시지 업데이트 |

#### 출력 파일
- `docs/reports/ui_response_analysis_YYYYMMDD_HHMMSS.md`

## 📊 보고서 해석

### 메모리 누수 보고서

#### 정상 패턴
```
초기 메모리: 150.00 MB
최종 메모리: 180.00 MB
메모리 증가: 30.00 MB (20.0%)
✅ 정상: 심각한 메모리 누수가 감지되지 않았습니다.
```

#### 누수 패턴
```
초기 메모리: 150.00 MB
최종 메모리: 350.00 MB
메모리 증가: 200.00 MB (133.3%)
⚠️ 경고: 심각한 메모리 누수가 감지되었습니다!
```

### UI 응답 시간 보고서

#### 정상 결과
```
drag_drop_single:
  목표: 50ms
  평균: 35.42ms ✅ PASS
```

#### 병목 지점
```
dashboard_load:
  목표: 100ms
  평균: 156.78ms ❌ FAIL
  
개선 방안:
- 차트 렌더링 최적화
- 데이터 집계를 백그라운드에서 수행
```

## 🔧 문제 해결

### 테스트 실행 오류

#### 1. ImportError
```bash
# 해결: requirements.txt 설치
pip install -r requirements.txt
pip install matplotlib psutil
```

#### 2. 테스트 파일 없음
```bash
# 해결: 테스트 파일 자동 생성됨
# 또는 수동 생성
mkdir -p tests/fixtures
echo "%PDF-1.4" > tests/fixtures/test.pdf
```

#### 3. 권한 오류
```bash
# 해결: 관리자 권한으로 실행
# Windows: 관리자 권한 CMD/PowerShell
# Linux/Mac: sudo python ...
```

## 💡 테스트 팁

### 1. 정확한 측정을 위한 준비
- 다른 프로그램 종료
- 백신 실시간 검사 일시 중지
- 충분한 메모리 확보 (최소 4GB 여유)

### 2. 빠른 테스트 먼저
```bash
# 5분 빠른 테스트로 기본 확인
python tests/performance/test_memory_leak.py --quick

# 문제 없으면 전체 테스트
python tests/performance/test_memory_leak.py
```

### 3. 반복 테스트
- 첫 실행은 캐시 워밍업
- 2-3회 반복하여 평균값 확인

## 📈 개선 작업 흐름

1. **테스트 실행**
   ```bash
   python tests/performance/run_performance_tests.py
   # 옵션 4 선택 (모든 테스트 - 빠른 모드)
   ```

2. **보고서 확인**
   ```bash
   # 보고서 위치
   cd docs/reports
   # 최신 보고서 열기
   ```

3. **병목 지점 파악**
   - 메모리 누수: 급증 구간 확인
   - UI 응답: FAIL 항목 확인

4. **코드 개선**
   - 보고서의 개선 방안 참고
   - 해당 모듈 수정

5. **재테스트**
   - 개선 후 동일 테스트 실행
   - 개선 효과 확인

## 🎯 목표 달성 체크리스트

### 메모리 관리
- [ ] 1시간 실행 메모리 증가 < 100MB
- [ ] 메모리 증가율 < 2MB/시간
- [ ] 대용량 파일 처리 후 메모리 회수
- [ ] 가비지 컬렉션 정상 작동

### UI 응답성
- [ ] 모든 UI 작업 < 100ms
- [ ] 드래그&드롭 < 50ms
- [ ] 프로파일 전환 < 30ms
- [ ] 대시보드 로딩 < 100ms
- [ ] 설정 저장 < 100ms

## 📝 추가 테스트 명령어

### 커스텀 테스트 시간
```bash
# 30분 메모리 테스트
python tests/performance/test_memory_leak.py --duration 30

# UI 테스트 반복 횟수 조정
python tests/performance/test_ui_response.py --iterations 20
```

### 결과만 확인
```bash
# 최근 보고서 보기
dir docs\reports\*.md /o-d | head -1
type docs\reports\[최신파일명]
```

### 자동화 스크립트
```batch
@echo off
REM run_perf_test.bat
cd C:\Users\wp\Desktop\pdf_quality_checker_v2
python tests/performance/test_memory_leak.py --quick
python tests/performance/test_ui_response.py
echo 테스트 완료! 보고서를 확인하세요.
pause
```

---

**작성 완료**: 2025-01-16
**다음 검토**: 테스트 실행 후 결과 기반 업데이트