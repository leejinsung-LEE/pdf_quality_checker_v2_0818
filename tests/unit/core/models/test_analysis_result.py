"""
AnalysisResult 모델 단위 테스트

PDF 분석 결과를 저장하고 관리하는 AnalysisResult 모델과
관련 클래스들(FontInfo, ColorInfo, ImageInfo)의 동작을 검증합니다.

이 테스트는 다음과 같은 중요한 기능들을 확인합니다:
- 분석 데이터의 올바른 저장과 조회
- 품질 점수 계산의 정확성
- 이슈 필터링 기능의 동작
- 통계 정보의 자동 계산
"""

import pytest
from datetime import datetime
from pathlib import Path

# 테스트할 모듈들을 임포트
from src.core.models.pdf_document import PDFDocument, PageInfo
from src.core.models.analysis_result import (
    AnalysisResult, FontInfo, ColorInfo, ImageInfo,
    ColorSpace, FontType, ImpositionReadiness
)
from src.core.models.quality_issue import QualityIssue, IssueSeverity, IssueCategory


class TestFontInfo:
    """FontInfo 클래스 테스트
    
    폰트 정보를 관리하는 FontInfo 클래스가 올바르게 동작하는지 확인합니다.
    폰트의 임베딩 상태, 타입, 사용 페이지 등을 정확히 추적하는지 검증합니다.
    """
    
    def test_font_info_creation(self):
        """FontInfo 객체 생성 및 기본 속성 테스트"""
        font = FontInfo(
            name="Arial",
            type=FontType.TRUETYPE,
            is_embedded=True,
            is_subset=True,
            encoding="WinAnsiEncoding",
            pages_used=[1, 2, 3]
        )
        
        # 기본 속성 확인
        assert font.name == "Arial"
        assert font.type == FontType.TRUETYPE
        assert font.is_embedded is True
        assert font.is_subset is True
        assert font.encoding == "WinAnsiEncoding"
        assert font.pages_used == [1, 2, 3]
        assert font.page_count == 3  # 중복 제거된 페이지 수
    
    def test_font_type_checks(self):
        """폰트 타입별 체크 메서드 테스트
        
        Type3 폰트와 CID 폰트는 특별한 처리가 필요하므로
        이를 구분하는 메서드가 올바르게 동작하는지 확인합니다.
        """
        # Type3 폰트 테스트
        type3_font = FontInfo("CustomFont", FontType.TYPE3, False, False, "Custom")
        assert type3_font.is_type3 is True
        assert type3_font.is_cid_font is False
        
        # CID 폰트 테스트 (한글, 중국어, 일본어 등에 사용)
        cid_font = FontInfo("NotoSansCJK", FontType.TYPE0, True, True, "Identity-H")
        assert cid_font.is_type3 is False
        assert cid_font.is_cid_font is True
        
        # CID 서브타입들도 확인
        for cid_type in [FontType.CID_TYPE0, FontType.CID_TYPE2]:
            font = FontInfo("TestFont", cid_type, True, True, "Identity-H")
            assert font.is_cid_font is True
    
    def test_font_embedding_requirements(self):
        """폰트 임베딩 필요성 판단 테스트
        
        PDF 표준 14개 폰트(Times, Helvetica 등)는 임베딩이 필요 없지만,
        그 외의 폰트는 임베딩이 필요합니다.
        """
        # 임베딩이 필요한 경우: 임베딩되지 않았고 표준 폰트가 아닌 경우
        custom_font = FontInfo("CustomFont", FontType.TRUETYPE, False, False, "Custom")
        custom_font.is_standard_14 = False
        assert custom_font.needs_embedding is True
        
        # 이미 임베딩된 경우
        embedded_font = FontInfo("EmbeddedFont", FontType.TRUETYPE, True, True, "Custom")
        assert embedded_font.needs_embedding is False
        
        # 표준 14개 폰트인 경우 (Times-Roman, Helvetica 등)
        standard_font = FontInfo("Times-Roman", FontType.TYPE1, False, False, "StandardEncoding")
        standard_font.is_standard_14 = True
        assert standard_font.needs_embedding is False
    
    def test_font_string_representation(self):
        """폰트 정보의 문자열 표현 테스트"""
        # 임베딩된 서브셋 폰트
        subset_font = FontInfo("Arial", FontType.TRUETYPE, True, True, "WinAnsiEncoding")
        font_str = str(subset_font)
        assert "Arial (subset)" in font_str
        assert "TrueType" in font_str
        assert "embedded" in font_str
        
        # 임베딩되지 않은 전체 폰트
        full_font = FontInfo("Helvetica", FontType.TYPE1, False, False, "StandardEncoding")
        font_str = str(full_font)
        assert "(subset)" not in font_str
        assert "not embedded" in font_str


class TestColorInfo:
    """ColorInfo 클래스 테스트
    
    PDF 문서의 색상 정보를 관리하는 ColorInfo 클래스를 테스트합니다.
    인쇄 품질에 중요한 색상 공간, 별색, 잉크량 등을 확인합니다.
    """
    
    def test_color_info_creation(self):
        """ColorInfo 객체 생성 및 기본 속성 테스트"""
        color_info = ColorInfo()
        
        # 색상 공간 추가
        color_info.color_spaces_used.add(ColorSpace.CMYK)
        color_info.color_spaces_used.add(ColorSpace.RGB)
        
        # 별색 추가
        color_info.spot_colors = ["PANTONE 186 C", "PANTONE 285 C"]
        
        # 속성 설정
        color_info.has_transparency = True
        color_info.has_overprint = False
        color_info.max_ink_coverage = 280.0
        
        # 확인
        assert ColorSpace.CMYK in color_info.color_spaces_used
        assert ColorSpace.RGB in color_info.color_spaces_used
        assert len(color_info.spot_colors) == 2
        assert color_info.has_transparency is True
    
    def test_color_space_checks(self):
        """색상 공간 사용 여부 확인 메서드 테스트"""
        color_info = ColorInfo()
        
        # 초기 상태 - 아무 색상도 사용하지 않음
        assert color_info.uses_rgb is False
        assert color_info.uses_cmyk is False
        assert color_info.uses_spot_colors is False
        
        # RGB 추가
        color_info.color_spaces_used.add(ColorSpace.RGB)
        assert color_info.uses_rgb is True
        
        # CMYK 추가
        color_info.color_spaces_used.add(ColorSpace.CMYK)
        assert color_info.uses_cmyk is True
        
        # 별색 추가
        color_info.spot_colors.append("PANTONE 186 C")
        assert color_info.uses_spot_colors is True
    
    def test_print_readiness(self):
        """인쇄 준비 상태 확인 테스트
        
        인쇄용 PDF는 다음 조건을 만족해야 합니다:
        1. CMYK 색상만 사용
        2. RGB 색상 사용하지 않음
        3. 총 잉크량이 320% 이하
        """
        color_info = ColorInfo()
        
        # 인쇄 준비 완료 상태
        color_info.color_spaces_used.add(ColorSpace.CMYK)
        color_info.max_ink_coverage = 300.0
        assert color_info.is_print_ready is True
        
        # RGB가 포함된 경우 - 인쇄 준비 안됨
        color_info.color_spaces_used.add(ColorSpace.RGB)
        assert color_info.is_print_ready is False
        
        # RGB 제거하고 잉크량 초과 - 인쇄 준비 안됨
        color_info.color_spaces_used.remove(ColorSpace.RGB)
        color_info.max_ink_coverage = 350.0
        assert color_info.is_print_ready is False
    
    def test_color_mode_summary(self):
        """색상 모드 요약 문자열 테스트"""
        color_info = ColorInfo()
        
        # 빈 상태
        assert color_info.color_mode_summary == "Unknown"
        
        # CMYK만
        color_info.color_spaces_used.add(ColorSpace.CMYK)
        assert color_info.color_mode_summary == "CMYK"
        
        # CMYK + RGB
        color_info.color_spaces_used.add(ColorSpace.RGB)
        assert "CMYK" in color_info.color_mode_summary
        assert "RGB" in color_info.color_mode_summary
        
        # 별색 추가
        color_info.spot_colors = ["PANTONE 186 C", "PANTONE 285 C"]
        summary = color_info.color_mode_summary
        assert "Spot(2)" in summary


class TestImageInfo:
    """ImageInfo 클래스 테스트
    
    PDF 내 이미지 정보를 관리하는 ImageInfo 클래스를 테스트합니다.
    해상도, 크기, 압축 등 인쇄 품질에 영향을 주는 요소들을 확인합니다.
    """
    
    def test_image_info_creation(self):
        """ImageInfo 객체 생성 테스트"""
        image = ImageInfo(
            page=1,
            width=1200,
            height=800,
            color_space=ColorSpace.RGB,
            bits_per_component=8,
            filter="DCTDecode"  # JPEG 압축
        )
        
        # 추가 정보 설정
        image.dpi_x = 300.0
        image.dpi_y = 300.0
        image.display_width = 101.6  # 4인치 = 101.6mm
        image.display_height = 67.7   # 2.67인치 = 67.7mm
        
        assert image.page == 1
        assert image.width == 1200
        assert image.height == 800
        assert image.pixel_count == 960000
        assert image.aspect_ratio == 1.5
    
    def test_resolution_checks(self):
        """이미지 해상도 확인 테스트
        
        인쇄용 이미지는 최소 300dpi를 권장합니다:
        - 300dpi 이상: 고품질
        - 150-300dpi: 경고
        - 150dpi 미만: 심각한 품질 문제
        """
        # 고해상도 이미지 (인쇄 품질 우수)
        high_res = ImageInfo(1, 3000, 2000, ColorSpace.CMYK, 8, "FlateDecode")
        high_res.dpi_x = 350.0
        high_res.dpi_y = 350.0
        assert high_res.effective_dpi == 350.0
        assert high_res.is_low_resolution is False
        assert high_res.is_very_low_resolution is False
        
        # 중간 해상도 이미지 (경고 수준)
        mid_res = ImageInfo(1, 1500, 1000, ColorSpace.RGB, 8, "DCTDecode")
        mid_res.dpi_x = 200.0
        mid_res.dpi_y = 200.0
        assert mid_res.effective_dpi == 200.0
        assert mid_res.is_low_resolution is True
        assert mid_res.is_very_low_resolution is False
        
        # 저해상도 이미지 (심각한 문제)
        low_res = ImageInfo(1, 600, 400, ColorSpace.RGB, 8, "DCTDecode")
        low_res.dpi_x = 72.0
        low_res.dpi_y = 72.0
        assert low_res.effective_dpi == 72.0
        assert low_res.is_low_resolution is True
        assert low_res.is_very_low_resolution is True
    
    def test_effective_dpi_calculation(self):
        """유효 DPI 계산 테스트
        
        이미지가 비균등하게 스케일된 경우 x, y DPI가 다를 수 있습니다.
        이 경우 더 낮은 값을 기준으로 품질을 판단합니다.
        """
        image = ImageInfo(1, 1000, 1000, ColorSpace.RGB, 8, "FlateDecode")
        
        # x, y DPI가 다른 경우
        image.dpi_x = 300.0
        image.dpi_y = 150.0
        assert image.effective_dpi == 150.0  # 더 낮은 값
        
        # DPI가 0인 경우 처리
        image.dpi_x = 0.0
        image.dpi_y = 300.0
        assert image.effective_dpi == 300.0  # 0이 아닌 값 사용


class TestAnalysisResult:
    """AnalysisResult 클래스 테스트
    
    전체 PDF 분석 결과를 종합하는 AnalysisResult 클래스를 테스트합니다.
    이 클래스는 모든 분석 데이터를 모아서 품질 점수를 계산하고
    이슈를 관리하는 중심 역할을 합니다.
    """
    
    @pytest.fixture
    def sample_document(self):
        """테스트용 PDF 문서 객체 생성"""
        # 임시 경로 사용 (실제 파일은 필요 없음)
        doc = PDFDocument(
            path=Path("/tmp/test.pdf"),
            file_hash="dummy_hash",
            file_size=1024000,
            created_at=datetime.now()
        )
        doc.page_count = 10
        doc.pdf_version = "1.7"
        return doc
    
    @pytest.fixture
    def sample_analysis_result(self, sample_document):
        """테스트용 분석 결과 객체 생성"""
        # 페이지 정보
        pages = [PageInfo(i, 210.0, 297.0) for i in range(1, 11)]
        
        # 폰트 정보
        fonts = {
            "Arial": FontInfo("Arial", FontType.TRUETYPE, True, True, "WinAnsiEncoding"),
            "TimesNewRoman": FontInfo("TimesNewRoman", FontType.TRUETYPE, False, False, "WinAnsiEncoding"),
        }
        
        # 색상 정보
        colors = ColorInfo()
        colors.color_spaces_used.add(ColorSpace.CMYK)
        colors.max_ink_coverage = 280.0
        
        # 이미지 정보
        images = [
            ImageInfo(1, 1200, 800, ColorSpace.RGB, 8, "DCTDecode"),
            ImageInfo(2, 600, 400, ColorSpace.RGB, 8, "DCTDecode"),
        ]
        images[0].dpi_x = images[0].dpi_y = 300.0
        images[1].dpi_x = images[1].dpi_y = 72.0  # 저해상도
        
        return AnalysisResult(
            document=sample_document,
            pages=pages,
            fonts=fonts,
            colors=colors,
            images=images
        )
    
    def test_analysis_result_creation(self, sample_analysis_result):
        """AnalysisResult 객체 생성 및 자동 통계 계산 테스트"""
        result = sample_analysis_result
        
        # 기본 속성 확인
        assert result.document.page_count == 10
        assert len(result.pages) == 10
        assert len(result.fonts) == 2
        assert len(result.images) == 2
        
        # 자동 계산된 통계 확인
        assert result.total_fonts == 2
        assert result.embedded_fonts == 1  # Arial만 임베딩됨
        assert result.total_images == 2
        assert result.low_res_images == 1  # 두 번째 이미지가 저해상도
        
        # 비율 계산
        assert result.font_embedding_rate == 50.0  # 2개 중 1개 임베딩
    
    def test_quality_score_calculation(self, sample_analysis_result):
        """품질 점수 계산 테스트
        
        품질 점수는 100점에서 시작하여 이슈의 심각도에 따라 감점됩니다:
        - 오류(error): -10점
        - 경고(warning): -3점
        - 정보(info): -1점
        """
        result = sample_analysis_result
        
        # 이슈가 없을 때는 100점
        assert result.quality_score == 100.0
        
        # 오류 추가
        error_issue = QualityIssue(
            category=IssueCategory.FONT_EMBEDDING,
            severity=IssueSeverity.ERROR,
            title="폰트 미임베딩",
            description="폰트가 임베딩되지 않았습니다"
        )
        result.add_issue(error_issue)
        assert result.quality_score == 90.0  # 100 - 10
        
        # 경고 추가
        warning_issue = QualityIssue(
            category=IssueCategory.IMAGE_RESOLUTION,
            severity=IssueSeverity.WARNING,
            title="저해상도 이미지",
            description="이미지 해상도가 낮습니다"
        )
        result.add_issue(warning_issue)
        assert result.quality_score == 87.0  # 90 - 3
        
        # 정보 추가
        info_issue = QualityIssue(
            category=IssueCategory.METADATA,
            severity=IssueSeverity.INFO,
            title="메타데이터 누락",
            description="PDF 제목이 설정되지 않았습니다"
        )
        result.add_issue(info_issue)
        assert result.quality_score == 86.0  # 87 - 1
        
        # 점수는 0 이하로 내려가지 않음
        for _ in range(20):
            result.add_issue(error_issue)
        assert result.quality_score == 0.0
    
    def test_issue_filtering(self, sample_analysis_result):
        """이슈 필터링 기능 테스트
        
        카테고리, 심각도, 페이지별로 이슈를 필터링하는 기능을 테스트합니다.
        이는 사용자가 특정 유형의 문제만 보고 싶을 때 유용합니다.
        """
        result = sample_analysis_result
        
        # 다양한 이슈 추가
        issues = [
            QualityIssue(IssueCategory.FONT_EMBEDDING, IssueSeverity.ERROR, 
                        "폰트 문제 1", "설명", pages=[1, 2]),
            QualityIssue(IssueCategory.FONT_EMBEDDING, IssueSeverity.WARNING, 
                        "폰트 문제 2", "설명", pages=[3]),
            QualityIssue(IssueCategory.IMAGE_RESOLUTION, IssueSeverity.ERROR, 
                        "이미지 문제", "설명", pages=[1]),
            QualityIssue(IssueCategory.COLOR_SPACE, IssueSeverity.INFO, 
                        "색상 정보", "설명", pages=[]),  # 전체 문서
        ]
        
        for issue in issues:
            result.add_issue(issue)
        
        # 카테고리별 필터링
        font_issues = result.get_issues_by_category("font_embedding")
        assert len(font_issues) == 2
        
        # 심각도별 필터링
        error_issues = result.get_issues_by_severity("error")
        assert len(error_issues) == 2
        
        # 페이지별 필터링
        page1_issues = result.get_issues_by_page(1)
        assert len(page1_issues) == 2  # 폰트 문제 1, 이미지 문제
        
        page3_issues = result.get_issues_by_page(3)
        assert len(page3_issues) == 1  # 폰트 문제 2만
    
    def test_issue_status_properties(self, sample_analysis_result):
        """이슈 상태 확인 속성 테스트"""
        result = sample_analysis_result
        
        # 초기 상태 - 이슈 없음
        assert result.has_errors is False
        assert result.has_warnings is False
        assert result.error_count == 0
        assert result.warning_count == 0
        assert result.info_count == 0
        
        # 이슈 추가
        result.add_issue(QualityIssue(
            IssueCategory.FONT_EMBEDDING, IssueSeverity.ERROR, "오류", "설명"
        ))
        result.add_issue(QualityIssue(
            IssueCategory.IMAGE_RESOLUTION, IssueSeverity.WARNING, "경고", "설명"
        ))
        
        # 상태 확인
        assert result.has_errors is True
        assert result.has_warnings is True
        assert result.error_count == 1
        assert result.warning_count == 1
    
    def test_category_specific_issue_checks(self, sample_analysis_result):
        """카테고리별 이슈 존재 여부 확인 테스트
        
        폰트, 색상, 이미지 각 카테고리에 문제가 있는지
        빠르게 확인할 수 있는 속성들을 테스트합니다.
        """
        result = sample_analysis_result
        
        # 폰트 이슈: 임베딩되지 않은 폰트가 있음
        assert result.has_font_issues is True  # TimesNewRoman이 임베딩 안됨
        
        # 색상 이슈: RGB 사용 또는 높은 잉크량
        assert result.has_color_issues is False  # CMYK만 사용, 잉크량 280%
        
        # RGB 추가하면 이슈 발생
        result.colors.color_spaces_used.add(ColorSpace.RGB)
        assert result.has_color_issues is True
        
        # 이미지 이슈: 저해상도 이미지 존재
        assert result.has_image_issues is True  # 72dpi 이미지가 있음
    
    def test_summary_generation(self, sample_analysis_result):
        """분석 결과 요약 생성 테스트
        
        get_summary() 메서드는 분석 결과를 한눈에 볼 수 있는
        요약 정보를 딕셔너리 형태로 반환합니다.
        """
        result = sample_analysis_result
        result.analysis_duration = 1.23  # 분석 시간 설정
        
        # 이슈 추가
        result.add_issue(QualityIssue(
            IssueCategory.FONT_EMBEDDING, IssueSeverity.ERROR, "오류", "설명"
        ))
        result.add_issue(QualityIssue(
            IssueCategory.IMAGE_RESOLUTION, IssueSeverity.WARNING, "경고", "설명"
        ))
        
        summary = result.get_summary()
        
        # 문서 정보
        assert summary['document'] == "test.pdf"
        assert summary['pages'] == 10
        assert summary['quality_score'] == 87.0  # 100 - 10 - 3
        
        # 이슈 카운트
        assert summary['errors'] == 1
        assert summary['warnings'] == 1
        
        # 폰트 정보
        assert summary['fonts']['total'] == 2
        assert summary['fonts']['embedded'] == 1
        assert summary['fonts']['embedding_rate'] == "50.0%"
        
        # 색상 정보
        assert "CMYK" in summary['colors']['mode']
        assert summary['colors']['max_ink_coverage'] == "280%"
        
        # 이미지 정보
        assert summary['images']['total'] == 2
        assert summary['images']['low_resolution'] == 1
        
        # 분석 시간
        assert summary['analysis_time'] == "1.23s"


class TestImpositionReadiness:
    """ImpositionReadiness 스텁 클래스 테스트
    
    Phase 1에서는 기본 구조만 테스트합니다.
    실제 판짜기 기능은 향후 구현될 예정입니다.
    """
    
    def test_imposition_readiness_stub(self):
        """판짜기 준비 상태 스텁 테스트"""
        readiness = ImpositionReadiness()
        
        # 기본값 확인
        assert readiness.is_ready is False
        assert readiness.issues == []
        assert readiness.warnings == []
        
        # 이슈 추가
        readiness.add_issue("페이지 크기가 일정하지 않습니다")
        assert len(readiness.issues) == 1
        assert readiness.is_ready is False  # 이슈가 있으면 준비 안됨
        
        # 경고 추가
        readiness.add_warning("재단선이 없는 페이지가 있습니다")
        assert len(readiness.warnings) == 1


if __name__ == "__main__":
    # 테스트 실행 - 자세한 출력과 함께
    pytest.main([__file__, "-v", "--tb=short"])