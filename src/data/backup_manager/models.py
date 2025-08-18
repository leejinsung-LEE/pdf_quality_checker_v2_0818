# -*- coding: utf-8 -*-
"""
백업 관리 데이터 모델

백업 정보와 관련된 데이터 구조를 정의합니다.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class BackupInfo:
    """백업 정보"""
    backup_id: str
    original_path: str
    backup_path: str
    file_hash: str
    file_size: int
    created_at: str
    profile_used: str
    changes_made: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupInfo':
        """딕셔너리에서 생성"""
        return cls(**data)


@dataclass
class BackupMetadata:
    """백업 메타데이터"""
    backup_count: int
    total_size: int
    oldest_backup: str
    newest_backup: str
    
    @classmethod
    def from_backup_list(cls, backups: List[BackupInfo]) -> 'BackupMetadata':
        """백업 목록에서 메타데이터 생성"""
        if not backups:
            return cls(
                backup_count=0,
                total_size=0,
                oldest_backup="",
                newest_backup=""
            )
        
        return cls(
            backup_count=len(backups),
            total_size=sum(b.file_size for b in backups),
            oldest_backup=backups[0].created_at,
            newest_backup=backups[-1].created_at
        )


@dataclass
class BackupStatistics:
    """백업 통계 정보"""
    total_files_backed_up: int
    total_backups: int
    total_size_mb: float
    retention_days: int
    max_backups_per_file: int
    compression_enabled: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)


@dataclass
class RollbackRecord:
    """롤백 이력 레코드"""
    file_path: str
    backup_id: str
    rolled_back_at: str
    
    @classmethod
    def create(cls, file_path: str, backup_id: str) -> 'RollbackRecord':
        """롤백 레코드 생성"""
        return cls(
            file_path=file_path,
            backup_id=backup_id,
            rolled_back_at=datetime.now().isoformat()
        )