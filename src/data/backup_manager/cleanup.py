# -*- coding: utf-8 -*-
"""
백업 정리 관리

오래된 백업 정리 및 보관 정책 관리를 담당합니다.
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .models import BackupInfo


class BackupCleaner:
    """백업 정리 관리자"""
    
    def __init__(self, 
                 retention_days: int = 30,
                 max_backups_per_file: int = 5,
                 logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            retention_days: 백업 보관 일수
            max_backups_per_file: 파일당 최대 백업 수
            logger: 로거
        """
        self.retention_days = retention_days
        self.max_backups_per_file = max_backups_per_file
        self.logger = logger or logging.getLogger(__name__)
        
    def cleanup_old_backups(self, 
                           backup_index: Dict[str, List[BackupInfo]]) -> Tuple[Dict[str, List[BackupInfo]], int]:
        """
        오래된 백업 정리
        
        Args:
            backup_index: 백업 인덱스
            
        Returns:
            Tuple[Dict[str, List[BackupInfo]], int]: (정리된 인덱스, 삭제된 백업 수)
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        cleaned_index = {}
        
        for file_key, backups in backup_index.items():
            remaining_backups = []
            
            for backup in backups:
                try:
                    created_at = datetime.fromisoformat(backup.created_at)
                    if created_at < cutoff_date:
                        # 백업 파일 삭제
                        if self._delete_backup_file(backup.backup_path):
                            deleted_count += 1
                            self.logger.debug(f"오래된 백업 삭제: {backup.backup_id}")
                        else:
                            # 삭제 실패 시 유지
                            remaining_backups.append(backup)
                    else:
                        remaining_backups.append(backup)
                        
                except Exception as e:
                    self.logger.error(f"백업 정리 오류: {e}")
                    remaining_backups.append(backup)
                    
            if remaining_backups:
                cleaned_index[file_key] = remaining_backups
                
        if deleted_count > 0:
            self.logger.info(f"오래된 백업 {deleted_count}개 삭제")
            
        return cleaned_index, deleted_count
        
    def enforce_max_backups(self, 
                           backup_index: Dict[str, List[BackupInfo]],
                           file_key: str) -> Tuple[Dict[str, List[BackupInfo]], int]:
        """
        파일당 최대 백업 수 제한 적용
        
        Args:
            backup_index: 백업 인덱스
            file_key: 파일 키
            
        Returns:
            Tuple[Dict[str, List[BackupInfo]], int]: (업데이트된 인덱스, 삭제된 백업 수)
        """
        if file_key not in backup_index:
            return backup_index, 0
            
        backups = backup_index[file_key]
        deleted_count = 0
        
        # 최대 개수 초과 시 오래된 백업부터 삭제
        while len(backups) > self.max_backups_per_file:
            oldest_backup = backups[0]
            
            if self._delete_backup_file(oldest_backup.backup_path):
                backups.pop(0)
                deleted_count += 1
                self.logger.debug(f"초과 백업 제거: {oldest_backup.backup_id}")
            else:
                # 삭제 실패 시 중단
                break
                
        backup_index[file_key] = backups
        return backup_index, deleted_count
        
    def remove_orphaned_backups(self, backup_dir: Path,
                               backup_index: Dict[str, List[BackupInfo]]) -> int:
        """
        인덱스에 없는 고아 백업 파일 제거
        
        Args:
            backup_dir: 백업 디렉토리
            backup_index: 백업 인덱스
            
        Returns:
            int: 삭제된 파일 수
        """
        # 인덱스에 있는 모든 백업 파일 경로 수집
        indexed_paths = set()
        for backups in backup_index.values():
            for backup in backups:
                indexed_paths.add(Path(backup.backup_path))
                
        # 실제 백업 파일 스캔
        deleted_count = 0
        
        for backup_file in backup_dir.rglob("*.zip"):
            if backup_file not in indexed_paths:
                try:
                    backup_file.unlink()
                    deleted_count += 1
                    self.logger.debug(f"고아 백업 파일 삭제: {backup_file}")
                except Exception as e:
                    self.logger.error(f"고아 백업 삭제 실패: {e}")
                    
        # 압축하지 않은 백업도 확인
        for backup_file in backup_dir.rglob("*.pdf"):
            # 백업 ID 패턴 확인 (YYYYMMDD_HHMMSS_)
            if len(backup_file.stem) > 16 and backup_file.stem[8] == '_' and backup_file.stem[15] == '_':
                if backup_file not in indexed_paths:
                    try:
                        backup_file.unlink()
                        deleted_count += 1
                        self.logger.debug(f"고아 백업 파일 삭제: {backup_file}")
                    except Exception as e:
                        self.logger.error(f"고아 백업 삭제 실패: {e}")
                        
        if deleted_count > 0:
            self.logger.info(f"고아 백업 파일 {deleted_count}개 삭제")
            
        return deleted_count
        
    def calculate_cleanup_candidates(self,
                                    backup_index: Dict[str, List[BackupInfo]]) -> List[BackupInfo]:
        """
        정리 대상 백업 계산
        
        Args:
            backup_index: 백업 인덱스
            
        Returns:
            List[BackupInfo]: 정리 대상 백업 목록
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        candidates = []
        
        for file_key, backups in backup_index.items():
            # 보관 기간 초과 백업
            for backup in backups:
                try:
                    created_at = datetime.fromisoformat(backup.created_at)
                    if created_at < cutoff_date:
                        candidates.append(backup)
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"백업 날짜 파싱 실패 {backup.backup_id}: {e}")
                    
            # 최대 개수 초과 백업
            if len(backups) > self.max_backups_per_file:
                excess_count = len(backups) - self.max_backups_per_file
                for backup in backups[:excess_count]:
                    if backup not in candidates:
                        candidates.append(backup)
                        
        return candidates
        
    def _delete_backup_file(self, backup_path: str) -> bool:
        """
        백업 파일 삭제
        
        Args:
            backup_path: 백업 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            path = Path(backup_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            self.logger.error(f"백업 파일 삭제 실패: {e}")
            return False