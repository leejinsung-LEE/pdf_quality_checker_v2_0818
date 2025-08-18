#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성능 테스트 실행 스크립트

메모리 누수 테스트와 UI 응답 시간 테스트를 실행합니다.
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime


def print_header(title):
    """헤더 출력"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def run_memory_test(quick=False):
    """메모리 누수 테스트 실행"""
    print_header("메모리 누수 테스트")
    
    cmd = [sys.executable, "tests/performance/test_memory_leak.py"]
    
    if quick:
        cmd.append("--quick")
        print("빠른 테스트 모드 (5분)")
    else:
        print("전체 테스트 (1시간)")
        response = input("\n1시간 동안 실행됩니다. 계속하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("테스트를 건너뜁니다.")
            return False
            
    print("\n테스트 실행 중...")
    print("Ctrl+C로 중단할 수 있습니다.\n")
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"테스트 실패: {e}")
        return False
    except KeyboardInterrupt:
        print("\n테스트가 중단되었습니다.")
        return False


def run_ui_response_test():
    """UI 응답 시간 테스트 실행"""
    print_header("UI 응답 시간 테스트")
    
    print("이 테스트는 약 5-10분 소요됩니다.")
    print("\n테스트 항목:")
    print("  - 드래그&드롭 응답 시간")
    print("  - 프로파일 전환 시간")
    print("  - 대시보드 로딩 시간")
    print("  - 설정 변경 적용 시간")
    print("  - 파일 목록 업데이트 시간")
    
    response = input("\n계속하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        print("테스트를 건너뜁니다.")
        return False
        
    print("\n테스트 실행 중...")
    
    cmd = [sys.executable, "tests/performance/test_ui_response.py"]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"테스트 실패: {e}")
        return False
    except KeyboardInterrupt:
        print("\n테스트가 중단되었습니다.")
        return False


def show_reports():
    """생성된 보고서 표시"""
    print_header("테스트 보고서")
    
    reports_dir = Path("docs/reports")
    if not reports_dir.exists():
        print("보고서 디렉토리가 없습니다.")
        return
        
    # 최근 보고서 찾기
    reports = list(reports_dir.glob("*.md"))
    reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not reports:
        print("생성된 보고서가 없습니다.")
        return
        
    print("\n최근 보고서:")
    for i, report in enumerate(reports[:5], 1):
        mtime = datetime.fromtimestamp(report.stat().st_mtime)
        print(f"  {i}. {report.name}")
        print(f"     생성 시간: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
    print(f"\n보고서 위치: {reports_dir.absolute()}")


def main():
    """메인 함수"""
    print("""
╔══════════════════════════════════════════════════════════╗
║     PDF Quality Checker v2.0 - 성능 테스트 스위트       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("테스트 옵션:")
    print("  1. 빠른 메모리 테스트 (5분)")
    print("  2. 전체 메모리 테스트 (1시간)")
    print("  3. UI 응답 시간 테스트 (5-10분)")
    print("  4. 모든 테스트 실행 (빠른 모드)")
    print("  5. 모든 테스트 실행 (전체)")
    print("  6. 보고서 확인")
    print("  0. 종료")
    
    while True:
        print()
        choice = input("선택 (0-6): ").strip()
        
        if choice == '0':
            print("종료합니다.")
            break
            
        elif choice == '1':
            run_memory_test(quick=True)
            
        elif choice == '2':
            run_memory_test(quick=False)
            
        elif choice == '3':
            run_ui_response_test()
            
        elif choice == '4':
            print("\n모든 테스트 실행 (빠른 모드)")
            run_memory_test(quick=True)
            run_ui_response_test()
            show_reports()
            
        elif choice == '5':
            print("\n모든 테스트 실행 (전체)")
            if run_memory_test(quick=False):
                run_ui_response_test()
            show_reports()
            
        elif choice == '6':
            show_reports()
            
        else:
            print("잘못된 선택입니다.")
            
        print("\n다른 테스트를 실행하시겠습니까?")
        if input("계속 (y/n): ").lower() != 'y':
            break
            
    print("\n테스트가 완료되었습니다.")
    print("보고서는 docs/reports/ 디렉토리에서 확인할 수 있습니다.")


if __name__ == "__main__":
    # 프로젝트 루트에서 실행되는지 확인
    if not Path("main.py").exists():
        print("오류: 프로젝트 루트에서 실행해주세요.")
        print("cd C:\\Users\\wp\\Desktop\\pdf_quality_checker_v2")
        sys.exit(1)
        
    main()