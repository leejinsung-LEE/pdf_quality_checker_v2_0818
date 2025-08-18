# src/reporting/report_generator/utils.py
"""
보고서 생성 유틸리티 함수
"""

from typing import Optional
from pathlib import Path
from datetime import datetime


class ReportUtils:
    """보고서 유틸리티"""
    
    @staticmethod
    def generate_report_filename(original_filename: str, 
                                format_type: str,
                                extension: str) -> str:
        """
        보고서 파일명 생성
        
        Args:
            original_filename: 원본 파일명
            format_type: 보고서 형식
            extension: 파일 확장자
            
        Returns:
            생성된 파일명
        """
        # 타임스탬프 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 기본 파일명 추출
        base_name = Path(original_filename).stem
        
        # 보고서 파일명 생성
        report_filename = f"{base_name}_report_{format_type}_{timestamp}{extension}"
        
        return report_filename
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        시간 포맷팅
        
        Args:
            seconds: 초 단위 시간
            
        Returns:
            포맷팅된 시간 문자열
        """
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}초"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}분 {secs}초"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}시간 {minutes}분"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        파일명 정리 (안전한 문자만 사용)
        
        Args:
            filename: 원본 파일명
            
        Returns:
            정리된 파일명
        """
        # 금지된 문자 제거
        invalid_chars = '<>:"|?*\\/\r\n'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 공백을 언더스코어로
        filename = filename.replace(' ', '_')
        
        # 중복 언더스코어 제거
        while '__' in filename:
            filename = filename.replace('__', '_')
        
        # 최대 길이 제한 (255자)
        max_length = 200  # 확장자와 여유분 고려
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename
    
    @staticmethod
    def get_report_template_path(template_name: str) -> Optional[Path]:
        """
        보고서 템플릿 경로 반환
        
        Args:
            template_name: 템플릿 이름
            
        Returns:
            템플릿 파일 경로
        """
        templates_dir = Path(__file__).parent.parent / 'templates'
        template_path = templates_dir / f"{template_name}.jinja2"
        
        if template_path.exists():
            return template_path
        
        return None
    
    @staticmethod
    def format_percentage(value: float, total: float) -> str:
        """
        백분율 포맷팅
        
        Args:
            value: 값
            total: 전체 값
            
        Returns:
            포맷팅된 백분율 문자열
        """
        if total == 0:
            return "0%"
        
        percentage = (value / total) * 100
        return f"{percentage:.1f}%"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        텍스트 자르기
        
        Args:
            text: 원본 텍스트
            max_length: 최대 길이
            suffix: 접미사
            
        Returns:
            잘린 텍스트
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_issue_count(count: int, singular: str = "개", plural: str = None) -> str:
        """
        이슈 개수 포맷팅
        
        Args:
            count: 개수
            singular: 단수 단위
            plural: 복수 단위
            
        Returns:
            포맷팅된 문자열
        """
        if plural is None:
            plural = singular
        
        unit = singular if count == 1 else plural
        return f"{count}{unit}"