# -*- coding: utf-8 -*-
"""
백업 저장소 관리

백업 파일의 저장, 로드, 인덱스 관리를 담당합니다.
"""

import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .models import BackupInfo


class BackupStorage:
    """백업 저장소 관리자"""
    
    def __init__(self, backup_dir: Path, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            backup_dir: 백업 디렉토리
            logger: 로거
        """
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        
        # 인덱스 파일 경로
        self.index_file = self.backup_dir / "backup_index.json"
        
    def load_index(self) -> Dict[str, List[BackupInfo]]:
        """
        백업 인덱스 로드
        
        Returns:
            Dict[str, List[BackupInfo]]: 파일별 백업 정보
        """
        if not self.index_file.exists():
            return {}
            
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # BackupInfo 객체로 변환
            index = {}
            for file_path, backups in data.items():
                index[file_path] = [
                    BackupInfo.from_dict(backup) for backup in backups
                ]
            return index
            
        except Exception as e:
            self.logger.error(f"백업 인덱스 로드 실패: {e}")
            return {}
            
    def save_index(self, index: Dict[str, List[BackupInfo]]) -> bool:
        """
        백업 인덱스 저장
        
        Args:
            index: 백업 인덱스
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 딕셔너리로 변환
            data = {}
            for file_path, backups in index.items():
                data[file_path] = [backup.to_dict() for backup in backups]
                
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"백업 인덱스 저장 실패: {e}")
            return False
            
    def save_backup_file(self, source_path: Path, backup_path: Path) -> bool:
        """
        백업 파일 저장
        
        Args:
            source_path: 원본 파일 경로
            backup_path: 백업 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 백업 디렉토리 생성
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 복사
            shutil.copy2(source_path, backup_path)
            
            self.logger.debug(f"백업 파일 저장: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"백업 파일 저장 실패: {e}")
            return False
            
    def delete_backup_file(self, backup_path: Path) -> bool:
        """
        백업 파일 삭제
        
        Args:
            backup_path: 백업 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            if backup_path.exists():
                backup_path.unlink()
                self.logger.debug(f"백업 파일 삭제: {backup_path}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"백업 파일 삭제 실패: {e}")
            return False
            
    def restore_backup_file(self, backup_path: Path, target_path: Path) -> bool:
        """
        백업 파일 복원
        
        Args:
            backup_path: 백업 파일 경로
            target_path: 복원 대상 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            if not backup_path.exists():
                self.logger.error(f"백업 파일을 찾을 수 없습니다: {backup_path}")
                return False
                
            # 대상 디렉토리 확인
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 복사
            shutil.copy2(backup_path, target_path)
            
            self.logger.info(f"백업 파일 복원: {backup_path} -> {target_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"백업 파일 복원 실패: {e}")
            return False
            
    def get_backup_size(self, backup_path: Path) -> int:
        """
        백업 파일 크기 조회
        
        Args:
            backup_path: 백업 파일 경로
            
        Returns:
            int: 파일 크기 (바이트)
        """
        try:
            if backup_path.exists():
                return backup_path.stat().st_size
            return 0
        except (OSError, PermissionError) as e:
            self.logger.error(f"백업 파일 크기 조회 실패: {e}")
            return 0
            
    def load_rollback_history(self) -> List[Dict]:
        """롤백 이력 로드"""
        rollback_log = self.backup_dir / "rollback_history.json"
        
        if rollback_log.exists():
            try:
                with open(rollback_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"롤백 이력 로드 실패: {e}")
                
        return []
        
    def save_rollback_history(self, history: List[Dict]) -> bool:
        """롤백 이력 저장"""
        rollback_log = self.backup_dir / "rollback_history.json"
        
        try:
            with open(rollback_log, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"롤백 이력 저장 실패: {e}")
            return False