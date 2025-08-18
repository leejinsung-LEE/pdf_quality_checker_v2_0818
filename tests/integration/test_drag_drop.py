"""
드래그앤드롭 기능 테스트
"""

import tkinter as tk
from pathlib import Path
import sys

# UTF-8 인코딩 설정
from _utf8_setup import setup_utf8_encoding

def test_tkinterdnd2():
    """tkinterdnd2 설치 확인"""
    try:
        import tkinterdnd2
        print("[OK] tkinterdnd2가 설치되어 있습니다.")
        return True
    except ImportError:
        print("[ERROR] tkinterdnd2가 설치되어 있지 않습니다.")
        print("설치 명령: pip install tkinterdnd2")
        return False

def test_drag_drop_simple():
    """간단한 드래그앤드롭 테스트"""
    try:
        import tkinterdnd2
        
        # 메인 윈도우 생성
        root = tkinterdnd2.Tk()
        root.title("드래그앤드롭 테스트")
        root.geometry("400x300")
        
        # 드롭 영역 생성
        drop_label = tk.Label(
            root,
            text="PDF 파일을 여기에 드래그하세요",
            bg="lightgray",
            relief="solid",
            width=40,
            height=10
        )
        drop_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # 드롭된 파일 목록
        file_list = tk.Listbox(root)
        file_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def on_drop(event):
            """드롭 이벤트 처리"""
            files = root.tk.splitlist(event.data)
            for file_path in files:
                if file_path.lower().endswith('.pdf'):
                    file_list.insert(tk.END, f"✓ {Path(file_path).name}")
                    print(f"[DROP] PDF 파일 감지: {file_path}")
                else:
                    file_list.insert(tk.END, f"✗ {Path(file_path).name} (PDF 아님)")
                    print(f"[DROP] PDF가 아닌 파일: {file_path}")
        
        def on_drag_enter(event):
            """드래그 진입 이벤트"""
            drop_label.config(bg="lightgreen")
            return event.action
        
        def on_drag_leave(event):
            """드래그 떠남 이벤트"""
            drop_label.config(bg="lightgray")
            return event.action
        
        # 드래그앤드롭 설정
        drop_label.drop_target_register(tkinterdnd2.DND_FILES)
        drop_label.dnd_bind('<<Drop>>', on_drop)
        drop_label.dnd_bind('<<DragEnter>>', on_drag_enter)
        drop_label.dnd_bind('<<DragLeave>>', on_drag_leave)
        
        print("[INFO] 드래그앤드롭 테스트 창이 열렸습니다.")
        print("[INFO] PDF 파일을 창으로 드래그해보세요.")
        
        root.mainloop()
        
    except Exception as e:
        print(f"[ERROR] 드래그앤드롭 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

def test_app_drag_drop():
    """실제 앱에서 드래그앤드롭 확인"""
    try:
        from src.ui.windows.main_window import MainWindow
        from src.ui.controllers import FileController
        
        # 파일 컨트롤러 생성
        controller = FileController()
        
        # 드롭 이벤트 콜백 추가
        def on_file_added(file_item):
            print(f"[APP] 파일 추가됨: {file_item.filename}")
        
        controller.on_file_added = on_file_added
        
        # 메인 윈도우 생성
        window = MainWindow()
        
        # 드래그앤드롭 테스트
        print("[INFO] 메인 앱 창이 열렸습니다.")
        print("[INFO] 사이드바의 드롭 영역에 PDF를 드래그해보세요.")
        
        window.mainloop()
        
    except Exception as e:
        print(f"[ERROR] 앱 드래그앤드롭 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

def check_sidebar_drop():
    """사이드바 드롭 영역 디버깅"""
    try:
        import tkinterdnd2
        from src.ui.components.sidebar import Sidebar
        
        root = tkinterdnd2.Tk()
        root.title("사이드바 드롭 테스트")
        root.geometry("300x600")
        
        # 사이드바 생성
        sidebar = Sidebar(root)
        sidebar.pack(fill="both", expand=True)
        
        # 드롭 콜백 설정
        def on_files_dropped(files):
            print(f"[SIDEBAR] 파일 드롭됨: {files}")
            for file in files:
                print(f"  - {file}")
        
        sidebar.on_files_dropped = on_files_dropped
        
        print("[INFO] 사이드바 드롭 테스트 창이 열렸습니다.")
        print("[INFO] 드롭 영역을 찾아서 PDF를 드래그해보세요.")
        
        # 드롭 프레임 존재 확인
        if hasattr(sidebar, 'drop_frame'):
            print("[OK] 드롭 프레임이 존재합니다.")
        else:
            print("[WARNING] 드롭 프레임이 없습니다.")
        
        root.mainloop()
        
    except Exception as e:
        print(f"[ERROR] 사이드바 드롭 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("드래그앤드롭 기능 테스트")
    print("=" * 60)
    print()
    
    # 1. tkinterdnd2 설치 확인
    if not test_tkinterdnd2():
        print("\n먼저 tkinterdnd2를 설치해주세요:")
        print("pip install tkinterdnd2")
        sys.exit(1)
    
    print("\n테스트 옵션:")
    print("1. 간단한 드래그앤드롭 테스트")
    print("2. 사이드바 드롭 영역 테스트")
    print("3. 전체 앱 테스트")
    
    choice = input("\n선택 (1/2/3): ").strip()
    
    if choice == "1":
        test_drag_drop_simple()
    elif choice == "2":
        check_sidebar_drop()
    elif choice == "3":
        test_app_drag_drop()
    else:
        print("잘못된 선택입니다.")