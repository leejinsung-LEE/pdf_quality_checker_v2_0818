# src/data/models.py
"""
데이터 모델 정의

처리 이력 및 관련 데이터 모델을 정의합니다.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pathlib import Path


class ProcessingStatus(Enum):
    """처리 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class HistoryEntry:
    """처리 이력 항목"""
    id: int
    file_path: str
    file_name: str
    file_size: int
    processed_at: datetime
    status: ProcessingStatus
    profile_used: str
    
    # 처리 결과
    quality_score: Optional[float] = None
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    
    # 처리 시간
    processing_time: float = 0.0
    
    # 보고서 경로
    report_path: Optional[str] = None
    
    # 추가 데이터
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """딕셔너리에서 HistoryEntry 생성"""
        # datetime 문자열을 datetime 객체로 변환
        if isinstance(data.get('processed_at'), str):
            data['processed_at'] = datetime.fromisoformat(data['processed_at'])
        
        # ProcessingStatus 문자열을 Enum으로 변환
        if isinstance(data.get('status'), str):
            data['status'] = ProcessingStatus(data['status'])
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """HistoryEntry를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'processed_at': self.processed_at.isoformat(),
            'status': self.status.value,
            'profile_used': self.profile_used,
            'quality_score': self.quality_score,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'info_count': self.info_count,
            'processing_time': self.processing_time,
            'report_path': self.report_path,
            'metadata': self.metadata
        }
    
    @property
    def status_text(self) -> str:
        """상태 텍스트"""
        status_map = {
            ProcessingStatus.PENDING: "대기중",
            ProcessingStatus.PROCESSING: "처리중",
            ProcessingStatus.COMPLETED: "완료",
            ProcessingStatus.FAILED: "실패",
            ProcessingStatus.CANCELLED: "취소됨"
        }
        return status_map.get(self.status, "알 수 없음")
    
    @property
    def issue_count(self) -> int:
        """전체 이슈 개수"""
        return self.error_count + self.warning_count + self.info_count
    
    @property
    def has_errors(self) -> bool:
        """오류 존재 여부"""
        return self.error_count > 0
    
    @property
    def has_issues(self) -> bool:
        """이슈 존재 여부"""
        return self.issue_count > 0
    
    @property
    def file_size_formatted(self) -> str:
        """포맷된 파일 크기"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    @property
    def processing_time_formatted(self) -> str:
        """포맷된 처리 시간"""
        if self.processing_time < 1:
            return f"{self.processing_time*1000:.0f}ms"
        elif self.processing_time < 60:
            return f"{self.processing_time:.1f}초"
        else:
            minutes = int(self.processing_time // 60)
            seconds = int(self.processing_time % 60)
            return f"{minutes}분 {seconds}초"