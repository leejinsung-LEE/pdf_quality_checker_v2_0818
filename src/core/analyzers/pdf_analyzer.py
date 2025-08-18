# src/core/analyzers/pdf_analyzer.py
"""
PDF 통합 분석기

여러 개별 분석기를 조합하여 PDF 파일을 종합적으로 분석합니다.
"""

from typing import Union, Optional, Dict, Any
from pathlib import Path
import time
import logging

from ..models import PDFDocument, AnalysisResult, ColorInfo
from .base_analyzer import BaseAnalyzer, AnalysisError
from .pdf_resource_manager import PDFResourceManager
from .metadata_analyzer import MetadataAnalyzer
from .page_analyzer import PageAnalyzer
from .font_analyzer import FontAnalyzer
from .color_analyzer import ColorAnalyzer
from .image_analyzer import ImageAnalyzer


class PDFAnalyzer(BaseAnalyzer):
    """
    PDF 통합 분석기
    
    모든 개별 분석기를 조합하여 PDF를 종합적으로 분석합니다.
    """
    
    def __init__(self):
        """분석기 초기화"""
        super().__init__(name="PDFAnalyzer")
        self.logger = logging.getLogger(__name__)
        
        # 개별 분석기 초기화
        self.analyzers = {
            'metadata': MetadataAnalyzer(),
            'page': PageAnalyzer(),
            'font': FontAnalyzer(),
            'color': ColorAnalyzer(),
            'image': ImageAnalyzer()
        }
    
    def can_analyze(self, document) -> bool:
        """
        PDF 문서 분석 가능 여부 확인
        
        Args:
            document: PDF 문서 객체
            
        Returns:
            bool: 분석 가능 여부
        """
        return hasattr(document, 'pages') or hasattr(document, 'get_pages')
    
    def analyze(self, pdf_path: Union[str, Path], 
                options: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        PDF 파일 종합 분석
        
        Args:
            pdf_path: PDF 파일 경로
            options: 분석 옵션
                - skip_metadata: 메타데이터 분석 건너뛰기
                - skip_pages: 페이지 분석 건너뛰기
                - skip_fonts: 폰트 분석 건너뛰기
                - skip_colors: 색상 분석 건너뛰기
                - skip_images: 이미지 분석 건너뛰기
                - quick_mode: 빠른 분석 모드 (기본 검사만)
                
        Returns:
            AnalysisResult: 분석 결과
            
        Raises:
            AnalysisError: 분석 실패시
        """
        start_time = time.time()
        options = options or {}
        
        # 경로 정규화
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise AnalysisError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise AnalysisError(f"PDF 파일이 아닙니다: {pdf_path}")
        
        try:
            # PDF 리소스 관리자 사용하여 안전하게 열고 닫기
            with PDFResourceManager(pdf_path) as document:
                # 분석 결과 객체 생성 (기본값으로 초기화)
                result = AnalysisResult(
                    document=document,
                    pages=[],  # 페이지 정보는 분석 중 채워짐
                    fonts={},  # 폰트 정보는 분석 중 채워짐
                    colors=ColorInfo(),  # 기본 색상 정보
                    images=[]  # 이미지 정보는 분석 중 채워짐
                )
                
                # 빠른 모드 설정
                if options.get('quick_mode'):
                    analyze_options = {
                        'skip_metadata': False,
                        'skip_pages': False,
                        'skip_fonts': True,
                        'skip_colors': True,
                        'skip_images': True
                    }
                    options.update(analyze_options)
                
                # 각 분석기 실행
                analysis_steps = [
                    ('metadata', '메타데이터'),
                    ('page', '페이지'),
                    ('font', '폰트'),
                    ('color', '색상'),
                    ('image', '이미지')
                ]
                
                for analyzer_key, analyzer_name in analysis_steps:
                    if options.get(f'skip_{analyzer_key}s' if analyzer_key != 'metadata' else f'skip_{analyzer_key}'):
                        self.logger.info(f"{analyzer_name} 분석 건너뜀")
                        continue
                    
                    try:
                        self.logger.info(f"{analyzer_name} 분석 시작")
                        analyzer = self.analyzers[analyzer_key]
                        
                        # 각 분석기가 analyze_result 메서드를 가지고 있는지 확인
                        if hasattr(analyzer, 'analyze_result'):
                            analyzer.analyze_result(result)
                        else:
                            # analyze_result가 없으면 기본 analyze 메서드 사용
                            if hasattr(analyzer, 'analyze'):
                                analyzer.analyze(document, pdf_path)
                        
                        self.logger.info(f"{analyzer_name} 분석 완료")
                        
                    except Exception as e:
                        self.logger.error(f"{analyzer_name} 분석 실패: {e}")
                        # 개별 분석 실패는 전체 분석을 중단시키지 않음
                        # add_analysis_error가 없으면 issues에 직접 추가
                        if hasattr(result, 'add_analysis_error'):
                            result.add_analysis_error(analyzer_key, str(e))
                        else:
                            from ..models import QualityIssue, IssueSeverity, IssueCategory
                            error_issue = QualityIssue(
                                category=IssueCategory.GENERAL,
                                severity=IssueSeverity.WARNING,
                                title=f"{analyzer_name} 분석 실패",
                                description=str(e),
                                pages=[]
                            )
                            result.issues.append(error_issue)
                
                # 분석 시간 기록
                result.analysis_duration = time.time() - start_time
                
                # 분석 완료 상태 설정 (메서드가 있는 경우만)
                if hasattr(result, 'mark_complete'):
                    result.mark_complete()
                
                return result
                
        except Exception as e:
            self.logger.error(f"PDF 분석 실패: {e}")
            raise AnalysisError(f"PDF 분석 실패: {e}") from e
    
    def analyze_file(self, pdf_path: Union[str, Path]) -> AnalysisResult:
        """
        PDF 파일 분석 (기본 옵션)
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            AnalysisResult: 분석 결과
        """
        return self.analyze(pdf_path)
    
    def quick_analyze(self, pdf_path: Union[str, Path]) -> AnalysisResult:
        """
        PDF 파일 빠른 분석 (기본 검사만)
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            AnalysisResult: 분석 결과
        """
        return self.analyze(pdf_path, {'quick_mode': True})
    
    def analyze_specific(self, pdf_path: Union[str, Path],
                        analyzers: list) -> AnalysisResult:
        """
        특정 분석기만 사용하여 분석
        
        Args:
            pdf_path: PDF 파일 경로
            analyzers: 사용할 분석기 목록 ['metadata', 'page', 'font', 'color', 'image']
            
        Returns:
            AnalysisResult: 분석 결과
        """
        # 모든 분석기를 건너뛰기로 설정
        options = {
            'skip_metadata': True,
            'skip_pages': True,
            'skip_fonts': True,
            'skip_colors': True,
            'skip_images': True
        }
        
        # 선택된 분석기만 활성화
        for analyzer in analyzers:
            if analyzer == 'metadata':
                options['skip_metadata'] = False
            elif analyzer == 'page':
                options['skip_pages'] = False
            elif analyzer == 'font':
                options['skip_fonts'] = False
            elif analyzer == 'color':
                options['skip_colors'] = False
            elif analyzer == 'image':
                options['skip_images'] = False
        
        return self.analyze(pdf_path, options)