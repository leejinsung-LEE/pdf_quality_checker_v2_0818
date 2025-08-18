# -*- coding: utf-8 -*-
"""
백업 매니저 메인 클래스

백업 시스템의 핵심 기능을 통합 관리합니다.
"""

import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from .models import BackupInfo, BackupStatistics
from .storage import BackupStorage
from .compression import BackupCompressor
from .cleanup import BackupCleaner
from .rollback import BackupRollback


class BackupManager:
    """백업 및 롤백 관리자"""
    
    def __init__(self, 
                 backup_dir: Optional[Path] = None,
                 max_backups_per_file: int = 5,
                 retention_days: int = 30,
                 compress_backups: bool = True,
                 logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            backup_dir: 백업 디렉토리
            max_backups_per_file: 파일당 최대 백업 수
            retention_days: 백업 보관 일수
            compress_backups: 백업 압축 여부
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 백업 디렉토리 설정
        if backup_dir is None:
            backup_dir = Path("data/backups")
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 설정
        self.max_backups_per_file = max_backups_per_file
        self.retention_days = retention_days
        self.compress_backups = compress_backups
        
        # 컴포넌트 초기화
        self.storage = BackupStorage(self.backup_dir, self.logger)
        self.compressor = BackupCompressor(self.logger)
        self.cleaner = BackupCleaner(retention_days, max_backups_per_file, self.logger)
        self.rollback_manager = BackupRollback(
            self.backup_dir, compress_backups, self.logger
        )
        
        # 백업 인덱스
        self.backup_index: Dict[str, List[BackupInfo]] = {}
        
        # 초기화 시 인덱스 로드 및 정리
        self._initialize()
        
    def _initialize(self):
        """초기화 작업"""
        # 인덱스 로드
        self.backup_index = self.storage.load_index()
        
        # 오래된 백업 정리
        self.backup_index, deleted_count = self.cleaner.cleanup_old_backups(
            self.backup_index
        )
        
        if deleted_count > 0:
            self.storage.save_index(self.backup_index)
            
    def create_backup(self, 
                     file_path: Path,
                     profile_used: str = "default",
                     changes_to_make: List[str] = None,
                     metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        백업 생성
        
        Args:
            file_path: 원본 파일 경로
            profile_used: 사용된 프로파일
            changes_to_make: 적용될 변경사항 목록
            metadata: 추가 메타데이터
            
        Returns:
            str: 백업 ID (실패 시 None)
        """
        if not file_path.exists():
            self.logger.error(f"파일을 찾을 수 없습니다: {file_path}")
            return None
            
        try:
            # 백업 ID 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = self._calculate_file_hash(file_path)
            backup_id = f"{timestamp}_{file_hash[:8]}"
            
            # 백업 경로 설정 및 파일 저장
            if self.compress_backups:
                # 압축 백업
                backup_path = self.compressor.compress_backup(
                    file_path, backup_id, self.backup_dir
                )
                if not backup_path:
                    return None
            else:
                # 일반 백업
                backup_subdir = self.backup_dir / file_path.name
                backup_subdir.mkdir(exist_ok=True)
                backup_path = backup_subdir / f"{backup_id}_{file_path.name}"
                
                if not self.storage.save_backup_file(file_path, backup_path):
                    return None
                    
            # 백업 정보 생성
            backup_info = BackupInfo(
                backup_id=backup_id,
                original_path=str(file_path),
                backup_path=str(backup_path),
                file_hash=file_hash,
                file_size=file_path.stat().st_size,
                created_at=datetime.now().isoformat(),
                profile_used=profile_used,
                changes_made=changes_to_make or [],
                metadata=metadata or {}
            )
            
            # 인덱스에 추가
            file_key = str(file_path)
            if file_key not in self.backup_index:
                self.backup_index[file_key] = []
            self.backup_index[file_key].append(backup_info)
            
            # 파일당 최대 백업 수 제한
            if len(self.backup_index[file_key]) > self.max_backups_per_file:
                self.backup_index, _ = self.cleaner.enforce_max_backups(
                    self.backup_index, file_key
                )
                
            # 인덱스 저장
            self.storage.save_index(self.backup_index)
            
            self.logger.info(f"백업 생성 완료: {backup_id} ({file_path.name})")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"백업 생성 실패: {e}")
            return None
            
    def rollback(self, 
                 file_path: Path,
                 backup_id: Optional[str] = None,
                 keep_current: bool = True) -> bool:
        """
        롤백 실행
        
        Args:
            file_path: 복구할 파일 경로
            backup_id: 특정 백업 ID (None이면 최신 백업)
            keep_current: 현재 파일을 백업으로 보관
            
        Returns:
            bool: 성공 여부
        """
        success, error_msg = self.rollback_manager.rollback(
            file_path, self.backup_index, backup_id, keep_current
        )
        
        if success and keep_current:
            # 인덱스 다시 로드 (현재 파일 백업이 추가되었을 수 있음)
            self.backup_index = self.storage.load_index()
            
        return success
        
    def get_backup_history(self, file_path: Path) -> List[BackupInfo]:
        """
        특정 파일의 백업 이력 조회
        
        Args:
            file_path: 파일 경로
            
        Returns:
            List[BackupInfo]: 백업 정보 목록
        """
        file_key = str(file_path)
        return self.backup_index.get(file_key, [])
        
    def verify_backup(self, backup_id: str) -> Tuple[bool, str]:
        """
        백업 무결성 검증
        
        Args:
            backup_id: 백업 ID
            
        Returns:
            Tuple[bool, str]: (성공 여부, 메시지)
        """
        # 백업 찾기
        backup = None
        for backups in self.backup_index.values():
            for b in backups:
                if b.backup_id == backup_id:
                    backup = b
                    break
            if backup:
                break
                
        if not backup:
            return False, "백업을 찾을 수 없습니다"
            
        backup_path = Path(backup.backup_path)
        
        if not backup_path.exists():
            return False, "백업 파일이 존재하지 않습니다"
            
        # 압축 백업인 경우
        if self.compress_backups and backup_path.suffix == '.zip':
            if self.compressor.verify_compressed_backup(backup_path):
                return True, "백업이 유효합니다"
            else:
                return False, "백업 파일이 손상되었습니다"
                
        # 일반 백업인 경우 크기 확인
        if backup_path.stat().st_size != backup.file_size:
            return False, "파일 크기가 일치하지 않습니다"
            
        return True, "백업이 유효합니다"
        
    def cleanup_old_backups(self) -> int:
        """
        오래된 백업 정리
        
        Returns:
            int: 삭제된 백업 수
        """
        self.backup_index, deleted_count = self.cleaner.cleanup_old_backups(
            self.backup_index
        )
        
        if deleted_count > 0:
            self.storage.save_index(self.backup_index)
            
        return deleted_count
        
    def get_backup_statistics(self) -> Dict[str, Any]:
        """백업 통계 조회"""
        total_backups = sum(len(backups) for backups in self.backup_index.values())
        total_size = 0
        
        for backups in self.backup_index.values():
            for backup in backups:
                backup_path = Path(backup.backup_path)
                if backup_path.exists():
                    total_size += backup_path.stat().st_size
                    
        stats = BackupStatistics(
            total_files_backed_up=len(self.backup_index),
            total_backups=total_backups,
            total_size_mb=total_size / (1024 * 1024),
            retention_days=self.retention_days,
            max_backups_per_file=self.max_backups_per_file,
            compression_enabled=self.compress_backups
        )
        
        return stats.to_dict()
        
    def export_backup_list(self, output_path: Path) -> bool:
        """
        백업 목록 내보내기
        
        Args:
            output_path: 출력 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'statistics': self.get_backup_statistics(),
                'backups': {}
            }
            
            for file_path, backups in self.backup_index.items():
                export_data['backups'][file_path] = [
                    backup.to_dict() for backup in backups
                ]
                
            with open(output_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"백업 목록 내보내기 완료: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"백업 목록 내보내기 실패: {e}")
            return False
            
    def _calculate_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()