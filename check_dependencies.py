#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Quality Checker 외부 도구 의존성 확인 스크립트

필수 및 선택적 외부 도구들의 설치 상태를 확인합니다.
"""

import shutil
import subprocess
import sys
from pathlib import Path

def check_tool(tool_name: str) -> tuple[bool, str]:
    """도구 설치 확인"""
    tool_path = shutil.which(tool_name)
    if tool_path:
        # 버전 정보 가져오기 시도
        try:
            if tool_name == 'gs':
                result = subprocess.run([tool_name, '--version'], 
                                      capture_output=True, text=True)
            elif tool_name == 'pdffonts':
                result = subprocess.run([tool_name, '-v'], 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run([tool_name, '--version'], 
                                      capture_output=True, text=True)
            version = result.stdout.strip() or result.stderr.strip()
            return True, version[:50]  # 버전 정보 일부만
        except:
            return True, "버전 확인 불가"
    return False, "미설치"

def main():
    """메인 함수"""
    print("=" * 60)
    print("PDF Quality Checker v2.0 - 외부 도구 의존성 확인")
    print("=" * 60)
    
    # 필수 도구
    required_tools = {
        'python': 'Python 인터프리터',
        'pip': 'Python 패키지 관리자',
    }
    
    # 권장 도구
    recommended_tools = {
        'pdffonts': 'PDF 폰트 분석 (poppler-utils)',
        'gs': 'Ghostscript - PDF 처리',
        'pdftk': 'PDF Toolkit - PDF 조작 (선택)',
        'pdfinfo': 'PDF 정보 추출 (poppler-utils)',
        'pdfimages': 'PDF 이미지 추출 (poppler-utils)',
    }
    
    print("\n[필수 도구]")
    all_required_installed = True
    for tool, description in required_tools.items():
        installed, version = check_tool(tool)
        status = "[OK]" if installed else "[누락]"
        print(f"  {status} {tool:12} - {description}")
        if installed and version != "버전 확인 불가":
            print(f"       버전: {version}")
        if not installed:
            all_required_installed = False
    
    print("\n[권장 도구]")
    missing_recommended = []
    for tool, description in recommended_tools.items():
        installed, version = check_tool(tool)
        status = "[OK]" if installed else "[누락]"
        print(f"  {status} {tool:12} - {description}")
        if installed and version != "버전 확인 불가":
            print(f"       버전: {version}")
        if not installed:
            missing_recommended.append(tool)
    
    # Python 패키지 확인
    print("\n[Python 패키지]")
    packages = ['pikepdf', 'PyMuPDF', 'customtkinter', 'watchdog', 'Pillow']
    for package in packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [누락] {package}")
    
    # 설치 가이드
    if missing_recommended:
        print("\n" + "=" * 60)
        print("설치 권장 사항")
        print("=" * 60)
        
        if 'pdffonts' in missing_recommended or 'pdfinfo' in missing_recommended:
            print("\n[poppler-utils 설치]")
            print("  Windows:")
            print("    1. scoop install poppler")
            print("    또는")
            print("    2. https://github.com/oschwartz10612/poppler-windows/releases")
            print("       다운로드 후 PATH 추가")
            print("  Mac:")
            print("    brew install poppler")
            print("  Linux:")
            print("    sudo apt-get install poppler-utils")
        
        if 'gs' in missing_recommended:
            print("\n[Ghostscript 설치]")
            print("  Windows:")
            print("    1. scoop install ghostscript")
            print("    또는")
            print("    2. https://www.ghostscript.com/download/gsdnld.html")
            print("  Mac:")
            print("    brew install ghostscript")
            print("  Linux:")
            print("    sudo apt-get install ghostscript")
        
        if 'pdftk' in missing_recommended:
            print("\n[PDFtk 설치 (선택사항)]")
            print("  Windows:")
            print("    https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/")
            print("  Mac:")
            print("    brew install pdftk-java")
            print("  Linux:")
            print("    sudo apt-get install pdftk")
    
    # 최종 판정
    print("\n" + "=" * 60)
    if all_required_installed and not missing_recommended:
        print("[결과] 모든 도구가 설치되어 있습니다!")
        print("PDF Quality Checker를 완전한 기능으로 사용할 수 있습니다.")
    elif all_required_installed:
        print("[결과] 기본 기능은 사용 가능합니다.")
        print(f"권장 도구 {len(missing_recommended)}개가 누락되어 일부 기능이 제한됩니다.")
        print("특히 pdffonts가 없으면 폰트 검사가 제한됩니다.")
    else:
        print("[결과] 필수 도구가 누락되었습니다!")
        print("프로그램이 정상 작동하지 않을 수 있습니다.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()