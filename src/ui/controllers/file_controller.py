# src/ui/controllers/file_controller.py
"""
파일 처리 컨트롤러 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 file_controller/ 모듈에 있습니다.

모듈화 이후에도 기존 임포트가 동작하도록 합니다:
- from .file_controller import FileController
- from src.ui.controllers.file_controller import FileStatus, FileItem
"""

# 모듈화된 구현에서 가져오기
from .file_controller import FileController, FileStatus, FileItem

# 전역 컨트롤러 인스턴스
_file_controller = None


def get_file_controller() -> FileController:
    """전역 파일 컨트롤러 인스턴스 반환"""
    global _file_controller
    if _file_controller is None:
        _file_controller = FileController()
    return _file_controller


# 호환성을 위한 export
__all__ = ['FileController', 'FileStatus', 'FileItem', 'get_file_controller']