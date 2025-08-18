# -*- coding: utf-8 -*-
"""
백업 롤백 관리

백업된 파일의 롤백 기능을 제공합니다.
"""

import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime

from .models import BackupInfo, RollbackRecord
from .compression import BackupCompressor
from .storage import BackupStorage


class BackupRollback:
    """백업 롤백 관리자"""
    
    def __init__(self, 
                 backup_dir: Path,
                 compress_backups: bool = True,
                 logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            backup_dir: 백업 디렉토리
            compress_backups: 백업 압축 여부
            logger: 로거
        """
        self.backup_dir = backup_dir
        self.compress_backups = compress_backups
        self.logger = logger or logging.getLogger(__name__)
        
        # 컴포넌트 초기화
        self.compressor = BackupCompressor(logger)
        self.storage = BackupStorage(backup_dir, logger)
        
    def rollback(self, 
                 file_path: Path,
                 backup_index: Dict[str, List[BackupInfo]],
                 backup_id: Optional[str] = None,
                 keep_current: bool = True) -> Tuple[bool, Optional[str]]:
        """
        롤백 실행
        
        Args:
            file_path: 복구할 파일 경로
            backup_index: 백업 인덱스
            backup_id: 특정 백업 ID (None이면 최신 백업)
            keep_current: 현재 파일을 백업으로 보관
            
        Returns:
            Tuple[bool, Optional[str]]: (성공 여부, 오류 메시지)
        """
        file_key = str(file_path)
        
        # 백업 확인
        if file_key not in backup_index or not backup_index[file_key]:
            return False, f"백업을 찾을 수 없습니다: {file_path}"
            
        try:
            # 백업 선택
            backup = self._select_backup(backup_index[file_key], backup_id)
            if not backup:
                return False, f"백업 ID를 찾을 수 없습니다: {backup_id}"
                
            backup_path = Path(backup.backup_path)
            
            if not backup_path.exists():
                return False, f"백업 파일을 찾을 수 없습니다: {backup_path}"
                
            # 현재 파일 백업 (선택적)
            if keep_current and file_path.exists():
                current_backup_id = self._backup_current_file(file_path, backup.backup_id)
                if current_backup_id:
                    self.logger.info(f"현재 파일 백업 완료: {current_backup_id}")
                    
            # 복구 실행
            success = self._restore_backup(backup_path, file_path)
            
            if success:
                # 롤백 이력 기록
                self._record_rollback(file_path, backup.backup_id)
                self.logger.info(f"롤백 완료: {file_path} (백업 ID: {backup.backup_id})")
                return True, None
            else:
                return False, "백업 파일 복원 실패"
                
        except Exception as e:
            error_msg = f"롤백 실패: {e}"
            self.logger.error(error_msg)
            return False, error_msg
            
    def _select_backup(self, backups: List[BackupInfo], 
                      backup_id: Optional[str]) -> Optional[BackupInfo]:
        """
        백업 선택
        
        Args:
            backups: 백업 목록
            backup_id: 특정 백업 ID
            
        Returns:
            Optional[BackupInfo]: 선택된 백업
        """
        if backup_id:
            # 특정 백업 ID로 검색
            for backup in backups:
                if backup.backup_id == backup_id:
                    return backup
            return None
        else:
            # 최신 백업 반환
            return backups[-1] if backups else None
            
    def _restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """
        백업 파일 복원
        
        Args:
            backup_path: 백업 파일 경로
            target_path: 복원 대상 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            if self.compress_backups and backup_path.suffix == '.zip':
                # 압축된 백업 복원
                return self.compressor.decompress_backup(backup_path, target_path)
            else:
                # 일반 백업 복원
                return self.storage.restore_backup_file(backup_path, target_path)
                
        except Exception as e:
            self.logger.error(f"백업 복원 실패: {e}")
            return False
            
    def _backup_current_file(self, file_path: Path, 
                            rollback_from: str) -> Optional[str]:
        """
        현재 파일을 백업으로 저장
        
        Args:
            file_path: 현재 파일 경로
            rollback_from: 롤백 원본 백업 ID
            
        Returns:
            Optional[str]: 새 백업 ID
        """
        try:
            # 백업 ID 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"{timestamp}_rollback"
            
            # 백업 경로 생성
            backup_subdir = self.backup_dir / file_path.name
            backup_subdir.mkdir(exist_ok=True)
            
            if self.compress_backups:
                # 압축 백업
                backup_path = self.compressor.compress_backup(
                    file_path, backup_id, self.backup_dir
                )
            else:
                # 일반 백업
                backup_path = backup_subdir / f"{backup_id}_{file_path.name}"
                self.storage.save_backup_file(file_path, backup_path)
                
            if backup_path:
                self.logger.debug(f"현재 파일 백업 생성: {backup_id}")
                return backup_id
                
        except Exception as e:
            self.logger.error(f"현재 파일 백업 실패: {e}")
            
        return None
        
    def _record_rollback(self, file_path: Path, backup_id: str):
        """
        롤백 이력 기록
        
        Args:
            file_path: 파일 경로
            backup_id: 백업 ID
        """
        try:
            # 롤백 레코드 생성
            record = RollbackRecord.create(str(file_path), backup_id)
            
            # 기존 이력 로드
            history = self.storage.load_rollback_history()
            
            # 새 이력 추가
            history.append({
                'file_path': record.file_path,
                'backup_id': record.backup_id,
                'rolled_back_at': record.rolled_back_at
            })
            
            # 저장
            self.storage.save_rollback_history(history)
            
        except Exception as e:
            self.logger.error(f"롤백 이력 기록 실패: {e}")
            
    def verify_rollback_possibility(self, 
                                   file_path: Path,
                                   backup_index: Dict[str, List[BackupInfo]],
                                   backup_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        롤백 가능 여부 확인
        
        Args:
            file_path: 파일 경로
            backup_index: 백업 인덱스
            backup_id: 백업 ID
            
        Returns:
            Tuple[bool, str]: (가능 여부, 메시지)
        """
        file_key = str(file_path)
        
        # 백업 존재 확인
        if file_key not in backup_index or not backup_index[file_key]:
            return False, "사용 가능한 백업이 없습니다"
            
        # 백업 선택
        backup = self._select_backup(backup_index[file_key], backup_id)
        if not backup:
            return False, f"백업을 찾을 수 없습니다: {backup_id}"
            
        # 백업 파일 존재 확인
        backup_path = Path(backup.backup_path)
        if not backup_path.exists():
            return False, "백업 파일이 존재하지 않습니다"
            
        # 압축 백업인 경우 무결성 확인
        if self.compress_backups and backup_path.suffix == '.zip':
            if not self.compressor.verify_compressed_backup(backup_path):
                return False, "백업 파일이 손상되었습니다"
                
        return True, f"롤백 가능 (백업 ID: {backup.backup_id})"