# src/processing/folder_watcher/base.py
"""
폴더 감시 시스템의 기본 데이터 구조 및 설정
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class FolderConfig:
    """폴더별 설정"""
    path: Path
    profile: str = 'default'
    auto_fix_settings: Dict[str, bool] = field(default_factory=dict)
    check_settings: Dict[str, bool] = field(default_factory=dict)  # 검사 종류 설정
    output_folder: Optional[Path] = None
    enabled: bool = True
    recursive: bool = False
    file_patterns: List[str] = field(default_factory=lambda: ['*.pdf', '*.PDF'])
    auto_process: bool = True  # 자동 처리 여부
    generate_report: bool = True  # 보고서 생성 여부
    report_formats: List[str] = field(default_factory=lambda: ['html'])  # 보고서 형식
    
    # 통계
    files_processed: int = 0
    last_processed: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'path': str(self.path),
            'profile': self.profile,
            'auto_fix_settings': self.auto_fix_settings,
            'check_settings': self.check_settings,
            'output_folder': str(self.output_folder) if self.output_folder else None,
            'enabled': self.enabled,
            'recursive': self.recursive,
            'file_patterns': self.file_patterns,
            'auto_process': self.auto_process,
            'generate_report': self.generate_report,
            'report_formats': self.report_formats,
            'files_processed': self.files_processed,
            'last_processed': self.last_processed.isoformat() if self.last_processed else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderConfig':
        """딕셔너리에서 생성"""
        config = cls(
            path=Path(data['path']),
            profile=data.get('profile', 'default'),
            auto_fix_settings=data.get('auto_fix_settings', {}),
            check_settings=data.get('check_settings', {}),
            output_folder=Path(data['output_folder']) if data.get('output_folder') else None,
            enabled=data.get('enabled', True),
            recursive=data.get('recursive', False),
            file_patterns=data.get('file_patterns', ['*.pdf', '*.PDF']),
            auto_process=data.get('auto_process', True),
            generate_report=data.get('generate_report', True),
            report_formats=data.get('report_formats', ['html'])
        )
        
        config.files_processed = data.get('files_processed', 0)
        if data.get('last_processed'):
            config.last_processed = datetime.fromisoformat(data['last_processed'])
        
        return config