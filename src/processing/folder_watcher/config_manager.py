# src/processing/folder_watcher/config_manager.py
"""
폴더 감시 설정 관리
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .base import FolderConfig


class ConfigManager:
    """설정 파일 관리자"""
    
    def __init__(self, config_file: str = "data/config/folder_watch_config.json"):
        """
        설정 관리자 초기화
        
        Args:
            config_file: 설정 파일 경로
        """
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        self.folder_configs: Dict[str, FolderConfig] = {}
    
    def load_config(self) -> Dict[str, FolderConfig]:
        """설정 파일 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.folder_configs.clear()
                for folder_data in data.get('folders', []):
                    config = FolderConfig.from_dict(folder_data)
                    self.folder_configs[str(config.path)] = config
                
                self.logger.info(f"{len(self.folder_configs)}개 폴더 설정 로드됨")
            except Exception as e:
                self.logger.error(f"설정 파일 로드 실패: {e}")
        
        return self.folder_configs
    
    def save_config(self, folder_configs: Dict[str, FolderConfig]) -> bool:
        """설정 파일 저장"""
        try:
            data = {
                'folders': [
                    config.to_dict() 
                    for config in folder_configs.values()
                ],
                'last_saved': datetime.now().isoformat()
            }
            
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"설정 파일 저장 실패: {e}")
            return False
    
    def validate_folder_config(self, path: Path, folder_configs: Dict[str, FolderConfig], 
                              recursive: bool = False) -> tuple[bool, str]:
        """
        폴더 설정 유효성 검증
        
        Args:
            path: 검증할 폴더 경로
            folder_configs: 기존 폴더 설정들
            recursive: 재귀 옵션
            
        Returns:
            (유효성, 오류 메시지)
        """
        folder_path = Path(path).absolute()
        folder_path_str = str(folder_path)
        
        # 폴더 존재 확인
        if not folder_path.exists():
            return True, ""  # 폴더가 없으면 생성 가능
        
        if not folder_path.is_dir():
            return False, f"디렉토리가 아님: {folder_path}"
        
        # 이미 등록된 폴더인지 확인
        if folder_path_str in folder_configs:
            return True, ""  # 업데이트 가능
        
        # 상위/하위 폴더 관계 체크
        for existing_path in folder_configs.keys():
            existing = Path(existing_path)
            
            # 새 폴더가 기존 폴더의 하위 폴더인 경우
            try:
                if folder_path.is_relative_to(existing):
                    existing_config = folder_configs[existing_path]
                    if existing_config.recursive:
                        return False, f"상위 폴더 {existing}가 이미 재귀적으로 감시 중"
            except ValueError:
                pass  # Windows에서 다른 드라이브일 경우
            
            # 기존 폴더가 새 폴더의 하위 폴더인 경우
            try:
                if existing.is_relative_to(folder_path) and recursive:
                    return False, f"하위 폴더 {existing}가 이미 등록됨. 재귀 옵션 충돌"
            except ValueError:
                pass
        
        return True, ""