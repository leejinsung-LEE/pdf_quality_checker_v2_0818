# tests/integration/test_pdf_analysis.py
"""
PDF 분석 통합 테스트

여러 분석기가 함께 동작하는 통합 시나리오를 테스트합니다.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import pikepdf
import subprocess

# UTF-8 인코딩 설정
from _utf8_setup import setup_utf8_encoding

from src.core.models import PDFDocument, AnalysisResult
from src.core.analyzers import (
    MetadataAnalyzer, PageAnalyzer, FontAnalyzer,
    ColorAnalyzer, ImageAnalyzer
)
from src.external import get_tool_manager


class TestPDFAnalysisIntegration:
    """PDF 분석 통합 테스트"""
    
    @pytest.fixture
    def analyzers(self):
        """모든 분석기 인스턴스 생성"""
        tool_manager = get_tool_manager()
        return {
            'metadata': MetadataAnalyzer(),
            'page': PageAnalyzer(),
            'font': FontAnalyzer(tool_manager),
            'color': ColorAnalyzer(),
            'image': ImageAnalyzer()
        }
    
    @pytest.fixture
    def complex_pdf(self):
        """복잡한 테스트 PDF 생성"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf = pikepdf.Pdf.new()
            
            # 메타데이터 설정
            pdf.docinfo['/Title'] = '통합 테스트 PDF'
            pdf.docinfo['/Author'] = 'PDF Quality Checker'
            
            # 다양한 크기의 페이지 추가
            page1 = pdf.add_blank_page(page_size=(595, 842))  # A4
            page2 = pdf.add_blank_page(page_size=(842, 595))  # A4 가로
            
            # 페이지에 컨텐츠 추가 (색상 테스트용)
            # RGB 색상 사용
            content1 = pikepdf.Stream(pdf, b"""
                q
                1 0 0 rg  % RGB red
                100 100 100 100 re
                f
                Q
            """)
            page1.Contents = content1
            
            # CMYK 색상 사용
            content2 = pikepdf.Stream(pdf, b"""
                q
                0 1 1 0 k  % CMYK cyan
                200 200 100 100 re
                f
                Q
            """)
            page2.Contents = content2
            
            pdf.save(tmp.name)
            yield Path(tmp.name)
            Path(tmp.name).unlink()
    
    def test_full_analysis_workflow(self, analyzers, complex_pdf):
        """전체 분석 워크플로우 테스트"""
        # PDFDocument 생성
        document = PDFDocument.from_path(complex_pdf)
        
        # 각 분석기 실행
        results = {}
        
        # 메타데이터 분석
        metadata_result = analyzers['metadata'].analyze(document, complex_pdf)
        assert metadata_result['page_count'] == 2
        assert metadata_result['metadata']['title'] == '통합 테스트 PDF'
        results['metadata'] = metadata_result
        
        # 페이지 분석
        page_result = analyzers['page'].analyze(document, complex_pdf)
        assert page_result['total_pages'] == 2
        assert page_result['has_mixed_orientations'] is True
        results['pages'] = page_result
        
        # 폰트 분석
        font_result = analyzers['font'].analyze(document, complex_pdf)
        assert 'fonts' in font_result
        results['fonts'] = font_result
        
        # 색상 분석
        color_result = analyzers['color'].analyze(document, complex_pdf)
        assert 'color_info' in color_result
        assert len(color_result['color_spaces']) > 0
        results['colors'] = color_result
        
        # 이미지 분석
        image_result = analyzers['image'].analyze(document, complex_pdf)
        assert 'total_images' in image_result
        results['images'] = image_result
        
        # AnalysisResult 객체 생성 가능 여부 확인
        analysis_result = AnalysisResult(
            document=document,
            pages=document.pages,
            fonts=font_result.get('fonts', {}),
            colors=color_result.get('color_info'),
            images=image_result.get('images', [])
        )
        
        assert analysis_result.document == document
        assert analysis_result.total_fonts >= 0
        assert analysis_result.total_images >= 0
    
    def test_analyzer_independence(self, analyzers, complex_pdf):
        """분석기 독립성 테스트 - 하나가 실패해도 다른 것들은 동작"""
        document = PDFDocument.from_path(complex_pdf)
        
        # 존재하지 않는 PDF로 일부 분석기 실패 유도
        invalid_path = Path("non_existent.pdf")
        
        # 각 분석기의 _safe_analyze 메서드 테스트
        for name, analyzer in analyzers.items():
            if hasattr(analyzer, '_safe_analyze'):
                # 유효한 PDF로는 성공해야 함
                result = analyzer._safe_analyze(document, complex_pdf)
                assert result['status'] == 'success'
                
                # 유효하지 않은 경로로는 에러 처리
                # (document는 이미 생성되어 있으므로 분석 시도는 가능)
                error_result = analyzer._safe_analyze(document, invalid_path)
                assert error_result['status'] == 'error'
    
    def test_cli_integration(self, complex_pdf):
        """CLI 통합 테스트"""
        # main.py 실행
        result = subprocess.run(
            [sys.executable, 'main.py', str(complex_pdf)],
            capture_output=True,
            text=True
        )
        
        # 실행 성공 확인
        assert result.returncode == 0
        
        # 출력에 주요 정보 포함 확인
        output = result.stdout
        assert '📄 PDF 분석 시작' in output
        assert '📊 분석 결과' in output
        assert '페이지 수: 2' in output
    
    def test_json_report_generation(self, complex_pdf):
        """JSON 보고서 생성 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            # main.py로 JSON 보고서 생성
            result = subprocess.run(
                [sys.executable, 'main.py', str(complex_pdf), '-o', tmp.name],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0
            
            # JSON 파일 확인
            report_path = Path(tmp.name)
            assert report_path.exists()
            
            # JSON 내용 확인
            import json
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            assert 'document' in report
            assert 'summary' in report
            assert report['document']['page_count'] == 2
            
            report_path.unlink()
    
    def test_tool_manager_integration(self):
        """도구 관리자 통합 테스트"""
        tool_manager = get_tool_manager()
        
        # 상태 보고서 생성 가능
        status = tool_manager.get_status_report()
        assert isinstance(status, dict)
        
        # 기본 도구들 확인
        for tool in ['ghostscript', 'pdffonts']:
            assert tool in status
            assert 'available' in status[tool]
            assert 'path' in status[tool]
    
    @pytest.mark.parametrize("analyzer_class", [
        MetadataAnalyzer,
        PageAnalyzer,
        FontAnalyzer,
        ColorAnalyzer,
        ImageAnalyzer
    ])
    def test_analyzer_initialization(self, analyzer_class):
        """각 분석기 초기화 테스트"""
        analyzer = analyzer_class()
        
        # 기본 속성 확인
        assert hasattr(analyzer, 'name')
        assert hasattr(analyzer, 'analyze')
        assert hasattr(analyzer, 'can_analyze')
        
        # 초기화 가능
        assert analyzer.initialize() is True
        assert analyzer.is_ready() is True
        
        # 의존성 확인 가능
        deps = analyzer.get_dependencies()
        assert isinstance(deps, dict)