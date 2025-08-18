#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTF-8 인코딩 설정 모듈

모든 테스트 파일에서 import하여 사용
"""

import sys
import os
import io
import locale

def setup_utf8_encoding():
    """UTF-8 인코딩 강제 설정"""
    if sys.platform == 'win32':
        # 콘솔 코드 페이지를 UTF-8로 설정
        os.system('chcp 65001 > nul 2>&1')
        # 환경 변수 설정
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        # stdout/stderr를 UTF-8로 재설정
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    else:
        # Unix 계열에서도 UTF-8 확인
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass

# 모듈 import 시 자동 실행
setup_utf8_encoding()