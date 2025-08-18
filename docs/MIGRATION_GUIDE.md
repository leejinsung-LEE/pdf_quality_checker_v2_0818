# PDF Quality Checker v2.0 - 마이그레이션 가이드

## 개요
이 문서는 PDF Quality Checker v1.x에서 v2.0으로 업그레이드하는 방법을 안내합니다.

## 목차
1. [주요 변경사항](#주요-변경사항)
2. [데이터 마이그레이션](#데이터-마이그레이션)
3. [설정 마이그레이션](#설정-마이그레이션)
4. [코드 마이그레이션](#코드-마이그레이션)
5. [롤백 방법](#롤백-방법)

---

## 주요 변경사항

### 새로운 기능
- ✅ SQLite 기반 이력 관리 (기존 JSON 방식 대체)
- ✅ 통계 대시보드 뷰
- ✅ 배치 스케줄러
- ✅ 백업/롤백 시스템
- ✅ 프로파일 가져오기/내보내기
- ✅ 프로파일 상세 설정 UI

### 변경된 구조
- `data/history.json` → SQLite 데이터베이스 (`data/history.db`)
- 싱글톤 패턴 적용 (모든 매니저 클래스)
- UI 구조 개선 (탭 뷰 추가)

### 제거된 기능
- Modern UI (Kivy 기반) - `docs/old_docs/modern_ui_backup/`으로 이동

---

## 데이터 마이그레이션

### 1단계: 기존 데이터 백업

```bash
# Windows
copy data\*.json data\backup\

# Linux/Mac
cp data/*.json data/backup/
```

### 2단계: 이력 데이터 마이그레이션

```python
# migrate_history.py
import json
from pathlib import Path
from datetime import datetime
from src.data.history_manager import HistoryManager, ProcessHistory
from src.data import get_data_manager

def migrate_history():
    """JSON 이력을 SQLite로 마이그레이션"""
    
    # 1. 기존 JSON 데이터 로드
    data_manager = get_data_manager()
    old_histories = data_manager.get_history(limit=None)
    
    # 2. 새 SQLite 매니저 초기화
    history_manager = HistoryManager()
    
    # 3. 데이터 변환 및 저장
    migrated_count = 0
    for entry in old_histories:
        try:
            # ProcessHistory 객체 생성
            history = ProcessHistory(
                file_name=entry.file_name,
                file_path=entry.file_path,
                profile=entry.profile_used,
                quality_score=entry.quality_score or 0.0,
                error_count=entry.error_count or 0,
                warning_count=entry.warning_count or 0,
                processing_time=entry.processing_time or 0.0,
                processed_at=entry.processed_at
            )
            
            # SQLite에 저장
            history_manager.add_history(history)
            migrated_count += 1
            
        except Exception as e:
            print(f"마이그레이션 실패: {entry.file_name} - {e}")
    
    print(f"완료: {migrated_count}개 이력 마이그레이션됨")
    return migrated_count

if __name__ == "__main__":
    migrate_history()
```

### 3단계: 프로파일 마이그레이션

```python
# migrate_profiles.py
from src.core.profiles import get_profile_manager

def migrate_profiles():
    """v1 프로파일을 v2 형식으로 변환"""
    
    profile_manager = get_profile_manager()
    
    # v1 프로파일 데이터 (예시)
    v1_profiles = {
        "custom_profile": {
            "min_dpi": 300,
            "max_ink": 320,
            "check_fonts": True
        }
    }
    
    # v2 형식으로 변환
    for name, v1_data in v1_profiles.items():
        v2_settings = {
            "quality_standards": {
                "minimum_dpi": v1_data.get("min_dpi", 300),
                "max_ink_coverage": v1_data.get("max_ink", 320)
            },
            "check_options": {
                "check_fonts": v1_data.get("check_fonts", True)
            }
        }
        
        # 프로파일 생성
        success = profile_manager.create_profile(
            name=name,
            base_profile="default",
            settings=v2_settings
        )
        
        if success:
            print(f"프로파일 마이그레이션: {name}")

if __name__ == "__main__":
    migrate_profiles()
```

---

## 설정 마이그레이션

### 환경 설정 파일

**v1 설정 (`config.json`)**
```json
{
    "default_profile": "strict",
    "auto_fix": true,
    "output_folder": "./output",
    "watch_folders": [
        "/path/to/watch1",
        "/path/to/watch2"
    ]
}
```

**v2 설정 (`data/settings.json`)**
```json
{
    "current_profile": "strict",
    "auto_fix_enabled": true,
    "output_folder": "./output",
    "folder_configs": [
        {
            "path": "/path/to/watch1",
            "recursive": true,
            "profile": "strict",
            "auto_process": true
        }
    ],
    "backup_settings": {
        "enabled": true,
        "max_backups": 5,
        "retention_days": 30
    },
    "scheduler_settings": {
        "enabled": false,
        "tasks": []
    }
}
```

### 자동 마이그레이션 스크립트

```python
# auto_migrate.py
import json
from pathlib import Path
import shutil
from datetime import datetime

def auto_migrate():
    """설정 자동 마이그레이션"""
    
    # 백업 생성
    backup_dir = Path("data/backup") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 기존 설정 파일 백업
    for file in Path("data").glob("*.json"):
        shutil.copy2(file, backup_dir / file.name)
    
    print(f"백업 완료: {backup_dir}")
    
    # v1 설정 로드
    v1_config_path = Path("config.json")
    if v1_config_path.exists():
        with open(v1_config_path, 'r', encoding='utf-8') as f:
            v1_config = json.load(f)
        
        # v2 형식으로 변환
        v2_config = {
            "current_profile": v1_config.get("default_profile", "default"),
            "auto_fix_enabled": v1_config.get("auto_fix", False),
            "output_folder": v1_config.get("output_folder", "./output"),
            "folder_configs": [],
            "backup_settings": {
                "enabled": True,
                "max_backups": 5,
                "retention_days": 30,
                "compress": True
            },
            "scheduler_settings": {
                "enabled": False,
                "tasks": []
            }
        }
        
        # 감시 폴더 변환
        for folder in v1_config.get("watch_folders", []):
            v2_config["folder_configs"].append({
                "path": folder,
                "recursive": True,
                "profile": v1_config.get("default_profile", "default"),
                "auto_process": True
            })
        
        # v2 설정 저장
        v2_config_path = Path("data/settings.json")
        with open(v2_config_path, 'w', encoding='utf-8') as f:
            json.dump(v2_config, f, ensure_ascii=False, indent=2)
        
        print("설정 마이그레이션 완료")
        
        # 옵션: 기존 설정 파일 이름 변경
        v1_config_path.rename("config.json.v1_backup")
    
    return True

if __name__ == "__main__":
    auto_migrate()
```

---

## 코드 마이그레이션

### API 변경사항

#### 이력 관리

**v1 (JSON 기반)**
```python
from src.data import get_data_manager

data_manager = get_data_manager()
entry = data_manager.add_history(
    file_path="document.pdf",
    status="completed",
    profile="default"
)
histories = data_manager.get_history(limit=10)
```

**v2 (SQLite 기반)**
```python
from src.data.history_manager import HistoryManager, ProcessHistory

history_manager = HistoryManager()
history = ProcessHistory(
    file_name="document.pdf",
    file_path="/path/to/document.pdf",
    profile="default",
    quality_score=85.0
)
history_id = history_manager.add_history(history)

# 고급 검색
histories = history_manager.search_history(
    file_name="document",
    min_score=80.0,
    limit=10
)
```

#### 프로파일 관리

**v1**
```python
from src.profiles import ProfileManager

profile_manager = ProfileManager()
profile = profile_manager.get_profile("default")
```

**v2**
```python
from src.core.profiles import get_profile_manager

profile_manager = get_profile_manager()  # 싱글톤
profile = profile_manager.get_profile("default")

# 새 기능: 내보내기/가져오기
profile_manager.export_profile("default", Path("profile.json"))
profile_manager.import_profile(Path("shared_profile.json"))
```

### UI 접근 방법

**v1**
```python
# 단일 뷰
from src.ui.main_window import MainWindow
window = MainWindow()
```

**v2**
```python
# 탭 기반 다중 뷰
from src.ui.windows.main_window import MainWindow
window = MainWindow()

# 새 뷰들
# F1: 처리 현황
# F2: 대시보드
# F3: 통계 분석
# F4: 프로파일 설정
```

---

## 롤백 방법

### 완전 롤백

v2에서 v1로 돌아가야 하는 경우:

1. **백업 복원**
```bash
# Windows
move data\backup\*.json data\
del data\*.db

# Linux/Mac
mv data/backup/*.json data/
rm data/*.db
```

2. **이전 버전 설치**
```bash
git checkout v1.0
pip install -r requirements_v1.txt
```

### 부분 롤백

특정 기능만 이전 버전 사용:

```python
# 이전 JSON 데이터 매니저 사용
from src.data import get_data_manager  # v1 방식
# 대신
# from src.data.history_manager import HistoryManager  # v2 방식
```

---

## 문제 해결

### 일반적인 문제

#### 1. SQLite 데이터베이스 오류
```
Error: database is locked
```

**해결방법:**
```python
# 연결 종료 확인
history_manager = HistoryManager()
# 사용 후
del history_manager  # 명시적 삭제
```

#### 2. 프로파일 호환성 문제
```
Error: Invalid profile format
```

**해결방법:**
```python
# 프로파일 재생성
profile_manager = get_profile_manager()
profile_manager.create_profile(
    "custom",
    base_profile="default",
    settings={...}
)
```

#### 3. 메모리 사용량 증가
```
Memory usage increased after migration
```

**해결방법:**
- 오래된 백업 정리: `backup_manager.cleanup_old_backups()`
- 이력 데이터 정리: `history_manager.cleanup_old_history(days=90)`

### 지원

문제가 지속되는 경우:
1. 로그 파일 확인: `logs/app.log`
2. GitHub Issues: https://github.com/yourusername/pdf-quality-checker/issues
3. 이메일 지원: support@example.com

---

## 체크리스트

마이그레이션 전 확인사항:

- [ ] 기존 데이터 백업 완료
- [ ] 새 버전 요구사항 확인 (Python 3.10+)
- [ ] 의존성 패키지 업데이트 (`pip install -r requirements.txt`)
- [ ] 테스트 환경에서 마이그레이션 테스트
- [ ] 프로파일 설정 검토
- [ ] 폴더 감시 설정 확인
- [ ] 스케줄 작업 설정 (필요시)
- [ ] 백업 정책 설정

---

*최종 업데이트: 2025년 1월 11일*