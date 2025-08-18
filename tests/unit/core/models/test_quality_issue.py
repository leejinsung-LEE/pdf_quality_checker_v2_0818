"""
QualityIssue 모델 단위 테스트

PDF 검사 중 발견된 품질 문제를 표현하는 QualityIssue 모델과
관련 클래스들(IssueSeverity, IssueCategory, FixOption)의 동작을 검증합니다.

이 테스트는 다음을 확인합니다:
- 이슈의 올바른 생성과 분류
- 심각도와 카테고리의 적절한 관리
- 자동 수정 옵션의 표현
- 이슈의 정렬과 필터링
"""

import pytest
from datetime import datetime
from typing import List

# 테스트할 모듈들을 임포트
from src.core.models.quality_issue import (
    QualityIssue, IssueSeverity, IssueCategory, FixOption,
    create_font_not_embedded_issue,
    create_rgb_color_issue,
    create_low_resolution_image_issue,
    create_high_ink_coverage_issue,
    create_missing_bleed_issue
)


class TestIssueSeverity:
    """IssueSeverity Enum 테스트
    
    이슈의 심각도를 나타내는 열거형이 올바르게 동작하는지 확인합니다.
    각 심각도는 이모지, 우선순위 등의 속성을 가집니다.
    """
    
    def test_severity_values(self):
        """심각도 값 확인"""
        assert IssueSeverity.ERROR.value == "error"
        assert IssueSeverity.WARNING.value == "warning"
        assert IssueSeverity.INFO.value == "info"
        assert IssueSeverity.SUCCESS.value == "success"
    
    def test_severity_emoji(self):
        """심각도별 이모지 확인"""
        assert IssueSeverity.ERROR.emoji == "❌"
        assert IssueSeverity.WARNING.emoji == "⚠️"
        assert IssueSeverity.INFO.emoji == "ℹ️"
        assert IssueSeverity.SUCCESS.emoji == "✅"
    
    def test_severity_priority(self):
        """심각도별 우선순위 확인 (낮을수록 중요)"""
        assert IssueSeverity.ERROR.priority == 1
        assert IssueSeverity.WARNING.priority == 2
        assert IssueSeverity.INFO.priority == 3
        assert IssueSeverity.SUCCESS.priority == 4
        
        # 우선순위 순서 확인
        assert IssueSeverity.ERROR.priority < IssueSeverity.WARNING.priority
        assert IssueSeverity.WARNING.priority < IssueSeverity.INFO.priority


class TestIssueCategory:
    """IssueCategory Enum 테스트
    
    이슈의 카테고리를 나타내는 열거형이 올바르게 동작하는지 확인합니다.
    각 카테고리는 사용자 친화적인 표시 이름을 가집니다.
    """
    
    def test_category_values(self):
        """카테고리 값 확인"""
        # 폰트 관련
        assert IssueCategory.FONT_EMBEDDING.value == "font_embedding"
        assert IssueCategory.FONT_TYPE.value == "font_type"
        
        # 색상 관련
        assert IssueCategory.COLOR_SPACE.value == "color_space"
        assert IssueCategory.INK_COVERAGE.value == "ink_coverage"
        
        # 이미지 관련
        assert IssueCategory.IMAGE_RESOLUTION.value == "image_resolution"
        assert IssueCategory.IMAGE_COMPRESSION.value == "image_compression"
    
    def test_category_display_names(self):
        """카테고리 표시 이름 확인"""
        assert IssueCategory.FONT_EMBEDDING.display_name == "폰트 임베딩"
        assert IssueCategory.COLOR_SPACE.display_name == "색상 공간"
        assert IssueCategory.IMAGE_RESOLUTION.display_name == "이미지 해상도"
        assert IssueCategory.PAGE_BLEED.display_name == "재단선"
        assert IssueCategory.INK_COVERAGE.display_name == "잉크량"
        
        # 기본 카테고리
        assert IssueCategory.GENERAL.display_name == "일반"


class TestFixOption:
    """FixOption 클래스 테스트
    
    자동 수정 옵션을 표현하는 FixOption 클래스를 테스트합니다.
    각 수정 옵션은 방법, 설명, 위험도 등의 정보를 포함합니다.
    """
    
    def test_fix_option_creation(self):
        """FixOption 객체 생성 테스트"""
        fix = FixOption(
            method="convert_rgb_to_cmyk",
            description="RGB를 CMYK로 변환",
            parameters={"profile": "ISO Coated v2"},
            estimated_time=5.0,
            risk_level="low"
        )
        
        assert fix.method == "convert_rgb_to_cmyk"
        assert fix.description == "RGB를 CMYK로 변환"
        assert fix.parameters["profile"] == "ISO Coated v2"
        assert fix.estimated_time == 5.0
        assert fix.risk_level == "low"
    
    def test_fix_option_safety(self):
        """수정 옵션의 안전성 확인 테스트"""
        # 안전한 수정 (low risk)
        safe_fix = FixOption("embed_font", "폰트 임베딩", risk_level="low")
        assert safe_fix.is_safe is True
        
        # 중간 위험도 수정
        medium_fix = FixOption("outline_text", "텍스트 아웃라인 변환", risk_level="medium")
        assert medium_fix.is_safe is False
        
        # 높은 위험도 수정
        risky_fix = FixOption("resample_image", "이미지 리샘플링", risk_level="high")
        assert risky_fix.is_safe is False


class TestQualityIssue:
    """QualityIssue 클래스 테스트
    
    PDF 품질 이슈를 표현하는 핵심 클래스를 테스트합니다.
    이슈의 생성, 관리, 표현 등 모든 기능을 검증합니다.
    """
    
    def test_quality_issue_creation(self):
        """QualityIssue 객체 생성 테스트"""
        issue = QualityIssue(
            category=IssueCategory.FONT_EMBEDDING,
            severity=IssueSeverity.ERROR,
            title="폰트 미임베딩",
            description="Arial 폰트가 임베딩되지 않았습니다",
            pages=[1, 2, 3]
        )
        
        assert issue.category == IssueCategory.FONT_EMBEDDING
        assert issue.severity == IssueSeverity.ERROR
        assert issue.title == "폰트 미임베딩"
        assert issue.pages == [1, 2, 3]
        assert isinstance(issue.detected_at, datetime)
    
    def test_quality_issue_string_conversion(self):
        """문자열 타입으로 생성 시 자동 변환 테스트"""
        # 문자열로 생성해도 Enum으로 자동 변환
        issue = QualityIssue(
            category="font_embedding",  # 문자열
            severity="error",           # 문자열
            title="테스트",
            description="설명"
        )
        
        assert isinstance(issue.category, IssueCategory)
        assert isinstance(issue.severity, IssueSeverity)
        assert issue.category == IssueCategory.FONT_EMBEDDING
        assert issue.severity == IssueSeverity.ERROR
    
    def test_fixability_checks(self):
        """수정 가능 여부 확인 테스트"""
        issue = QualityIssue(
            IssueCategory.COLOR_SPACE,
            IssueSeverity.WARNING,
            "RGB 색상 사용",
            "CMYK로 변환이 필요합니다"
        )
        
        # 초기 상태 - 수정 옵션 없음
        assert issue.is_fixable is False
        assert issue.safe_fix_available is False
        
        # 안전한 수정 옵션 추가
        issue.add_fix_option(
            method="convert_rgb_to_cmyk",
            description="RGB를 CMYK로 변환",
            risk_level="low"
        )
        
        assert issue.is_fixable is True
        assert issue.safe_fix_available is True
        
        # 위험한 수정 옵션만 추가
        risky_issue = QualityIssue(
            IssueCategory.IMAGE_RESOLUTION,
            IssueSeverity.ERROR,
            "저해상도 이미지",
            "이미지 품질이 낮습니다"
        )
        risky_issue.add_fix_option(
            method="resample_image",
            description="이미지 리샘플링",
            risk_level="high"
        )
        
        assert risky_issue.is_fixable is True
        assert risky_issue.safe_fix_available is False
    
    def test_page_information(self):
        """페이지 정보 관련 기능 테스트"""
        # 특정 페이지에만 영향
        page_issue = QualityIssue(
            IssueCategory.IMAGE_RESOLUTION,
            IssueSeverity.WARNING,
            "저해상도 이미지",
            "이미지 해상도가 낮습니다",
            pages=[1, 3, 5, 7, 9]
        )
        
        assert page_issue.pages_affected == 5
        assert page_issue.page_range_str == "페이지 1, 3, 5, 7, 9"
        
        # 많은 페이지에 영향 (6개 이상)
        many_pages_issue = QualityIssue(
            IssueCategory.FONT_EMBEDDING,
            IssueSeverity.ERROR,
            "폰트 문제",
            "폰트가 임베딩되지 않았습니다",
            pages=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        )
        
        assert many_pages_issue.pages_affected == 10
        assert "1-10 (10개)" in many_pages_issue.page_range_str
        
        # 전체 문서에 영향
        doc_issue = QualityIssue(
            IssueCategory.PDF_VERSION,
            IssueSeverity.INFO,
            "PDF 버전",
            "PDF 1.4 버전입니다",
            pages=[]  # 빈 리스트는 전체 문서를 의미
        )
        
        assert doc_issue.pages_affected == -1
        assert doc_issue.page_range_str == "전체 문서"
    
    def test_full_description_with_details(self):
        """상세 정보가 포함된 전체 설명 테스트"""
        # 기본 설명만 있는 경우
        simple_issue = QualityIssue(
            IssueCategory.FONT_EMBEDDING,
            IssueSeverity.ERROR,
            "폰트 문제",
            "폰트가 임베딩되지 않았습니다"
        )
        
        assert simple_issue.full_description == "폰트가 임베딩되지 않았습니다"
        
        # 상세 정보가 있는 경우
        detailed_issue = QualityIssue(
            IssueCategory.FONT_EMBEDDING,
            IssueSeverity.ERROR,
            "폰트 문제",
            "폰트가 임베딩되지 않았습니다",
            details={
                "count": 3,
                "names": ["Arial", "Helvetica", "Times"]
            }
        )
        
        full_desc = detailed_issue.full_description
        assert "3개 발견" in full_desc
        assert "Arial, Helvetica, Times" in full_desc
        
        # 많은 항목이 있는 경우
        many_items_issue = QualityIssue(
            IssueCategory.IMAGE_RESOLUTION,
            IssueSeverity.WARNING,
            "저해상도 이미지",
            "저해상도 이미지가 발견되었습니다",
            details={
                "count": 10,
                "names": ["img1", "img2", "img3", "img4", "img5", "img6"],
                "resolution": 150
            }
        )
        
        full_desc = many_items_issue.full_description
        assert "img1, img2, img3 외 3개" in full_desc
        assert "해상도: 150dpi" in full_desc
    
    def test_issue_sorting(self):
        """이슈 정렬 테스트 (심각도 우선, 그 다음 카테고리)"""
        issues = [
            QualityIssue(IssueCategory.FONT_EMBEDDING, IssueSeverity.WARNING, "경고1", "설명"),
            QualityIssue(IssueCategory.COLOR_SPACE, IssueSeverity.ERROR, "오류1", "설명"),
            QualityIssue(IssueCategory.IMAGE_RESOLUTION, IssueSeverity.ERROR, "오류2", "설명"),
            QualityIssue(IssueCategory.METADATA, IssueSeverity.INFO, "정보1", "설명"),
        ]
        
        # 정렬
        sorted_issues = sorted(issues)
        
        # 심각도 순서 확인 (ERROR -> WARNING -> INFO)
        assert sorted_issues[0].severity == IssueSeverity.ERROR
        assert sorted_issues[1].severity == IssueSeverity.ERROR
        assert sorted_issues[2].severity == IssueSeverity.WARNING
        assert sorted_issues[3].severity == IssueSeverity.INFO
        
        # 같은 심각도 내에서는 카테고리 알파벳 순
        assert sorted_issues[0].category == IssueCategory.COLOR_SPACE
        assert sorted_issues[1].category == IssueCategory.IMAGE_RESOLUTION
    
    def test_issue_to_dict(self):
        """딕셔너리 변환 테스트 (JSON 직렬화용)"""
        issue = QualityIssue(
            category=IssueCategory.FONT_EMBEDDING,
            severity=IssueSeverity.ERROR,
            title="폰트 미임베딩",
            description="Arial 폰트가 임베딩되지 않았습니다",
            pages=[1, 2, 3],
            details={"font_name": "Arial"},
            related_objects=["Arial"]
        )
        
        # 수정 옵션 추가
        issue.add_fix_option(
            method="embed_font",
            description="폰트를 PDF에 임베딩",
            risk_level="low"
        )
        
        # 딕셔너리로 변환
        issue_dict = issue.to_dict()
        
        assert issue_dict['category'] == "font_embedding"
        assert issue_dict['category_display'] == "폰트 임베딩"
        assert issue_dict['severity'] == "error"
        assert issue_dict['severity_emoji'] == "❌"
        assert issue_dict['title'] == "폰트 미임베딩"
        assert issue_dict['pages'] == [1, 2, 3]
        assert issue_dict['page_range'] == "페이지 1, 2, 3"
        assert issue_dict['is_fixable'] is True
        assert len(issue_dict['fix_options']) == 1
        assert issue_dict['fix_options'][0]['method'] == "embed_font"
        assert 'detected_at' in issue_dict  # ISO 형식 날짜
    
    def test_string_representations(self):
        """문자열 표현 테스트"""
        issue = QualityIssue(
            IssueCategory.COLOR_SPACE,
            IssueSeverity.WARNING,
            "RGB 색상 사용",
            "인쇄용으로 적합하지 않습니다"
        )
        
        # str() - 사용자 친화적 표현
        str_repr = str(issue)
        assert "⚠️" in str_repr
        assert "색상 공간" in str_repr
        assert "RGB 색상 사용" in str_repr
        
        # repr() - 개발자용 표현
        repr_str = repr(issue)
        assert "QualityIssue" in repr_str
        assert "category=color_space" in repr_str
        assert "severity=warning" in repr_str


class TestIssueFactoryFunctions:
    """이슈 생성 팩토리 함수 테스트
    
    자주 사용되는 이슈들을 쉽게 생성할 수 있는
    팩토리 함수들이 올바르게 동작하는지 확인합니다.
    """
    
    def test_create_font_not_embedded_issue(self):
        """폰트 미임베딩 이슈 생성 테스트"""
        issue = create_font_not_embedded_issue("Arial", [1, 2, 3])
        
        assert issue.category == IssueCategory.FONT_EMBEDDING
        assert issue.severity == IssueSeverity.ERROR
        assert "Arial" in issue.description
        assert issue.pages == [1, 2, 3]
        assert issue.details['font_name'] == "Arial"
        assert len(issue.fix_options) == 2  # embed_font, outline_text
        assert issue.related_objects == ["Arial"]
        
        # 수정 옵션 확인
        fix_methods = [fix.method for fix in issue.fix_options]
        assert "embed_font" in fix_methods
        assert "outline_text" in fix_methods
    
    def test_create_rgb_color_issue(self):
        """RGB 색상 사용 이슈 생성 테스트"""
        issue = create_rgb_color_issue(page_count=5)
        
        assert issue.category == IssueCategory.COLOR_SPACE
        assert issue.severity == IssueSeverity.WARNING
        assert "RGB" in issue.description
        assert "CMYK" in issue.description
        assert issue.pages == []  # 전체 문서
        assert issue.details['count'] == 5
        assert len(issue.fix_options) == 1
        
        # 수정 옵션 확인
        fix = issue.fix_options[0]
        assert fix.method == "convert_rgb_to_cmyk"
        assert fix.parameters['profile'] == 'ISO Coated v2'
        assert fix.risk_level == "low"
    
    def test_create_low_resolution_image_issue(self):
        """저해상도 이미지 이슈 생성 테스트"""
        # 경고 수준 (150-300 dpi)
        warning_issue = create_low_resolution_image_issue(page=1, resolution=200)
        assert warning_issue.severity == IssueSeverity.WARNING
        assert "200dpi" in warning_issue.description
        assert warning_issue.pages == [1]
        assert warning_issue.details['resolution'] == 200
        
        # 오류 수준 (150 dpi 미만)
        error_issue = create_low_resolution_image_issue(page=2, resolution=72)
        assert error_issue.severity == IssueSeverity.ERROR
        assert "72dpi" in error_issue.description
        
        # 수정 옵션 확인
        fix = error_issue.fix_options[0]
        assert fix.method == "resample_image"
        assert fix.parameters['target_dpi'] == 300
        assert fix.risk_level == "high"  # 품질 손실 가능
    
    def test_create_high_ink_coverage_issue(self):
        """높은 잉크량 이슈 생성 테스트"""
        # 경고 수준 (320-340%)
        warning_issue = create_high_ink_coverage_issue(page=3, coverage=330)
        assert warning_issue.severity == IssueSeverity.WARNING
        assert "330%" in warning_issue.description
        assert "320%" in warning_issue.description  # 권장 기준
        assert warning_issue.pages == [3]
        
        # 오류 수준 (340% 초과)
        error_issue = create_high_ink_coverage_issue(page=4, coverage=380)
        assert error_issue.severity == IssueSeverity.ERROR
        assert "380%" in error_issue.description
        assert "번짐" in error_issue.description
        
        # 수정 옵션 확인
        fix = error_issue.fix_options[0]
        assert fix.method == "reduce_ink_coverage"
        assert "GCR/UCR" in fix.description
        assert fix.parameters['target_coverage'] == 300
        assert fix.risk_level == "medium"
    
    def test_create_missing_bleed_issue(self):
        """재단선 누락 이슈 생성 테스트"""
        issue = create_missing_bleed_issue(pages=[1, 3, 5, 7])
        
        assert issue.category == IssueCategory.PAGE_BLEED
        assert issue.severity == IssueSeverity.WARNING
        assert "재단선" in issue.title
        assert "Bleed" in issue.description
        assert "흰 여백" in issue.description
        assert issue.pages == [1, 3, 5, 7]
        assert issue.details['required_bleed'] == 3.0
        
        # 수정 옵션 확인
        fix = issue.fix_options[0]
        assert fix.method == "add_bleed"
        assert fix.parameters['bleed_size'] == 3.0
        assert fix.risk_level == "high"  # 컨텐츠 확장 필요


class TestComplexScenarios:
    """복잡한 시나리오 테스트
    
    실제 사용 상황에서 발생할 수 있는 복잡한 케이스들을 테스트합니다.
    """
    
    def test_multiple_issues_same_category(self):
        """같은 카테고리의 여러 이슈 관리"""
        issues: List[QualityIssue] = []
        
        # 여러 폰트 문제
        fonts = ["Arial", "Helvetica", "Times New Roman", "Calibri"]
        for i, font in enumerate(fonts):
            issue = create_font_not_embedded_issue(font, [i+1])
            issues.append(issue)
        
        # 카테고리별 그룹화
        font_issues = [issue for issue in issues if issue.category == IssueCategory.FONT_EMBEDDING]
        assert len(font_issues) == 4
        
        # 관련 객체 확인
        all_fonts = []
        for issue in font_issues:
            all_fonts.extend(issue.related_objects)
        assert set(all_fonts) == set(fonts)
    
    def test_issue_with_multiple_fix_options(self):
        """여러 수정 옵션이 있는 이슈"""
        issue = QualityIssue(
            IssueCategory.FONT_EMBEDDING,
            IssueSeverity.ERROR,
            "복잡한 폰트 문제",
            "특수 폰트가 임베딩되지 않았습니다"
        )
        
        # 여러 수정 옵션 추가 (위험도 순)
        issue.add_fix_option(
            method="embed_font",
            description="폰트 임베딩 시도",
            risk_level="low",
            estimated_time=2.0
        )
        
        issue.add_fix_option(
            method="substitute_font",
            description="유사 폰트로 대체",
            risk_level="medium",
            estimated_time=1.0
        )
        
        issue.add_fix_option(
            method="outline_text",
            description="텍스트를 아웃라인으로 변환",
            risk_level="high",
            estimated_time=5.0
        )
        
        assert len(issue.fix_options) == 3
        assert issue.is_fixable is True
        assert issue.safe_fix_available is True  # low risk 옵션이 있음
        
        # 안전한 옵션만 필터링
        safe_options = [fix for fix in issue.fix_options if fix.is_safe]
        assert len(safe_options) == 1
        assert safe_options[0].method == "embed_font"
    
    def test_issue_priority_in_report(self):
        """보고서에서의 이슈 우선순위 테스트"""
        # 다양한 심각도와 카테고리의 이슈들
        issues = [
            # 정보성 이슈들
            QualityIssue(IssueCategory.METADATA, IssueSeverity.INFO, "메타데이터 누락", "PDF 제목 없음"),
            QualityIssue(IssueCategory.PDF_VERSION, IssueSeverity.INFO, "구버전 PDF", "PDF 1.4"),
            
            # 경고 이슈들
            create_rgb_color_issue(3),
            create_missing_bleed_issue([1, 2]),
            
            # 오류 이슈들
            create_font_not_embedded_issue("CustomFont", [1, 2, 3]),
            create_low_resolution_image_issue(5, 72),
            create_high_ink_coverage_issue(7, 380),
        ]
        
        # 심각도별 정렬
        sorted_by_severity = sorted(issues, key=lambda x: x.severity.priority)
        
        # 처음 3개는 오류여야 함
        for i in range(3):
            assert sorted_by_severity[i].severity == IssueSeverity.ERROR
        
        # 그 다음 2개는 경고
        for i in range(3, 5):
            assert sorted_by_severity[i].severity == IssueSeverity.WARNING
        
        # 마지막 2개는 정보
        for i in range(5, 7):
            assert sorted_by_severity[i].severity == IssueSeverity.INFO


if __name__ == "__main__":
    # 테스트 실행 - 상세 출력, 커버리지 포함
    pytest.main([__file__, "-v", "--cov=src.core.models.quality_issue", "--cov-report=term-missing"])