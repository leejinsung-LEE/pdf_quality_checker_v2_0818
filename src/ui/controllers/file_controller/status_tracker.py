# src/ui/controllers/file_controller/status_tracker.py
"""
상태 추적 및 통계 관리

파일 상태 조회, 통계 생성, 완료된 파일 정리 등을 담당합니다.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import FileControllerBase, FileStatus, FileItem


class StatusTracker:
    """상태 추적 관리 클래스"""
    
    def __init__(self, parent: 'FileControllerBase'):
        self.parent = parent
    
    def get_file_item(self, file_id: str) -> Optional['FileItem']:
        """파일 아이템 조회"""
        return self.parent.file_items.get(file_id)
    
    def get_all_files(self) -> List['FileItem']:
        """모든 파일 아이템 조회"""
        return list(self.parent.file_items.values())
    
    def get_files_by_status(self, status: 'FileStatus') -> List['FileItem']:
        """상태별 파일 아이템 조회"""
        return [item for item in self.parent.file_items.values() if item.status == status]
    
    def get_statistics(self) -> Dict[str, Any]:
        """처리 통계 조회"""
        from .base import FileStatus
        
        stats = {
            'total': len(self.parent.file_items),
            'waiting': 0,
            'processing': 0,
            'completed': 0,
            'error': 0,
            'cancelled': 0,
            'completed_today': self.parent._count_completed_today(),
            'total_errors': 0,
            'total_warnings': 0,
            'avg_processing_time': 0.0,
            'success_rate': 0.0
        }
        
        processing_times = []
        
        for file_item in self.parent.file_items.values():
            # 상태별 카운트
            if file_item.status == FileStatus.WAITING:
                stats['waiting'] += 1
            elif file_item.status == FileStatus.PROCESSING:
                stats['processing'] += 1
            elif file_item.status == FileStatus.COMPLETED:
                stats['completed'] += 1
                if file_item.processing_time > 0:
                    processing_times.append(file_item.processing_time)
            elif file_item.status == FileStatus.ERROR:
                stats['error'] += 1
            elif file_item.status == FileStatus.CANCELLED:
                stats['cancelled'] += 1
            
            # 문제 카운트
            stats['total_errors'] += file_item.error_count
            stats['total_warnings'] += file_item.warning_count
        
        # 평균 처리 시간
        if processing_times:
            stats['avg_processing_time'] = sum(processing_times) / len(processing_times)
        
        # 성공률 계산
        total_processed = stats['completed'] + stats['error']
        if total_processed > 0:
            stats['success_rate'] = (stats['completed'] / total_processed) * 100
        
        return stats
    
    def clear_completed(self):
        """완료된 파일 목록에서 제거"""
        from .base import FileStatus
        
        completed_ids = []
        for file_id, file_item in self.parent.file_items.items():
            if file_item.status in [FileStatus.COMPLETED, FileStatus.ERROR, FileStatus.CANCELLED]:
                completed_ids.append(file_id)
        
        # 완료된 파일들 제거
        for file_id in completed_ids:
            del self.parent.file_items[file_id]
        
        self.parent.logger.info(f"완료된 파일 {len(completed_ids)}개 정리")
    
    def clear_by_status(self, status: 'FileStatus'):
        """특정 상태의 파일들을 목록에서 제거"""
        status_ids = []
        for file_id, file_item in self.parent.file_items.items():
            if file_item.status == status:
                status_ids.append(file_id)
        
        # 해당 상태 파일들 제거
        for file_id in status_ids:
            del self.parent.file_items[file_id]
        
        self.parent.logger.info(f"{status.value} 상태 파일 {len(status_ids)}개 정리")
    
    def get_files_with_issues(self) -> List['FileItem']:
        """문제가 있는 파일들 조회"""
        return [item for item in self.parent.file_items.values() if item.has_issues]
    
    def get_folder_files(self, folder_name: str) -> List['FileItem']:
        """특정 폴더의 파일들 조회"""
        return [item for item in self.parent.file_items.values() 
                if item.folder_name == folder_name]
    
    def get_profile_files(self, profile: str) -> List['FileItem']:
        """특정 프로파일로 처리된 파일들 조회"""
        return [item for item in self.parent.file_items.values() 
                if item.profile == profile]
    
    def get_files_summary(self) -> Dict[str, Any]:
        """파일 처리 요약 정보"""
        from .base import FileStatus
        
        files = list(self.parent.file_items.values())
        
        if not files:
            return {
                'total_files': 0,
                'total_size_mb': 0.0,
                'avg_size_mb': 0.0,
                'largest_file': None,
                'smallest_file': None,
                'most_common_profile': None,
                'folder_distribution': {}
            }
        
        # 기본 통계
        total_size = sum(file_item.size_mb for file_item in files)
        sizes = [file_item.size_mb for file_item in files if file_item.size_mb > 0]
        
        # 프로파일 분포
        profile_count = {}
        for file_item in files:
            profile_count[file_item.profile] = profile_count.get(file_item.profile, 0) + 1
        
        most_common_profile = max(profile_count.items(), key=lambda x: x[1])[0] if profile_count else None
        
        # 폴더 분포
        folder_count = {}
        for file_item in files:
            if file_item.folder_name:
                folder_count[file_item.folder_name] = folder_count.get(file_item.folder_name, 0) + 1
        
        # 최대/최소 파일
        largest_file = max(files, key=lambda x: x.size_mb) if files else None
        smallest_file = min(files, key=lambda x: x.size_mb if x.size_mb > 0 else float('inf')) if files else None
        
        return {
            'total_files': len(files),
            'total_size_mb': total_size,
            'avg_size_mb': total_size / len(files) if files else 0.0,
            'largest_file': {
                'filename': largest_file.filename,
                'size_mb': largest_file.size_mb
            } if largest_file else None,
            'smallest_file': {
                'filename': smallest_file.filename,
                'size_mb': smallest_file.size_mb
            } if smallest_file and smallest_file.size_mb > 0 else None,
            'most_common_profile': most_common_profile,
            'folder_distribution': folder_count,
            'profile_distribution': profile_count
        }