#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern UI 직접 테스트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

# UTF-8 설정
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 필수 디렉토리 생성
for directory in [Path("data"), Path("logs"), Path("reports"), Path("output")]:
    directory.mkdir(exist_ok=True)

# 로깅 설정
import logging
logging.basicConfig(level=logging.INFO)

print("Modern UI 테스트 시작...")

try:
    # Modern UI 직접 실행
    from src.ui.modern import ModernApp
    print("Modern UI 모듈 로드 성공")
    
    app = ModernApp()
    print("Modern UI 앱 생성 성공")
    
    print("Modern UI 실행 중...")
    app.run()
    
except Exception as e:
    print(f"에러 발생: {e}")
    import traceback
    traceback.print_exc()
    
print("테스트 종료")