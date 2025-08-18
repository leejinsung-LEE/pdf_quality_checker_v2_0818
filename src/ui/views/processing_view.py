"""
처리 화면 뷰 - 호환성 래퍼

이 파일은 기존 코드와의 호환성을 위한 래퍼입니다.
실제 구현은 processing/ 디렉토리에 모듈화되어 있습니다.

마이그레이션:
기존: from src.ui.views.processing_view import ProcessingView
새로운: from src.ui.views.processing import ProcessingView

최종 수정: 2025-01-12
"""

from .processing import ProcessingView

# 원본 파일의 추가 export가 있다면 여기에 추가
# 예: 원본에서 직접 export하던 함수나 클래스들

# 기존 파일의 메서드들을 ProcessingView 클래스에 동적으로 추가
# (호환성을 위해 필요한 경우)

# add_file, update_file_status 등 메서드는 이미 모듈화된 코드에서 처리됨
# file_list_manager를 통해 접근 가능

# 호환성을 위한 메서드 추가
def _add_compat_methods():
    """기존 코드와의 호환성을 위한 메서드 추가"""
    
    # add_file 메서드 래핑
    def add_file(self, file_item):
        """파일 추가 (호환성)"""
        self.file_list_manager.add_file(file_item)
    
    # update_file_status 메서드 래핑
    def update_file_status(self, file_id, status):
        """파일 상태 업데이트 (호환성)"""
        self.file_list_manager.update_file_status(file_id, status)
    
    # update_file_progress 메서드 래핑
    def update_file_progress(self, file_id, progress, message):
        """파일 진행률 업데이트 (호환성)"""
        self.file_list_manager.update_file_progress(file_id, progress, message)
    
    # update_file_complete 메서드 래핑
    def update_file_complete(self, file_id, file_item):
        """파일 처리 완료 업데이트 (호환성)"""
        self.file_list_manager.update_file_complete(file_id, file_item)
    
    # clear_completed 메서드 래핑
    def clear_completed(self):
        """완료 항목 정리 (호환성)"""
        self.file_list_manager.clear_completed()
    
    # 메서드들을 ProcessingView 클래스에 추가
    ProcessingView.add_file = add_file
    ProcessingView.update_file_status = update_file_status
    ProcessingView.update_file_progress = update_file_progress
    ProcessingView.update_file_complete = update_file_complete
    ProcessingView.clear_completed = clear_completed

# 호환성 메서드 추가 실행
_add_compat_methods()

__all__ = ['ProcessingView']