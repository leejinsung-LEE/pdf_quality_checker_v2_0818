"""
간단한 드래그앤드롭 테스트 - 메인 앱과 동일한 구조
"""

# UTF-8 인코딩 설정
from _utf8_setup import setup_utf8_encoding

import tkinterdnd2
from pathlib import Path

def test_main_window_drag():
    """메인 윈도우와 동일한 구조로 테스트"""
    from src.ui.windows.main_window import MainWindow
    
    # 메인 윈도우 실행
    app = MainWindow()
    
    print("\n" + "="*60)
    print("드래그앤드롭 테스트 안내")
    print("="*60)
    print()
    print("1. 왼쪽 사이드바를 확인하세요")
    print("2. '파일 또는 폴더를 여기에 드래그' 영역을 찾으세요")
    print("3. PDF 파일을 그 영역으로 드래그하세요")
    print("4. 콘솔에 디버그 메시지가 출력되는지 확인하세요")
    print()
    print("디버그 메시지:")
    print("- [INFO] 드래그앤드롭 활성화됨")
    print("- [DEBUG] 드롭 이벤트 발생: ...")
    print("- [DEBUG] PDF 파일 감지: ...")
    print()
    
    app.mainloop()

if __name__ == "__main__":
    test_main_window_drag()