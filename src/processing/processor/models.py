# src/processing/processor/models.py
"""
프로세서 데이터 모델 정의
"""

from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import hashlib
from dataclasses import dataclass, field


@dataclass
class FileInfo:
    """처리할 파일 정보"""
    path: Path
    file_id: str
    folder_config: Optional[Dict[str, Any]] = None
    priority: int = 0
    added_at: datetime = field(default_factory=datetime.now)
    
    @property
    def filename(self) -> str:
        """파일명"""
        return self.path.name
    
    @property
    def size(self) -> int:
        """파일 크기"""
        try:
            return self.path.stat().st_size
        except:
            return 0
    
    @property
    def size_mb(self) -> float:
        """파일 크기 (MB)"""
        return self.size / (1024 * 1024)
    
    def generate_hash(self) -> str:
        """파일 해시 생성"""
        hasher = hashlib.md5()
        try:
            with open(self.path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return ""