#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 처리 플로우 테스트 스크립트

GUI에서 파일을 추가하고 처리하는 전체 플로우를 테스트합니다.
"""

import sys
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# UTF-8 인코딩 설정
from _utf8_setup import setup_utf8_encoding

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.controllers import FileController
from src.ui.views import ProcessingView
from src.processing.queue_manager import TaskPriority
from src.utils.logger import setup_logger

def test_gui_processing():
    """GUI 처리 플로우 테스트"""
    print("=== GUI Processing Flow Test ===\n")
    
    # 로거 설정
    logger = setup_logger(Path("logs/test_gui.log"))
    
    # 1. 컨트롤러 초기화
    print("1. FileController 초기화 중...")
    controller = FileController(logger=logger)
    print("   [OK] FileController 초기화 완료")
    
    # 2. 테스트 GUI 생성
    print("\n2. 테스트 GUI 생성 중...")
    root = tk.Tk()
    root.title("PDF Quality Checker - 처리 테스트")
    root.geometry("1200x700")
    
    # ProcessingView 생성
    processing_view = ProcessingView(root, controller)
    processing_view.pack(fill='both', expand=True)
    
    print("   [OK] GUI 생성 완료")
    
    # 3. 테스트 PDF 파일 찾기
    print("\n3. 테스트 PDF 파일 찾기...")
    test_files = list(Path(".").glob("*.pdf"))
    if not test_files:
        # 테스트 PDF 생성
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        test_file = Path("test_gui_sample.pdf")
        c = canvas.Canvas(str(test_file), pagesize=A4)
        c.drawString(100, 750, "GUI Processing Test PDF")
        c.drawString(100, 700, "This is a test file for GUI processing flow")
        c.save()
        test_files = [test_file]
        print(f"   [OK] 테스트 파일 생성: {test_file}")
    else:
        print(f"   [OK] 테스트 파일 발견: {test_files[0]}")
    
    # 4. 파일 추가 및 처리
    def add_and_process_files():
        """파일 추가 및 처리"""
        print("\n4. 파일 추가 및 처리 시작...")
        
        # 파일 추가
        file_ids = controller.add_files(
            test_files[:3],  # 최대 3개만
            profile="default",
            priority=TaskPriority.NORMAL,
            auto_fix=False
        )
        
        print(f"   [OK] {len(file_ids)}개 파일 추가됨")
        for file_id in file_ids:
            print(f"       - {file_id}")
        
        # 상태 모니터링
        def check_status():
            """상태 확인"""
            all_completed = True
            for file_id in file_ids:
                if file_id in controller.file_items:
                    item = controller.file_items[file_id]
                    status = item.status.value
                    print(f"   [{file_id[:20]}...] {status}")
                    
                    if status in ['waiting', 'processing']:
                        all_completed = False
            
            if not all_completed:
                # 1초 후 다시 확인
                root.after(1000, check_status)
            else:
                print("\n5. 처리 완료!")
                print_results()
        
        # 결과 출력
        def print_results():
            """결과 출력"""
            print("\n=== 처리 결과 ===")
            for file_id in file_ids:
                if file_id in controller.file_items:
                    item = controller.file_items[file_id]
                    print(f"\n파일: {item.filename}")
                    print(f"  상태: {item.status.value}")
                    print(f"  오류: {item.error_count}")
                    print(f"  경고: {item.warning_count}")
                    print(f"  품질 점수: {item.quality_score:.1f}")
                    print(f"  처리 시간: {item.processing_time:.2f}초")
            
            # 5초 후 종료
            print("\n5초 후 종료됩니다...")
            root.after(5000, root.quit)
        
        # 상태 확인 시작
        root.after(1000, check_status)
    
    # 시작 버튼
    start_button = ttk.Button(
        root,
        text="테스트 시작",
        command=add_and_process_files
    )
    start_button.pack(pady=10)
    
    # GUI 실행
    print("\n=== GUI를 시작합니다. '테스트 시작' 버튼을 클릭하세요 ===")
    root.mainloop()
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    try:
        test_gui_processing()
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
    except Exception as e:
        print(f"\n\n오류 발생: {e}")
        import traceback
        traceback.print_exc()