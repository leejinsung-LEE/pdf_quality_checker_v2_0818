# PDF Quality Checker v2.0 - API 문서

## 목차
1. [핵심 모듈](#핵심-모듈)
2. [데이터 관리](#데이터-관리)
3. [처리 시스템](#처리-시스템)
4. [UI 컴포넌트](#ui-컴포넌트)
5. [유틸리티](#유틸리티)

---

## 핵심 모듈

### QualityChecker
PDF 품질 검사의 메인 클래스

```python
from src.core import QualityChecker

class QualityChecker:
    def __init__(self, profile_manager: Optional[ProfileManager] = None)
    
    def check(self, pdf_path: Union[str, Path], 
             profile_name: Optional[str] = None) -> QualityCheckResult
    """기본 품질 검사"""
    
    def check_with_profile(self, pdf_path: Union[str, Path], 
                          profile: Union[str, QualityProfile]) -> QualityCheckResult
    """특정 프로파일로 검사"""
    
    def quick_check(self, pdf_path: Union[str, Path]) -> QualityCheckResult
    """빠른 검사 (필수 항목만)"""
    
    def strict_check(self, pdf_path: Union[str, Path]) -> QualityCheckResult
    """엄격한 검사"""
    
    def batch_check(self, pdf_paths: List[Union[str, Path]], 
                   profile_name: Optional[str] = None) -> List[QualityCheckResult]
    """여러 파일 일괄 검사"""
```

### QualityCheckResult
품질 검사 결과 클래스

```python
class QualityCheckResult:
    @property
    def has_errors(self) -> bool
    """오류 존재 여부"""
    
    @property
    def has_warnings(self) -> bool
    """경고 존재 여부"""
    
    @property
    def error_count(self) -> int
    """오류 개수"""
    
    @property
    def warning_count(self) -> int
    """경고 개수"""
    
    @property
    def quality_score(self) -> float
    """품질 점수 (0-100)"""
    
    def get_summary(self) -> Dict[str, Any]
    """결과 요약 딕셔너리"""
```

---

## 데이터 관리

### HistoryManager (새 기능)
SQLite 기반 작업 이력 관리

```python
from src.data.history_manager import HistoryManager, ProcessHistory

class HistoryManager:
    def __init__(self, db_path: Optional[Path] = None)
    
    def add_history(self, history: ProcessHistory) -> int
    """이력 추가, 이력 ID 반환"""
    
    def update_history(self, history_id: int, **updates) -> bool
    """이력 업데이트"""
    
    def search_history(self, 
                      file_name: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      profile: Optional[str] = None,
                      min_score: Optional[float] = None,
                      max_score: Optional[float] = None,
                      limit: int = 100,
                      offset: int = 0) -> List[ProcessHistory]
    """고급 검색"""
    
    def get_statistics(self, period: str = "day") -> Dict[str, Any]
    """통계 계산 (day/week/month)"""
    
    def get_profile_statistics(self) -> Dict[str, Dict[str, Any]]
    """프로파일별 통계"""
    
    def export_to_csv(self, file_path: Path, 
                     histories: Optional[List[ProcessHistory]] = None) -> bool
    """CSV로 내보내기"""
    
    def export_to_json(self, file_path: Path,
                      histories: Optional[List[ProcessHistory]] = None) -> bool
    """JSON으로 내보내기"""
```

### ProcessHistory
처리 이력 데이터 클래스

```python
@dataclass
class ProcessHistory:
    file_name: str
    file_path: str
    profile: str
    quality_score: float
    error_count: int = 0
    warning_count: int = 0
    processing_time: float = 0.0
    backup_id: Optional[str] = None
    processed_at: Optional[datetime] = None
    id: Optional[int] = None
```

### BackupManager (새 기능)
백업 및 롤백 관리

```python
from src.data import get_backup_manager

class BackupManager:
    def __init__(self, backup_dir: Optional[Path] = None,
                 max_backups_per_file: int = 5,
                 retention_days: int = 30,
                 compress_backups: bool = True)
    
    def create_backup(self, file_path: Path,
                     profile_used: str = "default",
                     changes_to_make: List[str] = None,
                     metadata: Dict[str, Any] = None) -> Optional[str]
    """백업 생성, 백업 ID 반환"""
    
    def rollback(self, file_path: Path,
                backup_id: Optional[str] = None,
                keep_current: bool = True) -> bool
    """롤백 실행"""
    
    def get_backup_history(self, file_path: Path) -> List[BackupInfo]
    """파일의 백업 이력 조회"""
    
    def verify_backup(self, backup_id: str) -> Tuple[bool, str]
    """백업 무결성 검증"""
    
    def cleanup_old_backups(self) -> int
    """오래된 백업 정리, 삭제된 개수 반환"""
    
    def get_backup_statistics(self) -> Dict[str, Any]
    """백업 통계"""
```

---

## 처리 시스템

### BatchScheduler (새 기능)
배치 작업 스케줄러

```python
from src.processing import get_batch_scheduler, ScheduleTask, ScheduleFrequency

class BatchScheduler:
    def __init__(self, batch_processor: Optional[Any] = None,
                 config_file: Optional[Path] = None)
    
    def add_task(self, task: ScheduleTask) -> bool
    """스케줄 작업 추가"""
    
    def update_task(self, task_id: str, **kwargs) -> bool
    """작업 업데이트"""
    
    def remove_task(self, task_id: str) -> bool
    """작업 제거"""
    
    def start(self)
    """스케줄러 시작"""
    
    def stop(self)
    """스케줄러 중지"""
    
    def get_next_runs(self, limit: int = 10) -> List[Dict[str, Any]]
    """다음 실행 예정 작업 목록"""
    
    def get_task_history(self, task_id: str) -> Dict[str, Any]
    """작업 실행 이력"""
```

### ScheduleTask
스케줄 작업 데이터 클래스

```python
@dataclass
class ScheduleTask:
    id: str
    name: str
    frequency: ScheduleFrequency
    time: str  # HH:MM 형식
    folder_path: str
    profile: str = "default"
    auto_fix: bool = False
    recursive: bool = True
    file_pattern: str = "*.pdf"
    enabled: bool = True
    weekday: Optional[int] = None  # 0=월요일, 6=일요일
    day_of_month: Optional[int] = None  # 1-31
```

### PDFProcessor
단일 PDF 파일 처리기

```python
from src.processing import PDFProcessor

class PDFProcessor:
    def process_file(self, file_path: Path,
                    file_id: Optional[str] = None,
                    folder_config: Optional[Dict[str, Any]] = None) -> ProcessingResult
    """단일 파일 처리"""
    
    def process_with_profile(self, file_path: Path,
                           profile_name: str,
                           auto_fix: bool = False) -> ProcessingResult
    """특정 프로파일로 처리"""
    
    def set_callbacks(self,
                     on_start: Optional[Callable] = None,
                     on_progress: Optional[Callable] = None,
                     on_complete: Optional[Callable] = None,
                     on_error: Optional[Callable] = None)
    """콜백 함수 설정"""
```

---

## UI 컴포넌트

### StatisticsDashboardView (새 기능)
통계 대시보드 뷰

```python
from src.ui.views import StatisticsDashboardView

class StatisticsDashboardView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs)
    
    def refresh_data(self)
    """데이터 새로고침"""
    
    def set_period(self, period: str)
    """기간 설정 (day/week/month)"""
    
    def export_chart(self, file_path: Path) -> bool
    """차트 이미지 내보내기"""
```

### ProfileSettingsView (새 기능)
프로파일 상세 설정 뷰

```python
from src.ui.views import ProfileSettingsView

class ProfileSettingsView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs)
    
    def load_profile_list(self)
    """프로파일 목록 로드"""
    
    def load_profile_settings(self, profile_name: str)
    """프로파일 설정 로드"""
    
    def save_settings(self)
    """설정 저장"""
    
    def import_profile(self)
    """프로파일 가져오기"""
    
    def export_profile(self)
    """프로파일 내보내기"""
```

---

## 유틸리티

### AlarmManager (새 기능)
알람 시스템 관리

```python
from src.utils.alarm_manager import get_alarm_manager

class AlarmManager:
    def add_condition(self, condition: AlarmCondition)
    """알람 조건 추가"""
    
    def check_and_notify(self, condition_type: AlarmConditionType,
                        value: Any = None,
                        title: str = "",
                        message: str = "") -> bool
    """조건 확인 및 알림"""
    
    def set_enabled(self, enabled: bool)
    """알람 활성화/비활성화"""
```

### 프로파일 관리
프로파일 가져오기/내보내기

```python
from src.core.profiles import get_profile_manager

profile_manager = get_profile_manager()

# 프로파일 내보내기
success = profile_manager.export_profile(
    profile_name="custom_profile",
    file_path=Path("profile.json")
)

# 프로파일 가져오기
success = profile_manager.import_profile(
    file_path=Path("shared_profile.json"),
    new_name="imported_profile"  # 선택적
)

# 프로파일 생성
success = profile_manager.create_profile(
    name="new_profile",
    base_profile="default",  # 기반 프로파일
    settings={
        "quality_standards": {
            "minimum_dpi": 300,
            "standard_bleed_size": 3.0
        }
    }
)
```

---

## 예제 코드

### 전체 워크플로우 예제

```python
from pathlib import Path
from src.core import QualityChecker
from src.data import get_backup_manager
from src.data.history_manager import HistoryManager, ProcessHistory
from src.processing import get_batch_scheduler, ScheduleTask, ScheduleFrequency

# 1. 품질 검사
checker = QualityChecker()
result = checker.check("document.pdf", profile_name="strict")

# 2. 백업 생성 (자동 수정 전)
if result.has_errors:
    backup_manager = get_backup_manager()
    backup_id = backup_manager.create_backup(
        Path("document.pdf"),
        profile_used="strict",
        changes_to_make=["오류 수정 예정"]
    )

# 3. 이력 기록
history_manager = HistoryManager()
history = ProcessHistory(
    file_name="document.pdf",
    file_path=str(Path("document.pdf").absolute()),
    profile="strict",
    quality_score=result.quality_score,
    error_count=result.error_count,
    warning_count=result.warning_count,
    backup_id=backup_id
)
history_id = history_manager.add_history(history)

# 4. 스케줄 작업 설정
scheduler = get_batch_scheduler()
task = ScheduleTask(
    id="daily_check",
    name="일일 품질 검사",
    frequency=ScheduleFrequency.DAILY,
    time="09:00",
    folder_path="/path/to/pdfs",
    profile="strict",
    auto_fix=True
)
scheduler.add_task(task)
scheduler.start()

# 5. 통계 확인
stats = history_manager.get_statistics("week")
print(f"주간 평균 품질: {stats['average_score']:.1f}")
print(f"처리 파일 수: {stats['total_files']}")
```

### 비동기 처리 예제

```python
import threading
from src.processing import PDFProcessor

processor = PDFProcessor()

# 콜백 함수 정의
def on_progress(file_id, status, progress, message):
    print(f"[{progress}%] {message}")

def on_complete(file_info, result):
    print(f"완료: {file_info.filename}")
    print(f"품질 점수: {result.quality_score}")

# 콜백 설정
processor.set_callbacks(
    on_progress=on_progress,
    on_complete=on_complete
)

# 비동기 처리
def process_async(file_path):
    processor.process_with_profile(
        file_path,
        profile_name="default",
        auto_fix=True
    )

thread = threading.Thread(
    target=process_async,
    args=(Path("document.pdf"),)
)
thread.start()
```

---

## 오류 처리

### 공통 예외

```python
class ProfileNotFoundError(Exception):
    """프로파일을 찾을 수 없음"""

class BackupError(Exception):
    """백업 생성/복구 실패"""

class SchedulerError(Exception):
    """스케줄러 오류"""

class DatabaseError(Exception):
    """데이터베이스 오류"""
```

### 오류 처리 예제

```python
from src.data import get_backup_manager

try:
    backup_manager = get_backup_manager()
    backup_id = backup_manager.create_backup(Path("document.pdf"))
    
    # 처리...
    
    if error_occurred:
        # 롤백
        success = backup_manager.rollback(
            Path("document.pdf"),
            backup_id
        )
        if not success:
            raise BackupError("롤백 실패")
            
except BackupError as e:
    logging.error(f"백업 오류: {e}")
    # 수동 복구 시도
    
except Exception as e:
    logging.error(f"예상치 못한 오류: {e}")
```

---

## 성능 고려사항

### 대용량 파일 처리
- 스트리밍 방식 사용
- 메모리 매핑 활용
- 청크 단위 처리

### 동시성
- 스레드 풀 사용 (기본 3개)
- 작업 큐 관리
- 리소스 잠금 최소화

### 캐싱
- 프로파일 캐싱
- 분석 결과 캐싱
- 데이터베이스 쿼리 캐싱

---

*최종 업데이트: 2025년 1월 11일*