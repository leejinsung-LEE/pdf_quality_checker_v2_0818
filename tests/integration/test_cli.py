#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Quality Checker v2.0 - CLI 테스트

PDF 품질 검사 기능을 콘솔에서 테스트합니다.
"""

import sys
import os
import io
from pathlib import Path

# UTF-8 인코딩 강제 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import PDFQualityChecker


def main():
    """메인 함수"""
    print("""
=========================================
     PDF Quality Checker v2.0
     CLI Test Version
=========================================
""")
    
    # 샘플 PDF 파일 경로
    sample_pdf = Path("gs/examples/text_graph_image_cmyk_rgb.pdf")
    
    if not sample_pdf.exists():
        print(f"[ERROR] Sample PDF file not found: {sample_pdf}")
        return
    
    print(f"[File] Test file: {sample_pdf}")
    print("-" * 40)
    
    try:
        # PDF 품질 검사기 생성
        checker = PDFQualityChecker()
        
        # 품질 검사 수행
        print("\n[INFO] Starting quality check...")
        result = checker.check(sample_pdf)
        
        # 결과 출력
        print("\n" + "=" * 40)
        print("INSPECTION RESULTS")
        print("=" * 40)
        
        summary = result.get_summary()
        
        print(f"* File: {summary['file']}")
        print(f"* Profile: {summary['profile']}")
        print(f"* Quality Score: {summary['quality_score']:.1f}/100")
        print(f"* Time Taken: {summary['duration']['total']:.2f} seconds")
        
        print("\n[ISSUE SUMMARY]")
        print(f"  - Errors: {summary['issues']['errors']}")
        print(f"  - Warnings: {summary['issues']['warnings']}")
        print(f"  - Info: {summary['issues']['info']}")
        print(f"  - Total: {summary['issues']['total']}")
        
        # 이슈 상세 내용
        if result.issues:
            print("\n[ISSUE DETAILS]")
            for i, issue in enumerate(result.issues[:10], 1):  # 처음 10개만
                severity_icon = {
                    'error': '[ERROR]',
                    'warning': '[WARN]',
                    'info': '[INFO]'
                }.get(issue.severity.value, '[*]')
                
                print(f"\n  {i}. {severity_icon} [{issue.category.value}] {issue.title}")
                print(f"     {issue.description}")
                if issue.affected_items:
                    print(f"     Affected items: {', '.join(issue.affected_items[:3])}")
        
        print("\n[SUCCESS] Inspection completed!")
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()