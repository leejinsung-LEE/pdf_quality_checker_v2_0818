# src/core/fixers/base_fixer.py
"""
자동 수정 기본 클래스

모든 수정 기능의 기본이 되는 추상 클래스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import logging
import tempfile
import shutil

from ..models import PDFDocument, QualityIssue


@dataclass
class FixResult:
    """수정 결과"""
    success: bool
    message: str
    output_path: Optional[Path] = None
    fixes_applied: List[str] = field(default_factory=list)
    backup_path: Optional[Path] = None
    processing_time: float = 0.0
    error: Optional[str] = None
    
    def add_fix(self, fix_name: str):
        """적용된 수정 추가"""
        self.fixes_applied.append(fix_name)


@dataclass
class FixContext:
    """수정 컨텍스트"""
    input_path: Path
    output_path: Optional[Path] = None
    create_backup: bool = True
    overwrite: bool = False
    dry_run: bool = False  # 실제 수정 없이 시뮬레이션만
    options: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """초기화 후처리"""
        if self.output_path is None:
            # 출력 경로가 없으면 입력 파일명에 _fixed 추가
            stem = self.input_path.stem
            suffix = self.input_path.suffix
            self.output_path = self.input_path.parent / f"{stem}_fixed{suffix}"


class BaseFixer(ABC):
    """
    자동 수정 기본 클래스
    
    모든 수정 기능의 기본이 되는 추상 클래스입니다.
    """
    
    def __init__(self, name: str = None):
        """
        수정기 초기화
        
        Args:
            name: 수정기 이름
        """
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(self.name)
    
    @abstractmethod
    def can_fix(self, document: PDFDocument, issues: List[QualityIssue]) -> bool:
        """
        수정 가능 여부 확인
        
        Args:
            document: PDF 문서
            issues: 품질 문제 목록
            
        Returns:
            bool: 수정 가능 여부
        """
        pass
    
    @abstractmethod
    def fix(self, context: FixContext) -> FixResult:
        """
        PDF 수정 실행
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            FixResult: 수정 결과
        """
        pass
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """
        백업 파일 생성
        
        Args:
            file_path: 원본 파일 경로
            
        Returns:
            Path: 백업 파일 경로
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = file_path.parent / "backup"
            backup_dir.mkdir(exist_ok=True)
            
            backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            shutil.copy2(file_path, backup_path)
            
            self.logger.info(f"백업 생성: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"백업 생성 실패: {e}")
            return None
    
    def validate_context(self, context: FixContext) -> bool:
        """
        컨텍스트 유효성 검사
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            bool: 유효성 여부
        """
        # 입력 파일 존재 확인
        if not context.input_path.exists():
            self.logger.error(f"입력 파일이 없습니다: {context.input_path}")
            return False
        
        # PDF 파일인지 확인
        if context.input_path.suffix.lower() != '.pdf':
            self.logger.error(f"PDF 파일이 아닙니다: {context.input_path}")
            return False
        
        # 출력 파일 덮어쓰기 확인
        if context.output_path.exists() and not context.overwrite:
            self.logger.error(f"출력 파일이 이미 존재합니다: {context.output_path}")
            return False
        
        return True
    
    def safe_fix(self, context: FixContext) -> FixResult:
        """
        안전한 수정 실행 (백업 포함)
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            FixResult: 수정 결과
        """
        start_time = datetime.now()
        
        # 컨텍스트 검증
        if not self.validate_context(context):
            return FixResult(
                success=False,
                message="컨텍스트 검증 실패",
                error="유효하지 않은 수정 컨텍스트"
            )
        
        # 백업 생성
        backup_path = None
        if context.create_backup and not context.dry_run:
            backup_path = self.create_backup(context.input_path)
        
        try:
            # 실제 수정 실행
            result = self.fix(context)
            
            # 백업 경로 추가
            result.backup_path = backup_path
            
            # 처리 시간 계산
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            self.logger.error(f"수정 중 오류 발생: {e}")
            
            # 백업에서 복원
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, context.input_path)
                    self.logger.info("백업에서 복원됨")
                except:
                    pass
            
            return FixResult(
                success=False,
                message="수정 실패",
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )


class CompositeFixer(BaseFixer):
    """
    복합 수정기
    
    여러 개의 수정기를 조합하여 사용합니다.
    """
    
    def __init__(self):
        """복합 수정기 초기화"""
        super().__init__("CompositeFixer")
        self.fixers: List[BaseFixer] = []
    
    def add_fixer(self, fixer: BaseFixer):
        """
        수정기 추가
        
        Args:
            fixer: 추가할 수정기
        """
        self.fixers.append(fixer)
    
    def can_fix(self, document: PDFDocument, issues: List[QualityIssue]) -> bool:
        """
        수정 가능 여부 확인
        
        하나라도 수정 가능한 수정기가 있으면 True
        """
        return any(fixer.can_fix(document, issues) for fixer in self.fixers)
    
    def fix(self, context: FixContext) -> FixResult:
        """
        모든 수정기를 순차적으로 실행
        
        Args:
            context: 수정 컨텍스트
            
        Returns:
            FixResult: 종합 수정 결과
        """
        result = FixResult(
            success=True,
            message="복합 수정 완료"
        )
        
        # 임시 파일 경로들
        temp_files = []
        current_input = context.input_path
        
        try:
            # 각 수정기 순차 실행
            for i, fixer in enumerate(self.fixers):
                # 임시 출력 파일 생성
                if i < len(self.fixers) - 1:
                    # 마지막이 아니면 임시 파일로
                    temp_output = Path(tempfile.mktemp(suffix='.pdf'))
                    temp_files.append(temp_output)
                else:
                    # 마지막은 최종 출력 파일로
                    temp_output = context.output_path
                
                # 수정 컨텍스트 생성
                fix_context = FixContext(
                    input_path=current_input,
                    output_path=temp_output,
                    create_backup=False,  # 중간 단계는 백업 불필요
                    overwrite=True,
                    dry_run=context.dry_run,
                    options=context.options
                )
                
                # 수정 실행
                fix_result = fixer.fix(fix_context)
                
                if fix_result.success:
                    result.add_fix(fixer.name)
                    current_input = temp_output
                    self.logger.info(f"{fixer.name} 수정 완료")
                else:
                    self.logger.warning(f"{fixer.name} 수정 실패: {fix_result.error}")
                    # 실패해도 계속 진행
            
            result.output_path = context.output_path
            
        finally:
            # 임시 파일 정리
            for temp_file in temp_files:
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
        
        return result