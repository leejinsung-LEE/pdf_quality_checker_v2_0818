# src/reporting/json_builder.py
"""
JSON 보고서 빌더

품질 검사 결과를 구조화된 JSON 형식으로 변환합니다.
API 연동 및 데이터 교환을 위한 표준 포맷을 제공합니다.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .report_generator import ReportBuilder, ReportOptions
from ..core.quality_checker import QualityCheckResult
from ..core.models import QualityIssue, AnalysisResult
from ..core.models.quality_issue import IssueSeverity, IssueCategory


class JSONReportBuilder(ReportBuilder):
    """JSON 보고서 빌더 - API 연동을 위한 구조화된 데이터 생성"""
    
    def build(self, 
              quality_result: QualityCheckResult,
              additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        JSON 보고서 생성
        
        Args:
            quality_result: 품질 검사 결과
            additional_data: 추가 데이터 (썸네일, 차트 데이터 등)
            
        Returns:
            str: JSON 문자열
        """
        # 전체 보고서 구조 생성
        report_data = self._create_report_structure(quality_result, additional_data)
        
        # JSON 문자열로 변환 (들여쓰기 포함, 한글 유지)
        return json.dumps(report_data, ensure_ascii=False, indent=2)
    
    def get_file_extension(self) -> str:
        """파일 확장자 반환"""
        return '.json'
    
    def _create_report_structure(self, 
                                quality_result: QualityCheckResult,
                                additional_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        보고서 데이터 구조 생성
        
        Args:
            quality_result: 품질 검사 결과
            additional_data: 추가 데이터
            
        Returns:
            Dict[str, Any]: 구조화된 보고서 데이터
        """
        analysis = quality_result.analysis_result
        
        # 메타데이터
        metadata = self._create_metadata(quality_result)
        
        # 파일 정보
        file_info = self._create_file_info(analysis)
        
        # 요약 정보
        summary = self._create_summary(quality_result)
        
        # 분석 결과 상세
        analysis_details = self._create_analysis_details(analysis)
        
        # 품질 이슈 목록
        issues = self._create_issues_list(quality_result.issues)
        
        # 전체 구조 조합
        report_structure = {
            "metadata": metadata,
            "file_info": file_info,
            "summary": summary,
            "analysis_details": analysis_details,
            "issues": issues
        }
        
        # 추가 데이터가 있으면 포함
        if additional_data:
            if 'thumbnails' in additional_data:
                report_structure['thumbnails'] = additional_data['thumbnails']
            if 'fix_suggestions' in additional_data:
                report_structure['fix_suggestions'] = additional_data['fix_suggestions']
            if 'chart_data' in additional_data:
                report_structure['visualization_data'] = additional_data['chart_data']
        
        return report_structure
    
    def _create_metadata(self, quality_result: QualityCheckResult) -> Dict[str, Any]:
        """보고서 메타데이터 생성"""
        return {
            "report_version": "2.0.0",
            "generator": "PDF Quality Checker v2",
            "generated_at": quality_result.timestamp.isoformat(),
            "profile_used": quality_result.profile_name,
            "processing_time": {
                "analysis_seconds": quality_result.analysis_result.analysis_duration,
                "check_seconds": quality_result.check_duration,
                "total_seconds": quality_result.analysis_result.analysis_duration + quality_result.check_duration
            },
            "analyzer_version": quality_result.analysis_result.analyzer_version
        }
    
    def _create_file_info(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """파일 정보 생성"""
        doc = analysis.document
        
        return {
            "filename": doc.filename,
            "full_path": str(doc.path),
            "file_size": doc.file_size,
            "file_size_formatted": self._format_file_size(doc.file_size),
            "file_hash": doc.file_hash,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "pdf_version": doc.pdf_version,
            "page_count": doc.page_count,
            "is_encrypted": doc.is_encrypted,
            "is_uniform_size": doc.is_uniform_size,
            "metadata": doc.metadata
        }
    
    def _create_summary(self, quality_result: QualityCheckResult) -> Dict[str, Any]:
        """요약 정보 생성"""
        return {
            "quality_score": quality_result.quality_score,
            "quality_grade": self._calculate_grade(quality_result.quality_score),
            "total_issues": len(quality_result.issues),
            "issues_by_severity": {
                "error": quality_result.error_count,
                "warning": quality_result.warning_count,
                "info": quality_result.info_count
            },
            "has_critical_issues": quality_result.has_errors,
            "is_print_ready": quality_result.quality_score >= 90 and not quality_result.has_errors,
            "recommendations": self._generate_recommendations(quality_result)
        }
    
    def _create_analysis_details(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """분석 결과 상세 정보"""
        details = {
            "pages": self._create_pages_info(analysis.pages),
            "fonts": self._create_fonts_info(analysis.fonts),
            "colors": self._create_colors_info(analysis.colors),
            "images": self._create_images_info(analysis.images)
        }
        
        # 판짜기 준비 상태 (있는 경우)
        if hasattr(analysis, 'imposition_readiness') and analysis.imposition_readiness:
            details['imposition_readiness'] = {
                "is_ready": analysis.imposition_readiness.is_ready,
                "issues": analysis.imposition_readiness.issues,
                "warnings": analysis.imposition_readiness.warnings
            }
        
        return details
    
    def _create_pages_info(self, pages: List[Any]) -> Dict[str, Any]:
        """페이지 정보 생성"""
        if not pages:
            return {"count": 0}
        
        # 페이지 크기 분포
        size_distribution = {}
        for page in pages:
            size_key = f"{page.width_mm:.1f}x{page.height_mm:.1f}mm"
            size_distribution[size_key] = size_distribution.get(size_key, 0) + 1
        
        return {
            "count": len(pages),
            "size_distribution": size_distribution,
            "has_transparency": any(p.has_transparency for p in pages),
            "has_overprint": any(p.has_overprint for p in pages),
            "all_have_bleed": all(p.bleed_info and p.bleed_info.has_proper_bleed for p in pages if hasattr(p, 'bleed_info'))
        }
    
    def _create_fonts_info(self, fonts: Dict[str, Any]) -> Dict[str, Any]:
        """폰트 정보 생성"""
        font_list = []
        for name, info in fonts.items():
            font_list.append({
                "name": name,
                "type": info.font_type,
                "is_embedded": info.is_embedded,
                "is_subset": info.is_subset,
                "encoding": info.encoding,
                "pages_used": len(info.pages_used)
            })
        
        return {
            "total_count": len(fonts),
            "embedded_count": sum(1 for f in fonts.values() if f.is_embedded),
            "not_embedded_count": sum(1 for f in fonts.values() if not f.is_embedded),
            "type3_count": sum(1 for f in fonts.values() if f.font_type == "Type3"),
            "fonts": font_list
        }
    
    def _create_colors_info(self, colors: Any) -> Dict[str, Any]:
        """색상 정보 생성"""
        return {
            "color_spaces": list(colors.color_spaces),
            "has_rgb": colors.has_rgb,
            "has_cmyk": colors.has_cmyk,
            "has_spot_colors": colors.has_spot_colors,
            "spot_colors": list(colors.spot_colors),
            "spot_color_count": len(colors.spot_colors),
            "has_transparency": colors.has_transparency
        }
    
    def _create_images_info(self, images: List[Any]) -> Dict[str, Any]:
        """이미지 정보 생성"""
        if not images:
            return {"count": 0}
        
        # DPI 분포
        dpi_ranges = {
            "below_150": 0,
            "150_to_300": 0,
            "above_300": 0
        }
        
        # 압축 타입 분포
        compression_types = {}
        
        for img in images:
            # DPI 분류
            if img.dpi_x < 150:
                dpi_ranges["below_150"] += 1
            elif img.dpi_x <= 300:
                dpi_ranges["150_to_300"] += 1
            else:
                dpi_ranges["above_300"] += 1
            
            # 압축 타입 집계
            comp_type = img.compression or "unknown"
            compression_types[comp_type] = compression_types.get(comp_type, 0) + 1
        
        return {
            "count": len(images),
            "dpi_distribution": dpi_ranges,
            "compression_types": compression_types,
            "average_dpi": sum(img.dpi_x for img in images) / len(images) if images else 0,
            "total_size_bytes": sum(img.file_size for img in images if hasattr(img, 'file_size') and img.file_size)
        }
    
    def _create_issues_list(self, issues: List[QualityIssue]) -> List[Dict[str, Any]]:
        """이슈 목록 생성"""
        issues_list = []
        
        for issue in issues:
            issue_dict = {
                "id": f"issue_{len(issues_list) + 1}",
                "category": issue.category.value,
                "category_display": issue.category.display_name,
                "severity": issue.severity.value,
                "severity_priority": issue.severity.priority,
                "title": issue.title,
                "description": issue.description,
                "full_description": issue.full_description,
                "pages": issue.pages,
                "page_range": issue.page_range_str,
                "is_fixable": issue.is_fixable,
                "safe_fix_available": issue.safe_fix_available,
                "fix_options": [
                    {
                        "method": fix.method,
                        "description": fix.description,
                        "risk_level": fix.risk_level,
                        "is_safe": fix.is_safe
                    }
                    for fix in issue.fix_options
                ],
                "details": issue.details,
                "related_objects": issue.related_objects
            }
            
            # 위치 정보가 있으면 포함
            if issue.location:
                issue_dict["location"] = issue.location
            
            issues_list.append(issue_dict)
        
        # 심각도 우선순위로 정렬
        issues_list.sort(key=lambda x: (x["severity_priority"], x["category"]))
        
        return issues_list
    
    def _calculate_grade(self, score: float) -> str:
        """점수를 등급으로 변환"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, quality_result: QualityCheckResult) -> List[str]:
        """품질 검사 결과에 따른 권장사항 생성"""
        recommendations = []
        
        # 오류가 있는 경우
        if quality_result.has_errors:
            recommendations.append("인쇄 전 반드시 오류를 수정하세요.")
            
            # 폰트 임베딩 오류
            font_errors = [i for i in quality_result.issues 
                          if i.category == IssueCategory.FONT_EMBEDDING and i.severity == IssueSeverity.ERROR]
            if font_errors:
                recommendations.append("누락된 폰트를 임베딩하거나 아웃라인으로 변환하세요.")
            
            # RGB 색상 오류
            color_errors = [i for i in quality_result.issues 
                           if i.category == IssueCategory.COLOR_SPACE and i.severity == IssueSeverity.ERROR]
            if color_errors:
                recommendations.append("RGB 색상을 CMYK로 변환하세요.")
        
        # 경고가 있는 경우
        if quality_result.has_warnings:
            # 저해상도 이미지
            image_warnings = [i for i in quality_result.issues 
                             if i.category == IssueCategory.IMAGE_RESOLUTION]
            if image_warnings:
                recommendations.append("이미지 해상도를 300 DPI 이상으로 높이는 것을 권장합니다.")
            
            # 재단선 누락
            bleed_warnings = [i for i in quality_result.issues 
                             if i.category == IssueCategory.PAGE_BLEED]
            if bleed_warnings:
                recommendations.append("재단선(Bleed)을 3mm 이상 추가하세요.")
        
        # 품질 점수에 따른 일반 권장사항
        if quality_result.quality_score < 70:
            recommendations.append("전문가의 검토를 받는 것을 강력히 권장합니다.")
        elif quality_result.quality_score < 85:
            recommendations.append("인쇄 전 샘플 출력으로 품질을 확인하세요.")
        elif quality_result.quality_score >= 95:
            recommendations.append("우수한 인쇄 품질이 예상됩니다.")
        
        return recommendations
    
    def _format_file_size(self, size: int) -> str:
        """파일 크기 포맷팅"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"