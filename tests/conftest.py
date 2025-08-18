# tests/conftest.py
"""
pytest 설정 파일

테스트 실행을 위한 공통 설정과 픽스처를 정의합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))