# src/processing/processor/utils.py
"""
프로세서 유틸리티 함수
"""

from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from ..pipeline import PipelineOptions


def prepare_options(folder_config: Optional[Dict[str, Any]]) -> PipelineOptions:
    """
    폴더 설정을 파이프라인 옵션으로 변환
    
    Args:
        folder_config: 폴더 설정 딕셔너리
        
    Returns:
        파이프라인 옵션
    """
    options = PipelineOptions()
    
    if folder_config:
        # 프로파일
        options.profile_name = folder_config.get('profile', 'default')
        
        # 검사 설정
        check_settings = folder_config.get('check_settings', {})
        if check_settings:
            options.check_options = check_settings
        
        # 자동 수정 설정
        auto_fix_settings = folder_config.get('auto_fix_settings', {})
        if auto_fix_settings:
            options.auto_fix = any(auto_fix_settings.values())
            options.fix_options = auto_fix_settings
        
        # 보고서 설정
        options.generate_report = folder_config.get('generate_report', True)
        options.report_formats = folder_config.get('report_formats', ['html'])
        
        # 출력 폴더
        output_folder = folder_config.get('output_folder')
        if output_folder:
            options.output_folder = Path(output_folder)
    
    return options


def generate_file_id(file_path: Path) -> str:
    """
    파일 ID 생성
    
    Args:
        file_path: 파일 경로
        
    Returns:
        생성된 파일 ID
    """
    # 파일명과 타임스탬프로 고유 ID 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    name_part = file_path.stem[:20]  # 파일명 일부
    return f"{name_part}_{timestamp}"