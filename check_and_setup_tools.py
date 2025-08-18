#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Quality Checker v2.0 - 외부 도구 설정 및 확인 스크립트

외부 도구(gs, poppler)의 경로를 자동으로 찾고 설정합니다.
"""

import sys
import os
from pathlib import Path
import subprocess

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.external.tool_manager import get_tool_manager


def check_tool_with_path(tool_name: str, tool_path: str) -> bool:
    """도구 경로 확인 및 버전 테스트"""
    try:
        if tool_name == 'gs' or 'ghostscript' in tool_name.lower():
            result = subprocess.run(
                [tool_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            result = subprocess.run(
                [tool_path, '-v'],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        if result.returncode == 0 or result.stderr:  # poppler 도구는 stderr에 버전 출력
            version = result.stdout.strip() or result.stderr.strip()
            return True, version[:50]
    except Exception as e:
        return False, str(e)
    return False, "Unknown error"


def main():
    """메인 함수"""
    print("=" * 80)
    print("PDF Quality Checker v2.0 - 외부 도구 설정 확인")
    print("=" * 80)
    
    # Tool Manager 초기화
    print("\n[도구 관리자 초기화]")
    tool_manager = get_tool_manager()
    
    # 현재 상태 확인
    print("\n[현재 설정된 도구 경로]")
    print("-" * 40)
    
    tools_to_check = ['ghostscript', 'pdffonts', 'pdfinfo', 'pdftoppm', 'pdfimages']
    found_count = 0
    missing_tools = []
    
    for tool_name in tools_to_check:
        tool_path = tool_manager.get_tool_path(tool_name)
        if tool_path:
            print(f"[OK] {tool_name:12} : {tool_path}")
            
            # 버전 확인
            success, version = check_tool_with_path(tool_name, tool_path)
            if success:
                print(f"               버전: {version}")
                found_count += 1
            else:
                print(f"               [경고] 실행 불가: {version}")
        else:
            print(f"[X] {tool_name:12} : 찾을 수 없음")
            missing_tools.append(tool_name)
    
    # 프로젝트 내 도구 폴더 확인
    print("\n[프로젝트 내 도구 폴더 확인]")
    print("-" * 40)
    
    base_dir = Path.cwd()
    gs_dir = base_dir / 'gs'
    poppler_dir = base_dir / 'poppler'
    
    if gs_dir.exists():
        print(f"[OK] Ghostscript 폴더: {gs_dir}")
        # gs/bin 폴더 내용 확인
        gs_bin = gs_dir / 'bin'
        if gs_bin.exists():
            gs_files = list(gs_bin.glob('*.exe'))
            if gs_files:
                print(f"  실행 파일: {', '.join(f.name for f in gs_files[:3])}")
    else:
        print(f"[X] Ghostscript 폴더 없음: {gs_dir}")
    
    if poppler_dir.exists():
        print(f"[OK] Poppler 폴더: {poppler_dir}")
        # poppler/bin 또는 poppler/Library/bin 확인
        poppler_bins = [
            poppler_dir / 'bin',
            poppler_dir / 'Library' / 'bin'
        ]
        for bin_dir in poppler_bins:
            if bin_dir.exists():
                poppler_files = list(bin_dir.glob('*.exe'))
                if poppler_files:
                    print(f"  실행 파일 ({bin_dir.name}): {', '.join(f.name for f in poppler_files[:3])}")
    else:
        print(f"[X] Poppler 폴더 없음: {poppler_dir}")
    
    # 테스트
    print("\n[기능 테스트]")
    print("-" * 40)
    
    # 테스트 PDF 생성
    test_pdf = Path("test_sample.pdf")
    if not test_pdf.exists():
        # 간단한 테스트 PDF가 있는지 확인
        test_pdfs = list(Path(".").glob("*.pdf"))
        if test_pdfs:
            test_pdf = test_pdfs[0]
            print(f"테스트 파일: {test_pdf}")
        else:
            print("테스트할 PDF 파일이 없습니다.")
            test_pdf = None
    
    if test_pdf and test_pdf.exists():
        # pdffonts 테스트
        if tool_manager.has_tool('pdffonts'):
            print("\n[pdffonts 테스트]")
            try:
                result = tool_manager.run_tool('pdffonts', [str(test_pdf)], timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')[:5]
                    for line in lines:
                        if line.strip():
                            print(f"  {line[:80]}")
                    print("  [OK] pdffonts 정상 작동")
                else:
                    print(f"  [X] pdffonts 실행 오류: {result.stderr}")
            except Exception as e:
                print(f"  [X] pdffonts 테스트 실패: {e}")
        
        # ghostscript 테스트
        if tool_manager.has_tool('ghostscript'):
            print("\n[Ghostscript 테스트]")
            try:
                # 간단한 정보 추출
                result = tool_manager.run_tool(
                    'ghostscript',
                    ['-dNODISPLAY', '-dQUIET', '-dNOPAUSE', '-dBATCH', str(test_pdf)],
                    timeout=10
                )
                print("  [OK] Ghostscript 정상 작동")
            except Exception as e:
                print(f"  [X] Ghostscript 테스트 실패: {e}")
    
    # 최종 진단
    print("\n" + "=" * 80)
    print("[진단 결과]")
    print("=" * 80)
    
    if found_count == len(tools_to_check):
        print("[OK] 모든 도구가 정상적으로 설정되어 있습니다!")
        print("  PDF Quality Checker의 모든 기능을 사용할 수 있습니다.")
    elif found_count > 0:
        print(f"[PARTIAL] {found_count}/{len(tools_to_check)}개 도구가 설정되어 있습니다.")
        print(f"  누락된 도구: {', '.join(missing_tools)}")
        print("\n[권장 조치]")
        if 'pdffonts' in missing_tools or 'pdfinfo' in missing_tools:
            print("* Poppler 도구가 누락되었습니다.")
            print("  1. poppler 폴더가 있는지 확인")
            print("  2. poppler/Library/bin/*.exe 파일들이 있는지 확인")
            print("  3. 없다면 https://github.com/oschwartz10612/poppler-windows/releases 에서 다운로드")
        if 'ghostscript' in missing_tools:
            print("* Ghostscript가 누락되었습니다.")
            print("  1. gs 폴더가 있는지 확인")
            print("  2. gs/bin/gswin64c.exe 파일이 있는지 확인")
            print("  3. 없다면 https://www.ghostscript.com/download/gsdnld.html 에서 다운로드")
    else:
        print("[X] 외부 도구를 찾을 수 없습니다.")
        print("  PDF Quality Checker의 고급 기능이 제한됩니다.")
        print("\n[설치 가이드]")
        print("1. 프로젝트 폴더에 'gs'와 'poppler' 폴더가 있는지 확인")
        print("2. 각 폴더 내에 실행 파일들이 있는지 확인")
        print("3. 파일이 없다면 위 링크에서 다운로드하여 설치")
    
    print("\n" + "=" * 80)
    
    # 환경 변수 설정 제안
    if missing_tools and (gs_dir.exists() or poppler_dir.exists()):
        print("\n[환경 변수 설정 제안]")
        print("시스템 PATH에 다음 경로를 추가하면 도움이 될 수 있습니다:")
        if gs_dir.exists():
            print(f"  * {gs_dir / 'bin'}")
        if poppler_dir.exists():
            print(f"  * {poppler_dir / 'Library' / 'bin'}")
            print(f"  * {poppler_dir / 'bin'}")


if __name__ == "__main__":
    main()