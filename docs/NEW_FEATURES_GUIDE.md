# PDF Quality Checker v2.0 - 새 기능 사용 가이드

## 목차
1. [SQLite 기반 작업 이력 관리](#1-sqlite-기반-작업-이력-관리)
2. [통계 대시보드](#2-통계-대시보드)
3. [배치 스케줄러](#3-배치-스케줄러)
4. [백업 및 롤백 시스템](#4-백업-및-롤백-시스템)
5. [프로파일 가져오기/내보내기](#5-프로파일-가져오기내보내기)
6. [프로파일 상세 설정 UI](#6-프로파일-상세-설정-ui)

---

## 1. SQLite 기반 작업 이력 관리

### 개요
기존 JSON 기반 이력 관리를 SQLite 데이터베이스로 업그레이드하여 더 빠르고 강력한 검색과 통계 기능을 제공합니다.

### 주요 기능
- **고급 검색**: 파일명, 날짜, 프로파일, 품질 점수 등으로 필터링
- **통계 분석**: 일/주/월별 처리 통계
- **데이터 내보내기**: CSV, JSON 형식 지원

### 사용 방법

#### Python API
```python
from src.data.history_manager import HistoryManager, ProcessHistory

# 이력 매니저 초기화
history_manager = HistoryManager()

# 처리 이력 추가
history = ProcessHistory(
    file_name="document.pdf",
    file_path="/path/to/document.pdf",
    profile="strict",
    quality_score=92.5,
    error_count=0,
    warning_count=2,
    processing_time=3.2
)
history_id = history_manager.add_history(history)

# 이력 검색
results = history_manager.search_history(
    file_name="document",
    start_date=datetime(2024, 1, 1),
    min_score=80.0,
    limit=50
)

# 통계 조회
stats = history_manager.get_statistics("week")
print(f"주간 평균 품질 점수: {stats['average_score']:.1f}")
```

---

## 2. 통계 대시보드

### 개요
처리 결과를 시각적으로 분석할 수 있는 대시보드 뷰입니다.

### 주요 기능
- **요약 카드**: 전체/성공/실패 건수, 평균 품질 점수
- **타임라인 차트**: 시간대별 처리 추이
- **프로파일별 통계**: 각 프로파일의 사용 빈도와 성능
- **최근 처리 목록**: 최근 처리된 파일들의 상세 정보

### 사용 방법

#### GUI에서 접근
1. 메인 창에서 `F3` 키를 누르거나
2. 메뉴바 > 보기 > 통계 분석 선택
3. 상단의 기간 선택 버튼으로 일/주/월 전환

#### 주요 지표
- **품질 점수**: 0-100 범위, 높을수록 좋음
- **처리 시간**: 파일당 평균 처리 시간
- **오류율**: 전체 중 오류 발생 비율

---

## 3. 배치 스케줄러

### 개요
특정 시간에 자동으로 PDF 품질 검사를 실행하는 스케줄링 시스템입니다.

### 주요 기능
- **다양한 주기**: 한 번, 매일, 매주, 매월
- **폴더 감시**: 지정 폴더의 모든 PDF 자동 처리
- **프로파일 지정**: 작업별로 다른 프로파일 사용
- **자동 수정**: 문제 발견 시 자동 수정 옵션

### 사용 방법

#### 스케줄 작업 추가
```python
from src.processing import get_batch_scheduler, ScheduleTask, ScheduleFrequency

scheduler = get_batch_scheduler()

# 매일 오전 9시에 실행할 작업 추가
task = ScheduleTask(
    id="daily_check",
    name="일일 품질 검사",
    frequency=ScheduleFrequency.DAILY,
    time="09:00",
    folder_path="/path/to/pdfs",
    profile="strict",
    auto_fix=True,
    recursive=True,
    file_pattern="*.pdf"
)

scheduler.add_task(task)
scheduler.start()  # 스케줄러 시작
```

#### GUI에서 설정
1. 메뉴바 > 도구 > 배치 스케줄러
2. "새 작업 추가" 버튼 클릭
3. 실행 시간, 폴더, 프로파일 설정
4. 저장 후 스케줄러 시작

---

## 4. 백업 및 롤백 시스템

### 개요
자동 수정 전 원본 파일을 백업하고, 필요시 복구할 수 있는 시스템입니다.

### 주요 기능
- **자동 백업**: 수정 전 자동으로 원본 저장
- **압축 저장**: ZIP 형식으로 공간 절약
- **버전 관리**: 파일당 최대 5개 백업 유지
- **무결성 검증**: MD5 해시로 파일 무결성 확인

### 사용 방법

#### 수동 백업/롤백
```python
from src.data import get_backup_manager

backup_manager = get_backup_manager()

# 백업 생성
backup_id = backup_manager.create_backup(
    file_path=Path("document.pdf"),
    profile_used="strict",
    changes_to_make=["RGB to CMYK 변환", "폰트 임베딩"]
)

# 백업 이력 조회
backups = backup_manager.get_backup_history(Path("document.pdf"))
for backup in backups:
    print(f"{backup.backup_id}: {backup.created_at}")

# 롤백 실행
success = backup_manager.rollback(
    file_path=Path("document.pdf"),
    backup_id=backup_id,  # 특정 백업으로 복구
    keep_current=True  # 현재 버전도 백업
)
```

#### 자동 백업
자동 수정이 활성화되면 자동으로 백업이 생성됩니다:
- 수정 전 원본 백업
- 수정 실패 시 자동 롤백 옵션
- 백업 보관 기간: 30일 (설정 가능)

---

## 5. 프로파일 가져오기/내보내기

### 개요
품질 검사 프로파일을 파일로 저장하고 공유할 수 있습니다.

### 주요 기능
- **JSON 형식**: 사람이 읽을 수 있는 형식
- **메타데이터 포함**: 생성일, 버전, 설명
- **호환성 검사**: 가져올 때 자동 유효성 검증

### 사용 방법

#### GUI에서 사용
1. 메뉴바 > 편집 > 프로파일 관리
2. 프로파일 선택
3. "내보내기" 버튼 클릭하여 JSON 파일로 저장
4. "가져오기" 버튼으로 외부 프로파일 추가

#### Python API
```python
from src.core.profiles import get_profile_manager

profile_manager = get_profile_manager()

# 프로파일 내보내기
success = profile_manager.export_profile(
    "my_custom_profile",
    Path("my_profile.json")
)

# 프로파일 가져오기
success = profile_manager.import_profile(
    Path("shared_profile.json"),
    new_name="imported_profile"  # 선택적: 새 이름 지정
)
```

---

## 6. 프로파일 상세 설정 UI

### 개요
프로파일의 모든 설정을 시각적으로 관리할 수 있는 전용 UI입니다.

### 주요 기능
- **탭 구조**: 기본/품질/색상/폰트/이미지/고급 설정
- **실시간 미리보기**: 변경사항 즉시 확인
- **프로파일 상속**: 부모 프로파일 기반 커스터마이징
- **검증 기능**: 설정값 자동 검증

### 사용 방법

#### GUI 접근
1. 메인 창에서 `F4` 키를 누르거나
2. 메뉴바 > 보기 > 프로파일 설정 선택

#### 주요 설정 항목

**품질 기준 탭**
- 최소 이미지 DPI: 72-600 (기본: 300)
- 표준 재단선: 0-10mm (기본: 3mm)
- 최소 텍스트 크기: 4-12pt (기본: 6pt)
- 최대 잉크 커버리지: 200-400% (기본: 320%)

**색상 설정 탭**
- RGB 색상 허용 여부
- 별색(Spot Color) 검사
- 권장 색상 프로파일 선택

**폰트 설정 탭**
- 폰트 임베딩 필수 여부
- Type3 폰트 허용
- 서브셋 폰트 허용

**이미지 설정 탭**
- JPEG 압축 품질: 50-100
- 이미지 리샘플링 허용

**고급 설정 탭**
- 권장 PDF 버전
- 메타데이터 검사
- 자동 수정 옵션

---

## 성능 최적화 팁

### 대용량 처리
- 배치 크기를 10-20개로 제한
- 동시 처리 수를 CPU 코어 수에 맞춤
- 백업 압축 활성화로 디스크 공간 절약

### 메모리 관리
- 정기적으로 오래된 이력 정리
- 백업 보관 기간 조정 (기본 30일)
- 대용량 파일은 개별 처리 권장

### 스케줄링 최적화
- 업무 시간 외 스케줄 설정
- 폴더별로 다른 시간대 배정
- 중요도에 따른 우선순위 설정

---

## 문제 해결

### 백업 복구 실패
1. 백업 파일 존재 확인: `data/backups/` 폴더 확인
2. 백업 무결성 검증: `backup_manager.verify_backup(backup_id)`
3. 수동 복구: ZIP 파일 직접 추출

### 스케줄러 미실행
1. 스케줄러 상태 확인: `scheduler.is_running`
2. 작업 활성화 확인: `task.enabled`
3. 시스템 시간 동기화 확인

### 이력 데이터베이스 오류
1. 데이터베이스 파일 권한 확인
2. 디스크 공간 확인
3. 데이터베이스 재구축: `history_manager.rebuild_database()`

---

## 추가 리소스

- [API 문서](./API_DOCUMENTATION.md)
- [설정 마이그레이션 가이드](./MIGRATION_GUIDE.md)
- [기술 지원](https://github.com/yourusername/pdf-quality-checker/issues)

---

*최종 업데이트: 2025년 1월 11일*