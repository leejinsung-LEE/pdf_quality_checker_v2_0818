# -*- coding: utf-8 -*-
"""
테스트 실행 헬퍼 스크립트
경로 문제 없이 테스트를 실행할 수 있도록 도와줍니다.
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """pytest를 사용하여 모든 테스트 실행"""
    
    # 프로젝트 루트 경로 확인
    project_root = Path(__file__).parent
    
    print("🧪 PDF Quality Checker v2.0 테스트 실행")
    print(f"프로젝트 루트: {project_root}")
    print("-" * 50)
    
    # pytest 실행
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        cwd=project_root
    )
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())
