# src/processing/folder_watcher/watcher.py
"""
메인 폴더 감시기 클래스
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

from .base import FolderConfig
from .config_manager import ConfigManager
from .monitor import FolderMonitor
from ..processor import PDFProcessor
from ..batch_processor import BatchProcessor, ProcessingPriority


class FolderWatcher:
    """
    다중 폴더 감시기
    
    여러 폴더를 동시에 감시하고 새 PDF 파일을 자동으로 처리합니다.
    """
    
    def __init__(self, 
                 config_file: str = "data/config/folder_watch_config.json",
                 use_batch_processor: bool = True,
                 logger: Optional[logging.Logger] = None):
        """
        폴더 감시기 초기화
        
        Args:
            config_file: 설정 파일 경로
            use_batch_processor: 배치 처리기 사용 여부
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        self.use_batch_processor = use_batch_processor
        
        # 모듈 초기화
        self.config_manager = ConfigManager(config_file)
        self.monitor = FolderMonitor(self.logger)
        
        # 폴더 설정
        self.folder_configs: Dict[str, FolderConfig] = {}
        
        # 처리기
        if use_batch_processor:
            self.batch_processor = BatchProcessor()
        else:
            self.processor = PDFProcessor()
        
        # 콜백
        self.on_file_found: Optional[Callable] = None
        self.on_file_processed: Optional[Callable] = None
        
        # 설정 로드
        self.folder_configs = self.config_manager.load_config()
    
    def add_folder(self, 
                  path: Path,
                  profile: str = 'default',
                  auto_fix_settings: Optional[Dict[str, bool]] = None,
                  check_settings: Optional[Dict[str, bool]] = None,
                  output_folder: Optional[Path] = None,
                  recursive: bool = False) -> bool:
        """
        감시할 폴더 추가
        
        Args:
            path: 폴더 경로
            profile: 프로파일 이름
            auto_fix_settings: 자동 수정 설정
            check_settings: 검사 설정
            output_folder: 출력 폴더
            recursive: 하위 폴더 포함 여부
            
        Returns:
            bool: 추가 성공 여부
        """
        folder_path = Path(path).absolute()
        
        # 폴더 존재 확인
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"폴더 생성됨: {folder_path}")
            except Exception as e:
                self.logger.error(f"폴더 생성 실패: {e}")
                return False
        
        # 유효성 검증
        is_valid, error_msg = self.config_manager.validate_folder_config(
            folder_path, self.folder_configs, recursive
        )
        
        if not is_valid:
            self.logger.error(error_msg)
            return False
        
        folder_path_str = str(folder_path)
        
        # 이미 등록된 폴더인지 확인
        if folder_path_str in self.folder_configs:
            self.logger.warning(f"이미 등록된 폴더: {folder_path}")
            # 기존 설정 업데이트
            existing_config = self.folder_configs[folder_path_str]
            existing_config.profile = profile
            existing_config.auto_fix_settings = auto_fix_settings or {}
            existing_config.check_settings = check_settings or {}
            existing_config.output_folder = output_folder
            existing_config.recursive = recursive
            self.config_manager.save_config(self.folder_configs)
            return True
        
        # 설정 생성
        config = FolderConfig(
            path=folder_path,
            profile=profile,
            auto_fix_settings=auto_fix_settings or {},
            check_settings=check_settings or {},
            output_folder=output_folder,
            recursive=recursive
        )
        
        # 저장
        self.folder_configs[folder_path_str] = config
        self.config_manager.save_config(self.folder_configs)
        
        # 감시 중이면 즉시 시작
        if self.monitor.is_watching:
            self.monitor.add_folder_observer(config, self._on_pdf_found)
        
        self.logger.info(f"폴더 추가됨: {folder_path} (프로파일: {profile})")
        return True
    
    def remove_folder(self, path: Path) -> bool:
        """폴더 제거"""
        folder_path = Path(path).absolute()
        path_str = str(folder_path)
        
        if path_str not in self.folder_configs:
            return False
        
        # 감시 중지
        self.monitor.remove_folder_observer(folder_path)
        
        # 설정 제거
        del self.folder_configs[path_str]
        self.config_manager.save_config(self.folder_configs)
        
        self.logger.info(f"폴더 제거됨: {folder_path}")
        return True
    
    def update_folder(self, path: Path, **kwargs) -> bool:
        """폴더 설정 업데이트"""
        folder_path = Path(path).absolute()
        path_str = str(folder_path)
        
        if path_str not in self.folder_configs:
            return False
        
        config = self.folder_configs[path_str]
        
        # 설정 업데이트
        if 'profile' in kwargs:
            config.profile = kwargs['profile']
        if 'auto_fix_settings' in kwargs:
            config.auto_fix_settings = kwargs['auto_fix_settings']
        if 'check_settings' in kwargs:
            config.check_settings = kwargs['check_settings']
        if 'output_folder' in kwargs:
            config.output_folder = kwargs['output_folder']
        if 'enabled' in kwargs:
            config.enabled = kwargs['enabled']
        if 'recursive' in kwargs:
            config.recursive = kwargs['recursive']
        if 'auto_process' in kwargs:
            config.auto_process = kwargs['auto_process']
        if 'generate_report' in kwargs:
            config.generate_report = kwargs['generate_report']
        if 'report_formats' in kwargs:
            config.report_formats = kwargs['report_formats']
        
        self.config_manager.save_config(self.folder_configs)
        self.logger.info(f"폴더 설정 업데이트: {folder_path}")
        return True
    
    def set_callbacks(self,
                     on_file_found: Optional[Callable] = None,
                     on_file_processed: Optional[Callable] = None):
        """
        콜백 설정
        
        Args:
            on_file_found: 파일 발견 콜백 (file_path, folder_config)
            on_file_processed: 파일 처리 완료 콜백 (file_path, result)
        """
        self.on_file_found = on_file_found
        self.on_file_processed = on_file_processed
    
    def start_watching(self):
        """모든 폴더 감시 시작"""
        # 배치 처리기 시작
        if self.use_batch_processor:
            self.batch_processor.start()
        
        # 모니터 시작
        self.monitor.start_watching(self.folder_configs, self._on_pdf_found)
    
    def stop_watching(self):
        """모든 폴더 감시 중지"""
        # 모니터 중지
        self.monitor.stop_watching()
        
        # 배치 처리기 중지
        if self.use_batch_processor:
            self.batch_processor.stop()
        
        self.logger.info("폴더 감시 중지됨")
    
    def _on_pdf_found(self, file_path: Path, folder_config: FolderConfig):
        """PDF 파일 발견 시 호출"""
        # 자동 처리 확인
        if not folder_config.auto_process:
            self.logger.info(f"파일 발견 (자동 처리 비활성화): {file_path}")
            return
        
        # 통계 업데이트
        folder_config.files_processed += 1
        folder_config.last_processed = datetime.now()
        self.config_manager.save_config(self.folder_configs)
        
        # 콜백 호출
        if self.on_file_found:
            self.on_file_found(file_path, folder_config)
        
        # 처리
        if self.use_batch_processor:
            # 배치 처리기에 추가
            self.batch_processor.add_file(
                file_path,
                priority=ProcessingPriority.NORMAL,
                folder_config=folder_config.to_dict()
            )
        else:
            # 즉시 처리
            result = self.processor.process_file(
                file_path,
                folder_config=folder_config.to_dict()
            )
            
            if self.on_file_processed:
                self.on_file_processed(file_path, result)
        
        self.logger.info(f"PDF 발견 및 처리 시작: {file_path.name}")
    
    def get_status(self) -> Dict[str, Any]:
        """감시 상태 조회"""
        active_folders = [
            config for config in self.folder_configs.values() 
            if config.enabled
        ]
        
        monitor_status = self.monitor.get_status()
        
        return {
            'is_watching': monitor_status['is_watching'],
            'mode': monitor_status['mode'],
            'total_folders': len(self.folder_configs),
            'active_folders': len(active_folders),
            'folders': [
                {
                    'path': config.path.name,
                    'full_path': str(config.path),
                    'profile': config.profile,
                    'enabled': config.enabled,
                    'files_processed': config.files_processed,
                    'last_processed': config.last_processed.isoformat() if config.last_processed else None,
                    'auto_fix': any(config.auto_fix_settings.values()),
                    'auto_process': config.auto_process,
                    'generate_report': config.generate_report
                }
                for config in self.folder_configs.values()
            ]
        }
    
    def get_folder_list(self) -> List[Dict[str, Any]]:
        """폴더 목록 조회"""
        return [
            {
                'path': str(config.path),
                'name': config.path.name,
                'profile': config.profile,
                'enabled': config.enabled,
                'processed': config.files_processed,
                'recursive': config.recursive,
                'auto_fix': any(config.auto_fix_settings.values()),
                'auto_process': config.auto_process
            }
            for config in self.folder_configs.values()
        ]