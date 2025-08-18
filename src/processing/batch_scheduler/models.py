# -*- coding: utf-8 -*-
"""
배치 스케줄러 데이터 모델

스케줄 작업의 데이터 구조와 열거형 정의
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional


class ScheduleFrequency(Enum):
    """스케줄 빈도"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    HOURLY = "hourly"
    CUSTOM = "custom"


class ScheduleStatus(Enum):
    """스케줄 상태"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScheduleTask:
    """
    스케줄 작업 데이터 모델
    
    배치 작업의 스케줄 정보와 실행 설정을 저장하는 데이터클래스
    """
    # 기본 정보
    id: str
    name: str
    frequency: ScheduleFrequency
    time: str  # HH:MM 형식
    
    # 스케줄 옵션
    weekday: Optional[int] = None  # 0=월요일, 6=일요일
    day_of_month: Optional[int] = None  # 1-31
    
    # 실행 설정
    folder_path: str = ""
    profile: str = "default"
    auto_fix: bool = False
    recursive: bool = True
    file_pattern: str = "*.pdf"
    
    # 상태 정보
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    
    # 통계
    run_count: int = 0
    error_count: int = 0
    
    # 메타데이터
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'frequency': self.frequency.value,
            'time': self.time,
            'weekday': self.weekday,
            'day_of_month': self.day_of_month,
            'folder_path': self.folder_path,
            'profile': self.profile,
            'auto_fix': self.auto_fix,
            'recursive': self.recursive,
            'file_pattern': self.file_pattern,
            'enabled': self.enabled,
            'last_run': self.last_run,
            'next_run': self.next_run,
            'run_count': self.run_count,
            'error_count': self.error_count,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduleTask':
        """딕셔너리에서 생성"""
        # frequency 변환
        freq_value = data.get('frequency', 'daily')
        if isinstance(freq_value, str):
            data['frequency'] = ScheduleFrequency(freq_value)
        elif not isinstance(freq_value, ScheduleFrequency):
            data['frequency'] = ScheduleFrequency.DAILY
            
        return cls(**data)
    
    @property
    def success_rate(self) -> float:
        """성공률 계산"""
        if self.run_count == 0:
            return 0.0
        return ((self.run_count - self.error_count) / self.run_count) * 100
    
    @property
    def is_active(self) -> bool:
        """활성 상태 확인"""
        return self.enabled and self.frequency != ScheduleFrequency.ONCE
    
    def update_stats(self, success: bool = True):
        """실행 통계 업데이트"""
        self.run_count += 1
        if not success:
            self.error_count += 1
        self.last_run = datetime.now().isoformat()
        
        # ONCE 타입은 실행 후 비활성화
        if self.frequency == ScheduleFrequency.ONCE:
            self.enabled = False
    
    def reset_stats(self):
        """통계 초기화"""
        self.run_count = 0
        self.error_count = 0
        self.last_run = None