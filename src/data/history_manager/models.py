# -*- coding: utf-8 -*-
"""
이력 관리 데이터 모델
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ProcessStatus(Enum):
    """처리 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessHistory:
    """처리 이력 데이터"""
    id: Optional[int] = None
    file_path: str = ""
    file_name: str = ""
    file_size: int = 0
    process_type: str = ""  # check, fix, batch, watch
    status: str = ProcessStatus.PENDING.value
    quality_score: Optional[float] = None
    issues_found: int = 0
    issues_fixed: int = 0
    processing_time: float = 0.0
    error_message: Optional[str] = None
    profile_used: Optional[str] = None
    user: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[str] = None  # JSON string
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessHistory':
        """딕셔너리에서 생성"""
        return cls(**data)
    
    def validate(self) -> None:
        """
        데이터 유효성 검증
        
        Raises:
            ValueError: 유효하지 않은 데이터
        """
        if not self.file_name:
            raise ValueError("파일명은 필수입니다")
        if not self.file_path:
            raise ValueError("파일 경로는 필수입니다")
        if not self.process_type:
            raise ValueError("처리 유형은 필수입니다")
        if self.quality_score is not None:
            if self.quality_score < 0 or self.quality_score > 100:
                raise ValueError("품질 점수는 0-100 범위여야 합니다")
        if self.issues_found < 0:
            raise ValueError("발견된 이슈 수는 음수일 수 없습니다")
        if self.issues_fixed < 0:
            raise ValueError("수정된 이슈 수는 음수일 수 없습니다")
        if self.processing_time < 0:
            raise ValueError("처리 시간은 음수일 수 없습니다")