# src/processing/pipeline/models.py
"""
파이프라인 데이터 모델 및 옵션 정의
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

from .enums import ProcessingStatus

# 타입 체킹용 임포트
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.models import AnalysisResult
    from ...core.quality_checker import QualityCheckResult


@dataclass
class PipelineOptions:
    """파이프라인 처리 옵션"""
    profile_name: str = "default"
    check_options: Dict[str, bool] = field(default_factory=dict)  # 검사 옵션 추가
    auto_fix: bool = False
    fix_options: Dict[str, bool] = field(default_factory=dict)
    generate_report: bool = True
    report_formats: List[str] = field(default_factory=lambda: ['html'])
    save_to_database: bool = True
    move_to_completed: bool = False
    output_folder: Optional[Path] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        if self.check_options is None:
            self.check_options = {}
        if self.fix_options is None:
            self.fix_options = {}
        if self.report_formats is None:
            self.report_formats = ['html']


@dataclass
class ProcessingResult:
    """처리 결과"""
    file_path: Path
    status: ProcessingStatus
    analysis_result: Optional['AnalysisResult'] = None  # 분석 결과 추가
    quality_result: Optional['QualityCheckResult'] = None
    fix_result: Optional[Dict[str, Any]] = None
    report_paths: Dict[str, Path] = field(default_factory=dict)
    error: Optional[str] = None
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """성공 여부"""
        return self.status == ProcessingStatus.COMPLETED
    
    @property
    def has_errors(self) -> bool:
        """오류 존재 여부"""
        if self.quality_result:
            return self.quality_result.has_errors
        return False
    
    @property
    def has_warnings(self) -> bool:
        """경고 존재 여부"""
        if self.quality_result:
            return self.quality_result.has_warnings
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'file_path': str(self.file_path),
            'status': self.status.value,
            'has_analysis': self.analysis_result is not None,  # 분석 결과 포함 여부
            'has_errors': self.has_errors,
            'has_warnings': self.has_warnings,
            'error_count': self.quality_result.error_count if self.quality_result else 0,
            'warning_count': self.quality_result.warning_count if self.quality_result else 0,
            'quality_score': self.quality_result.quality_score if self.quality_result else 0,
            'auto_fixed': bool(self.fix_result) if self.fix_result else False,
            'report_paths': {fmt: str(path) for fmt, path in self.report_paths.items()},
            'error': self.error,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat()
        }