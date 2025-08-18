# PDF Quality Checker v2.0 - 즉시 실행 가능한 명령어 모음
*작성일: 2025-01-15*
*목적: 새 세션에서 복사-붙여넣기로 바로 사용할 수 있는 명령어*

## 🚀 세션 시작 시 첫 번째로 실행할 명령어들

### 1단계: 프로젝트 상태 확인
```bash
# 현재 위치 확인
pwd

# 프로젝트 폴더로 이동
cd C:\Users\wp\Desktop\pdf_quality_checker_v2

# Git 상태 확인
git status

# 변경된 파일 목록
git diff --name-only

# 최근 커밋 확인
git log --oneline -5
```

### 2단계: 앱 실행 테스트
```bash
# 빠른 테스트 (권장)
python main.py --fast

# 싱글톤 패턴 테스트
python -c "from src.processing import get_queue_manager; from src.data.data_manager import get_data_manager; from src.processing.processor import get_processor; print('모든 싱글톤 OK')"

# 워커 수 확인
python -c "import multiprocessing; print(f'CPU: {multiprocessing.cpu_count()}'); from src.processing import get_queue_manager; print(f'Workers: {get_queue_manager().num_workers}')"
```

## 🔍 Bare except 제거 작업 (우선순위 중간)

### 작업 대상 파일 확인 및 수정

#### 1. backup_manager/storage.py
```bash
# 파일 열기 및 175번 라인 확인
python -c "
with open('src/data/backup_manager/storage.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(max(0, 174-5), min(len(lines), 175+5)):
        print(f'{i+1:4}: {lines[i]}', end='')
"
```

#### 2. backup_manager/cleanup.py
```bash
# 파일 열기 및 181번 라인 확인
python -c "
with open('src/data/backup_manager/cleanup.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(max(0, 180-5), min(len(lines), 181+5)):
        print(f'{i+1:4}: {lines[i]}', end='')
"
```

#### 3. backup_manager/compression.py
```bash
# 파일 열기 및 139번 라인 확인
python -c "
with open('src/data/backup_manager/compression.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(max(0, 138-5), min(len(lines), 139+5)):
        print(f'{i+1:4}: {lines[i]}', end='')
"
```

#### 4. batch_scheduler/manager.py
```bash
# 파일 열기 및 239번 라인 확인
python -c "
with open('src/processing/batch_scheduler/manager.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(max(0, 238-5), min(len(lines), 239+5)):
        print(f'{i+1:4}: {lines[i]}', end='')
"
```

#### 5. history_manager/search_engine.py
```bash
# 파일 열기 및 125번 라인 확인
python -c "
with open('src/data/history_manager/search_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(max(0, 124-5), min(len(lines), 125+5)):
        print(f'{i+1:4}: {lines[i]}', end='')
"
```

### 모든 bare except 한번에 찾기
```bash
# PowerShell
Get-ChildItem -Path "src" -Filter "*.py" -Recurse | Select-String -Pattern "^\s*except\s*:\s*$" | Format-Table Path, LineNumber, Line -AutoSize

# Python 스크립트로 찾기
python -c "
import os
import re

bare_except_pattern = re.compile(r'^\s*except\s*:\s*$')

for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if bare_except_pattern.match(line):
                        print(f'{filepath}:{i}')
"
```

## 🔄 동적 import 제거 작업

### 동적 import 패턴 찾기
```python
# 함수 내부의 import 문 찾기
python -c "
import os
import re

# 들여쓰기된 import 패턴 (함수/메서드 내부)
indented_import = re.compile(r'^[ \t]+(from|import)\s+')

results = {}
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if indented_import.match(line):
                        if filepath not in results:
                            results[filepath] = []
                        results[filepath].append((i, line.strip()))

# 결과 출력
for filepath, imports in sorted(results.items()):
    print(f'\n{filepath}:')
    for line_num, line in imports[:3]:  # 각 파일당 처음 3개만
        print(f'  {line_num}: {line}')
"
```

### TYPE_CHECKING 패턴 적용 예시
```python
# 순환 참조 방지를 위한 패턴
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..profiles import ProfileManager  # 타입 체크 시에만 import

class SomeClass:
    def __init__(self, profile_manager: 'ProfileManager'):
        self.profile_manager = profile_manager
```

## 🧪 테스트 작성 및 실행

### 싱글톤 패턴 테스트 파일 생성
```bash
# 테스트 디렉토리 생성
mkdir -p tests/unit

# 테스트 파일 생성
cat > tests/unit/test_singleton_patterns.py << 'EOF'
import unittest
import threading
from concurrent.futures import ThreadPoolExecutor

class TestSingletonPatterns(unittest.TestCase):
    
    def test_queue_manager_singleton(self):
        """큐 매니저 싱글톤 테스트"""
        from src.processing import get_queue_manager
        
        qm1 = get_queue_manager()
        qm2 = get_queue_manager()
        self.assertIs(qm1, qm2)
    
    def test_data_manager_singleton(self):
        """데이터 매니저 싱글톤 테스트"""
        from src.data.data_manager import get_data_manager
        
        dm1 = get_data_manager()
        dm2 = get_data_manager()
        self.assertIs(dm1, dm2)
    
    def test_thread_safety(self):
        """멀티스레드 환경에서 싱글톤 테스트"""
        from src.processing import get_queue_manager
        
        instances = []
        
        def get_instance():
            return get_queue_manager()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_instance) for _ in range(10)]
            instances = [f.result() for f in futures]
        
        # 모든 인스턴스가 동일해야 함
        first = instances[0]
        self.assertTrue(all(inst is first for inst in instances))

if __name__ == '__main__':
    unittest.main()
EOF
```

### 테스트 실행
```bash
# 단위 테스트 실행
python -m unittest tests.unit.test_singleton_patterns -v

# pytest 사용 (설치되어 있는 경우)
pytest tests/unit/test_singleton_patterns.py -v

# 특정 테스트만 실행
python -m unittest tests.unit.test_singleton_patterns.TestSingletonPatterns.test_queue_manager_singleton
```

## 📊 프로젝트 분석 명령어

### 코드 통계
```bash
# Python 파일 수
python -c "import os; print(f'Python files: {sum(1 for r, d, f in os.walk(\"src\") for file in f if file.endswith(\".py\"))}')"

# 전체 코드 라인 수
python -c "
import os
total = 0
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                total += len(f.readlines())
print(f'Total lines: {total:,}')
"

# 가장 큰 파일 10개
python -c "
import os
files = []
for root, dirs, filenames in os.walk('src'):
    for name in filenames:
        if name.endswith('.py'):
            path = os.path.join(root, name)
            size = os.path.getsize(path)
            with open(path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            files.append((path, lines, size))

for path, lines, size in sorted(files, key=lambda x: x[1], reverse=True)[:10]:
    print(f'{lines:5} lines: {path}')
"
```

### 모듈 의존성 확인
```python
# import 구조 분석
python -c "
import os
import re

import_pattern = re.compile(r'^(from|import)\s+([.\w]+)')

imports = {}
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            module = filepath.replace(os.sep, '.')[4:-3]  # src 제거, .py 제거
            
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    match = import_pattern.match(line.strip())
                    if match:
                        imported = match.group(2)
                        if module not in imports:
                            imports[module] = set()
                        imports[module].add(imported)

# 가장 많이 import하는 모듈
for module, deps in sorted(imports.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    print(f'{module}: {len(deps)} dependencies')
"
```

## 🔧 자주 사용하는 수정 패턴

### Bare except 수정 템플릿
```python
# 수정 전
try:
    some_operation()
except:
    pass

# 수정 후 - 옵션 1: 구체적 예외
try:
    some_operation()
except (FileNotFoundError, PermissionError) as e:
    self.logger.error(f"파일 작업 실패: {e}")

# 수정 후 - 옵션 2: 일반 Exception
try:
    some_operation()
except Exception as e:
    self.logger.error(f"예상치 못한 오류: {e}")
    # 선택적: 스택 트레이스 로깅
    import traceback
    self.logger.debug(traceback.format_exc())
```

### 동적 import 수정 템플릿
```python
# 수정 전
def process_file(self, file_path):
    from ...core.profiles import ProfileManager
    manager = ProfileManager()
    # ...

# 수정 후 - 옵션 1: 파일 상단
from ...core.profiles import ProfileManager

def process_file(self, file_path):
    manager = ProfileManager()
    # ...

# 수정 후 - 옵션 2: TYPE_CHECKING (순환 참조 시)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.profiles import ProfileManager

class Processor:
    def __init__(self):
        self.manager: Optional['ProfileManager'] = None
    
    def process_file(self, file_path):
        if self.manager is None:
            from ...core.profiles import ProfileManager
            self.manager = ProfileManager()
        # ...
```

## 🎯 작업 완료 확인

### 수정 후 테스트
```bash
# 기본 실행 테스트
python main.py --fast

# import 테스트
python -c "
try:
    from src.processing import get_queue_manager
    from src.data.data_manager import get_data_manager
    from src.processing.processor import get_processor
    from src.processing.batch_scheduler import get_batch_scheduler
    from src.utils.alarm_manager import get_alarm_manager
    print('✅ 모든 모듈 import 성공')
except ImportError as e:
    print(f'❌ Import 실패: {e}')
"

# 싱글톤 동작 테스트
python -c "
from src.processing import get_queue_manager
qm1 = get_queue_manager()
qm2 = get_queue_manager()
print(f'싱글톤 테스트: {'✅ 성공' if qm1 is qm2 else '❌ 실패'}')"
```

### Git 커밋 준비
```bash
# 변경사항 확인
git diff

# 스테이징
git add -p  # 대화식으로 추가

# 커밋 메시지 예시
git commit -m "refactor: bare except 제거 및 구체적 예외 처리 추가

- backup_manager 모듈의 bare except를 구체적 예외로 변경
- batch_scheduler와 history_manager 예외 처리 개선
- 에러 로깅 추가로 디버깅 용이성 향상"
```

## 📌 문제 발생 시 롤백

### 변경사항 되돌리기
```bash
# 특정 파일 되돌리기
git checkout -- src/data/backup_manager/storage.py

# 모든 변경사항 되돌리기 (주의!)
git checkout -- .

# 스테이징된 것 취소
git reset HEAD
```

### 백업 생성
```bash
# 작업 전 백업
copy src\data\backup_manager\storage.py src\data\backup_manager\storage.py.backup

# Python으로 백업
python -c "
import shutil
files = [
    'src/data/backup_manager/storage.py',
    'src/data/backup_manager/cleanup.py',
    'src/data/backup_manager/compression.py',
    'src/processing/batch_scheduler/manager.py',
    'src/data/history_manager/search_engine.py'
]
for f in files:
    shutil.copy2(f, f + '.backup')
    print(f'Backed up: {f}')
"
```

---

이 명령어들을 복사해서 바로 사용하세요! 🚀