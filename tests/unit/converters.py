# src/utils/converters.py
"""
변환 유틸리티 함수들

PDF 분석에 필요한 다양한 단위 변환 및 형식 변환 함수들을 제공합니다.
"""

from typing import Union, Optional


def points_to_mm(points: float) -> float:
    """
    포인트를 밀리미터로 변환
    
    1 포인트 = 0.352778 mm
    
    Args:
        points: 포인트 값
        
    Returns:
        float: 밀리미터 값
    """
    return points * 0.352778


def mm_to_points(mm: float) -> float:
    """
    밀리미터를 포인트로 변환
    
    1 mm = 2.834646 포인트
    
    Args:
        mm: 밀리미터 값
        
    Returns:
        float: 포인트 값
    """
    return mm * 2.834646


def format_size_mm(width_mm: float, height_mm: float) -> str:
    """
    크기를 밀리미터 형식으로 포맷팅
    
    Args:
        width_mm: 너비 (mm)
        height_mm: 높이 (mm)
        
    Returns:
        str: 포맷된 크기 문자열 (예: "210 x 297 mm")
    """
    return f"{width_mm:.0f} x {height_mm:.0f} mm"


def format_file_size(size_bytes: int) -> str:
    """
    파일 크기를 사람이 읽기 쉬운 형식으로 변환
    
    Args:
        size_bytes: 바이트 단위 크기
        
    Returns:
        str: 포맷된 크기 문자열 (예: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            if unit == 'B':
                return f"{size_bytes} {unit}"
            else:
                return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"


def safe_str(value: any, default: str = '') -> str:
    """
    안전한 문자열 변환
    
    None이나 변환 실패 시 기본값 반환
    
    Args:
        value: 변환할 값
        default: 기본값
        
    Returns:
        str: 변환된 문자열
    """
    if value is None:
        return default
    
    try:
        # pikepdf String 객체 처리
        if hasattr(value, '__str__'):
            result = str(value)
            # PDF 문자열에서 불필요한 문자 제거
            if result.startswith('(') and result.endswith(')'):
                result = result[1:-1]
            return result
        else:
            return str(value)
    except Exception:
        return default


def safe_integer(value: any, default: int = 0) -> int:
    """
    안전한 정수 변환
    
    Args:
        value: 변환할 값
        default: 기본값
        
    Returns:
        int: 변환된 정수
    """
    if value is None:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: any, default: float = 0.0) -> float:
    """
    안전한 실수 변환
    
    Args:
        value: 변환할 값
        default: 기본값
        
    Returns:
        float: 변환된 실수
    """
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def calculate_dpi(pixels: int, size_mm: float) -> float:
    """
    DPI (Dots Per Inch) 계산
    
    Args:
        pixels: 픽셀 수
        size_mm: 밀리미터 단위 크기
        
    Returns:
        float: DPI 값
    """
    if size_mm <= 0:
        return 0.0
    
    inches = size_mm / 25.4  # 1 inch = 25.4 mm
    return pixels / inches if inches > 0 else 0.0


def get_paper_size_name(width_mm: float, height_mm: float, tolerance: float = 2.0) -> str:
    """
    용지 크기 이름 가져오기
    
    Args:
        width_mm: 너비 (mm)
        height_mm: 높이 (mm)
        tolerance: 허용 오차 (mm)
        
    Returns:
        str: 용지 크기 이름 (예: "A4", "Letter")
    """
    # 표준 용지 크기 정의
    paper_sizes = {
        'A0': (841, 1189),
        'A1': (594, 841),
        'A2': (420, 594),
        'A3': (297, 420),
        'A4': (210, 297),
        'A5': (148, 210),
        'A6': (105, 148),
        'Letter': (216, 279),
        'Legal': (216, 356),
        'Tabloid': (279, 432),
        'B4': (250, 353),
        'B5': (176, 250)
    }
    
    # 가로/세로 모두 확인
    for name, (std_width, std_height) in paper_sizes.items():
        # 정방향 확인
        if (abs(width_mm - std_width) <= tolerance and 
            abs(height_mm - std_height) <= tolerance):
            return name
        # 회전된 방향 확인
        if (abs(width_mm - std_height) <= tolerance and 
            abs(height_mm - std_width) <= tolerance):
            return f"{name} (가로)"
    
    return "사용자 정의"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    백분율 형식으로 변환
    
    Args:
        value: 0-1 사이의 값
        decimals: 소수점 자리수
        
    Returns:
        str: 백분율 문자열 (예: "75.5%")
    """
    percentage = value * 100
    return f"{percentage:.{decimals}f}%"


def truncate_text(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """
    긴 텍스트를 적절한 길이로 자르기
    
    Args:
        text: 원본 텍스트
        max_length: 최대 길이
        suffix: 생략 표시
        
    Returns:
        str: 잘린 텍스트
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix