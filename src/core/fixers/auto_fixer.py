# src/core/fixers/auto_fixer.py
"""
자동 수정 통합 모듈

품질 검사 결과에 따라 자동으로 적절한 수정을 수행합니다.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
import tempfile
import shutil
from datetime import datetime

from .base_fixer import BaseFixer, FixResult, FixContext, CompositeFixer
from .color_fixer import ColorFixer
from .font_fixer import FontFixer
from .image_fixer import ImageFixer
from ..models import PDFDocument, QualityIssue
from ..analyzers import PDFAnalyzer
from ..quality_checker import PDFQualityChecker


class AutoFixer:
    """
    자동 수정 관리자
    
    PDF 파일을 분석하고 발견된 문제를 자동으로 수정합니다.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        자동 수정기 초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 분석기와 검사기
        self.analyzer = PDFAnalyzer()
        self.checker = PDFQualityChecker()
        
        # 개별 수정기
        self.color_fixer = ColorFixer()
        self.font_fixer = FontFixer()
        self.image_fixer = ImageFixer()
        
        # 수정 우선순위 (순서대로 적용)
        self.fix_order = [
            ('color', self.color_fixer),
            ('font', self.font_fixer),
            ('image', self.image_fixer)
        ]
    
    def auto_fix(self,
                input_path: Path,
                output_path: Optional[Path] = None,
                profile: str = 'default',
                options: Optional[Dict[str, Any]] = None) -> FixResult:
        """
        PDF 자동 수정 실행
        
        Args:
            input_path: 입력 PDF 경로
            output_path: 출력 PDF 경로 (없으면 자동 생성)
            profile: 품질 검사 프로파일
            options: 수정 옵션
            
        Returns:
            FixResult: 수정 결과
        """
        start_time = datetime.now()
        
        # 기본 옵션
        if options is None:
            options = {}
        
        # 출력 경로 설정
        if output_path is None:
            stem = input_path.stem
            suffix = input_path.suffix
            output_path = input_path.parent / f"{stem}_fixed{suffix}"
        
        try:
            # 1. PDF 분석
            self.logger.info(f"PDF 분석 시작: {input_path}")
            analysis_result = self.analyzer.analyze(input_path)
            
            if not analysis_result.success:
                return FixResult(
                    success=False,
                    message="PDF 분석 실패",
                    error=f"분석 오류: {', '.join(str(e) for e in analysis_result.issues)}"
                )
            
            # 2. 품질 검사
            self.logger.info(f"품질 검사 시작 (프로파일: {profile})")
            quality_result = self.checker.check(analysis_result.document, profile)
            
            # 문제가 없으면 수정 불필요
            if quality_result.passed and not quality_result.issues:
                self.logger.info("품질 문제가 없습니다. 수정이 필요하지 않습니다.")
                return FixResult(
                    success=True,
                    message="수정이 필요하지 않습니다 (품질 검사 통과)",
                    output_path=input_path
                )
            
            # 3. 수정 계획 수립
            fix_plan = self._create_fix_plan(
                analysis_result.document,
                quality_result.issues,
                options
            )
            
            if not fix_plan:
                return FixResult(
                    success=False,
                    message="수정 가능한 문제가 없습니다",
                    error="No fixable issues found"
                )
            
            self.logger.info(f"수정 계획: {', '.join(fix_plan.keys())}")
            
            # 4. 수정 실행
            result = self._execute_fixes(
                input_path,
                output_path,
                fix_plan,
                options
            )
            
            # 처리 시간 계산
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            # 5. 수정 후 검증 (옵션)
            if result.success and options.get('verify_after_fix', True):
                self.logger.info("수정 후 품질 재검사")
                verification = self._verify_fixed_file(result.output_path, profile)
                
                if verification['passed']:
                    result.message += f" (검증 완료: {verification['score']:.1f}점)"
                else:
                    result.message += f" (검증 실패: {len(verification['remaining_issues'])}개 문제 남음)"
            
            return result
            
        except Exception as e:
            self.logger.error(f"자동 수정 중 오류: {e}")
            return FixResult(
                success=False,
                message="자동 수정 실패",
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _create_fix_plan(self,
                        document: PDFDocument,
                        issues: List[QualityIssue],
                        options: Dict[str, Any]) -> Dict[str, BaseFixer]:
        """
        수정 계획 수립
        
        Args:
            document: PDF 문서
            issues: 품질 문제 목록
            options: 수정 옵션
            
        Returns:
            Dict[str, BaseFixer]: 수정할 카테고리와 수정기 맵
        """
        fix_plan = {}
        
        # 각 수정기별로 수정 가능 여부 확인
        for category, fixer in self.fix_order:
            # 해당 카테고리 수정이 비활성화되어 있으면 건너뛰기
            if options.get(f'skip_{category}_fix', False):
                continue
            
            # 수정 가능한지 확인
            if fixer.can_fix(document, issues):
                fix_plan[category] = fixer
                self.logger.debug(f"{category} 수정 가능")
        
        return fix_plan
    
    def _execute_fixes(self,
                      input_path: Path,
                      output_path: Path,
                      fix_plan: Dict[str, BaseFixer],
                      options: Dict[str, Any]) -> FixResult:
        """
        수정 계획 실행
        
        Args:
            input_path: 입력 PDF 경로
            output_path: 최종 출력 경로
            fix_plan: 수정 계획
            options: 수정 옵션
            
        Returns:
            FixResult: 수정 결과
        """
        if not fix_plan:
            return FixResult(
                success=False,
                message="수정할 항목이 없습니다"
            )
        
        # 단일 수정기만 있는 경우
        if len(fix_plan) == 1:
            category, fixer = list(fix_plan.items())[0]
            context = FixContext(
                input_path=input_path,
                output_path=output_path,
                create_backup=options.get('create_backup', True),
                overwrite=options.get('overwrite', False),
                options=options.get(f'{category}_options', {})
            )
            
            self.logger.info(f"{category} 수정 실행")
            return fixer.safe_fix(context)
        
        # 여러 수정기가 있는 경우 - 순차 실행
        temp_files = []
        current_input = input_path
        all_fixes = []
        
        try:
            for i, (category, fixer) in enumerate(fix_plan.items()):
                # 마지막 수정인지 확인
                is_last = (i == len(fix_plan) - 1)
                
                # 출력 경로 설정
                if is_last:
                    temp_output = output_path
                else:
                    temp_output = Path(tempfile.mktemp(suffix='.pdf'))
                    temp_files.append(temp_output)
                
                # 수정 컨텍스트 생성
                context = FixContext(
                    input_path=current_input,
                    output_path=temp_output,
                    create_backup=(i == 0 and options.get('create_backup', True)),
                    overwrite=True,
                    options=options.get(f'{category}_options', {})
                )
                
                # 수정 실행
                self.logger.info(f"{category} 수정 실행 ({i+1}/{len(fix_plan)})")
                result = fixer.safe_fix(context)
                
                if not result.success:
                    # 수정 실패시 중단
                    self.logger.error(f"{category} 수정 실패: {result.error}")
                    
                    # 이전까지 성공한 수정만 반환
                    return FixResult(
                        success=False,
                        message=f"{category} 수정 실패",
                        error=result.error,
                        fixes_applied=all_fixes
                    )
                
                # 성공한 수정 기록
                all_fixes.extend(result.fixes_applied)
                current_input = temp_output
            
            # 모든 수정 성공
            return FixResult(
                success=True,
                message=f"{len(fix_plan)}개 카테고리 수정 완료",
                output_path=output_path,
                fixes_applied=all_fixes
            )
            
        finally:
            # 임시 파일 정리
            for temp_file in temp_files:
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
    
    def _verify_fixed_file(self, file_path: Path, profile: str) -> Dict[str, Any]:
        """
        수정된 파일 검증
        
        Args:
            file_path: 수정된 파일 경로
            profile: 품질 검사 프로파일
            
        Returns:
            Dict: 검증 결과
        """
        try:
            # 재분석
            analysis_result = self.analyzer.analyze(file_path)
            
            if not analysis_result.success:
                return {
                    'passed': False,
                    'score': 0,
                    'remaining_issues': [],
                    'error': '재분석 실패'
                }
            
            # 재검사
            quality_result = self.checker.check(analysis_result.document, profile)
            
            return {
                'passed': quality_result.passed,
                'score': quality_result.quality_score,
                'remaining_issues': quality_result.issues,
                'warnings': quality_result.warnings
            }
            
        except Exception as e:
            self.logger.error(f"검증 중 오류: {e}")
            return {
                'passed': False,
                'score': 0,
                'remaining_issues': [],
                'error': str(e)
            }
    
    def fix_specific_issues(self,
                           input_path: Path,
                           output_path: Optional[Path] = None,
                           fix_types: List[str] = None) -> FixResult:
        """
        특정 문제만 수정
        
        Args:
            input_path: 입력 PDF 경로
            output_path: 출력 PDF 경로
            fix_types: 수정할 문제 유형 리스트 ['color', 'font', 'image']
            
        Returns:
            FixResult: 수정 결과
        """
        if fix_types is None:
            fix_types = ['color', 'font', 'image']
        
        # 옵션 설정
        options = {}
        for category in ['color', 'font', 'image']:
            if category not in fix_types:
                options[f'skip_{category}_fix'] = True
        
        return self.auto_fix(input_path, output_path, options=options)