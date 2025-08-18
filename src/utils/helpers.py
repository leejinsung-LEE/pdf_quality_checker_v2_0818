# src/utils/helpers.py
"""
유틸리티 헬퍼 함수들

PDF 분석에 필요한 다양한 유틸리티 함수들을 제공합니다.
"""

from typing import Tuple, Optional, Union
import math


def calculate_dpi(pixel_width: int, pixel_height: int, 
                  page_width_pt: float, page_height_pt: float) -> Tuple[float, float]:
    """
    이미지의 DPI 계산
    
    Args:
        pixel_width: 이미지 픽셀 너비
        pixel_height: 이미지 픽셀 높이
        page_width_pt: 페이지 너비 (포인트)
        page_height_pt: 페이지 높이 (포인트)
        
    Returns:
        (horizontal_dpi, vertical_dpi): 가로/세로 DPI
    """
    # 1 포인트 = 1/72 인치
    page_width_inch = page_width_pt / 72.0
    page_height_inch = page_height_pt / 72.0
    
    if page_width_inch > 0 and page_height_inch > 0:
        h_dpi = pixel_width / page_width_inch
        v_dpi = pixel_height / page_height_inch
        return (h_dpi, v_dpi)
    
    return (0.0, 0.0)


def points_to_mm(points: float) -> float:
    """
    포인트를 밀리미터로 변환
    
    Args:
        points: 포인트 값
        
    Returns:
        밀리미터 값
    """
    # 1 포인트 = 0.352778 mm
    return points * 0.352778


def mm_to_points(mm: float) -> float:
    """
    밀리미터를 포인트로 변환
    
    Args:
        mm: 밀리미터 값
        
    Returns:
        포인트 값
    """
    # 1 mm = 2.834646 포인트
    return mm * 2.834646


def inches_to_points(inches: float) -> float:
    """
    인치를 포인트로 변환
    
    Args:
        inches: 인치 값
        
    Returns:
        포인트 값
    """
    # 1 인치 = 72 포인트
    return inches * 72.0


def points_to_inches(points: float) -> float:
    """
    포인트를 인치로 변환
    
    Args:
        points: 포인트 값
        
    Returns:
        인치 값
    """
    return points / 72.0


def get_paper_size_name(width_pt: float, height_pt: float, 
                        tolerance: float = 2.0) -> Optional[str]:
    """
    포인트 크기로부터 용지 크기 이름 결정
    
    Args:
        width_pt: 너비 (포인트)
        height_pt: 높이 (포인트)
        tolerance: 허용 오차 (포인트)
        
    Returns:
        용지 크기 이름 (A4, Letter 등) 또는 None
    """
    # 일반적인 용지 크기 (포인트 단위)
    paper_sizes = {
        'A0': (2384, 3370),
        'A1': (1684, 2384),
        'A2': (1191, 1684),
        'A3': (842, 1191),
        'A4': (595, 842),
        'A5': (420, 595),
        'A6': (298, 420),
        'Letter': (612, 792),
        'Legal': (612, 1008),
        'Tabloid': (792, 1224),
        'B4': (709, 1001),
        'B5': (499, 709),
    }
    
    # 가로/세로 모두 확인
    for name, (w, h) in paper_sizes.items():
        if (abs(width_pt - w) <= tolerance and abs(height_pt - h) <= tolerance) or \
           (abs(width_pt - h) <= tolerance and abs(height_pt - w) <= tolerance):
            return name
    
    return None


def calculate_ink_coverage(cmyk_values: list) -> float:
    """
    CMYK 값으로부터 잉크 커버리지 계산
    
    Args:
        cmyk_values: [C, M, Y, K] 값 (0-1 또는 0-100)
        
    Returns:
        총 잉크 커버리지 (%)
    """
    # 0-1 범위로 정규화
    normalized = []
    for value in cmyk_values:
        if value > 1:
            normalized.append(value / 100.0)
        else:
            normalized.append(value)
    
    # 총 잉크 커버리지 계산
    total = sum(normalized) * 100
    return min(total, 400)  # 최대 400%


def is_rgb_color(color_space: str) -> bool:
    """
    RGB 색상 공간인지 확인
    
    Args:
        color_space: 색상 공간 이름
        
    Returns:
        RGB 여부
    """
    rgb_spaces = ['RGB', 'sRGB', 'DeviceRGB', 'CalRGB']
    return any(space in color_space for space in rgb_spaces)


def is_cmyk_color(color_space: str) -> bool:
    """
    CMYK 색상 공간인지 확인
    
    Args:
        color_space: 색상 공간 이름
        
    Returns:
        CMYK 여부
    """
    cmyk_spaces = ['CMYK', 'DeviceCMYK', 'CalCMYK']
    return any(space in color_space for space in cmyk_spaces)


def format_file_size(size_bytes: int) -> str:
    """
    파일 크기를 읽기 쉬운 형식으로 변환
    
    Args:
        size_bytes: 바이트 단위 크기
        
    Returns:
        포맷된 문자열 (예: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_bleed_requirements(page_width_mm: float, page_height_mm: float) -> dict:
    """
    페이지 크기에 따른 재단 여백 요구사항 결정
    
    Args:
        page_width_mm: 페이지 너비 (mm)
        page_height_mm: 페이지 높이 (mm)
        
    Returns:
        재단 여백 요구사항 딕셔너리
    """
    # 기본 재단 여백 (mm)
    standard_bleed = 3.0
    
    # 대형 포맷은 더 큰 재단 여백 필요
    if page_width_mm > 420 or page_height_mm > 420:  # A2 이상
        standard_bleed = 5.0
    
    return {
        'minimum': standard_bleed,
        'recommended': standard_bleed + 1.0,
        'unit': 'mm'
    }


def normalize_path(path: Union[str, 'Path']) -> str:
    """
    경로를 정규화
    
    Args:
        path: 파일 경로
        
    Returns:
        정규화된 경로 문자열
    """
    from pathlib import Path
    return str(Path(path).resolve())