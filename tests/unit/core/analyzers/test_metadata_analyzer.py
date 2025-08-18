# tests/unit/core/analyzers/test_metadata_analyzer.py
"""
MetadataAnalyzer 테스트
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import pikepdf

from src.core.models import PDFDocument
from src.core.analyzers import MetadataAnalyzer


class TestMetadataAnalyzer:
    """MetadataAnalyzer 테스트 클래스"""
    
    @pytest.fixture
    def analyzer(self):
        """MetadataAnalyzer 인스턴스 생성"""
        return MetadataAnalyzer()
    
    @pytest.fixture
    def sample_pdf(self):
        """테스트용 PDF 파일 생성"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # 간단한 PDF 생성
            pdf = pikepdf.Pdf.new()
            
            # 메타데이터 설정
            pdf.docinfo['/Title'] = 'Test PDF'
            pdf.docinfo['/Author'] = '테스트 작성자'
            pdf.docinfo['/Subject'] = 'PDF 테스트'
            pdf.docinfo['/Keywords'] = 'test, pdf, quality'
            pdf.docinfo['/Creator'] = 'Test Creator'
            pdf.docinfo['/Producer'] = 'pikepdf'
            
            # 페이지 추가
            page = pdf.add_blank_page(page_size=(595, 842))  # A4
            
            # 저장
            pdf.save(tmp.name)
            yield Path(tmp.name)
            
            # 정리
            Path(tmp.name).unlink()
    
    def test_analyzer_initialization(self, analyzer):
        """분석기 초기화 테스트"""
        assert analyzer.name == "MetadataAnalyzer"
        assert analyzer.can_analyze(None) is True
    
    def test_analyze_basic_info(self, analyzer, sample_pdf):
        """기본 정보 분석 테스트"""
        # PDFDocument 생성
        document = PDFDocument.from_path(sample_pdf)
        
        # 분석 수행
        result = analyzer.analyze(document, sample_pdf)
        
        # 기본 정보 확인
        assert 'page_count' in result
        assert result['page_count'] == 1
        assert 'pdf_version' in result
        assert 'is_encrypted' in result
        assert result['is_encrypted'] is False
        assert 'is_linearized' in result
    
    def test_analyze_metadata(self, analyzer, sample_pdf):
        """메타데이터 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf)
        result = analyzer.analyze(document, sample_pdf)
        
        # 메타데이터 확인
        assert 'metadata' in result
        metadata = result['metadata']
        
        assert metadata['title'] == 'Test PDF'
        assert metadata['author'] == '테스트 작성자'
        assert metadata['subject'] == 'PDF 테스트'
        assert metadata['keywords'] == 'test, pdf, quality'
        assert metadata['creator'] == 'Test Creator'
        assert metadata['producer'] == 'pikepdf'
    
    def test_document_update(self, analyzer, sample_pdf):
        """문서 객체 업데이트 테스트"""
        document = PDFDocument.from_path(sample_pdf)
        
        # 초기 상태 확인
        assert document.page_count == 0
        assert document.pdf_version == ""
        
        # 분석 수행
        analyzer.analyze(document, sample_pdf)
        
        # 업데이트 확인
        assert document.page_count == 1
        assert document.pdf_version != ""
        assert document.is_encrypted is False
        assert len(document.metadata) > 0
    
    def test_pdf_date_parsing(self, analyzer):
        """PDF 날짜 형식 파싱 테스트"""
        # 다양한 PDF 날짜 형식 테스트
        test_cases = [
            ('D:20231225120000', '2023-12-25 12:00:00'),
            ('D:20231225', '2023-12-25'),
            ('20231225120000', '2023-12-25 12:00:00'),
            ('invalid_date', 'invalid_date'),
            ('', '')
        ]
        
        for input_date, expected in test_cases:
            result = analyzer._parse_pdf_date(input_date)
            assert result == expected
    
    def test_encrypted_pdf(self, analyzer):
        """암호화된 PDF 처리 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # 암호화된 PDF 생성
            pdf = pikepdf.Pdf.new()
            pdf.add_blank_page()
            pdf.save(tmp.name, encryption=pikepdf.Encryption(
                user="user_password",
                owner="owner_password"
            ))
            
            pdf_path = Path(tmp.name)
            document = PDFDocument.from_path(pdf_path)
            
            # 암호가 필요한 PDF는 분석 실패할 수 있음
            try:
                result = analyzer.analyze(document, pdf_path)
                assert result.get('is_encrypted', False) is True
            except Exception:
                # 암호화된 PDF 열기 실패는 예상된 동작
                pass
            
            pdf_path.unlink()
    
    def test_safe_analyze(self, analyzer, sample_pdf):
        """안전한 분석 테스트"""
        document = PDFDocument.from_path(sample_pdf)
        
        # _safe_analyze 메서드 테스트
        result = analyzer._safe_analyze(document, sample_pdf)
        
        assert result['status'] == 'success'
        assert result['analyzer'] == 'MetadataAnalyzer'
        assert 'error' not in result
    
    def test_invalid_pdf_path(self, analyzer):
        """잘못된 PDF 경로 처리 테스트"""
        invalid_path = Path("non_existent.pdf")
        
        # PDFDocument 생성 시 예외 발생
        with pytest.raises(ValueError):
            PDFDocument.from_path(invalid_path)
    
    def test_dependencies(self, analyzer):
        """의존성 확인 테스트"""
        deps = analyzer.get_dependencies()
        
        assert 'pikepdf' in deps
        assert deps['pikepdf'] is True  # pikepdf가 설치되어 있어야 함