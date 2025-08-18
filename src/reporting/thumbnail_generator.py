# src/reporting/thumbnail_generator.py
"""
썸네일 생성기

PDF 페이지의 썸네일을 생성하여 보고서에 포함시킵니다.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import base64
import io
import logging

# PDF 및 이미지 처리 라이브러리
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False
    # 경고: PyMuPDF가 설치되지 않았습니다. 썸네일 생성이 비활성화됩니다.

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    # 경고: Pillow가 설치되지 않았습니다. 이미지 처리가 제한됩니다.


class ThumbnailGenerator:
    """PDF 썸네일 생성기"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        썸네일 생성기 초기화
        
        Args:
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        self.enabled = HAS_FITZ and HAS_PIL
        
        if not self.enabled:
            self.logger.warning("썸네일 생성이 비활성화되었습니다")
    
    def generate_for_report(self,
                          pdf_path: Path,
                          problem_pages: List[int],
                          total_pages: int,
                          max_width: int = 300) -> Dict[str, Any]:
        """
        보고서용 썸네일 생성
        
        Args:
            pdf_path: PDF 파일 경로
            problem_pages: 문제가 있는 페이지 번호 목록 (1부터 시작)
            total_pages: 총 페이지 수
            max_width: 썸네일 최대 너비
            
        Returns:
            Dict: 썸네일 데이터
        """
        if not self.enabled:
            return {
                'enabled': False,
                'error': '썸네일 생성기가 비활성화되었습니다'
            }
        
        try:
            result = {
                'enabled': True,
                'cover_page': None,
                'problem_pages': {},
                'total_pages': total_pages
            }
            
            # 표지 페이지 썸네일
            cover_thumb = self.create_thumbnail(pdf_path, 0, max_width)
            if cover_thumb:
                result['cover_page'] = cover_thumb
            
            # 문제 페이지 썸네일 (최대 5개)
            for page_num in problem_pages[:5]:
                if 1 <= page_num <= total_pages:
                    thumb = self.create_thumbnail(pdf_path, page_num - 1, max_width)
                    if thumb:
                        result['problem_pages'][page_num] = thumb
            
            return result
            
        except Exception as e:
            self.logger.error(f"썸네일 생성 실패: {e}")
            return {
                'enabled': False,
                'error': str(e)
            }
    
    def create_thumbnail(self,
                        pdf_path: Union[str, Path],
                        page_num: int = 0,
                        max_width: int = 300) -> Optional[str]:
        """
        단일 페이지 썸네일 생성
        
        Args:
            pdf_path: PDF 파일 경로
            page_num: 페이지 번호 (0부터 시작)
            max_width: 최대 너비
            
        Returns:
            str: Base64 인코딩된 이미지 데이터 URL
        """
        if not self.enabled:
            return None
        
        try:
            # PDF 열기
            doc = fitz.open(str(pdf_path))
            
            # 페이지 범위 확인
            if page_num >= len(doc):
                return None
            
            # 페이지 가져오기
            page = doc[page_num]
            
            # 적절한 해상도 계산 (너비 기준)
            mat = fitz.Matrix(2.0, 2.0)  # 2배 확대
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # PIL 이미지로 변환
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # 크기 조정
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Base64로 인코딩
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            doc.close()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            self.logger.error(f"썸네일 생성 오류 (페이지 {page_num}): {e}")
            return None
    
    def create_page_preview(self,
                          pdf_path: Union[str, Path],
                          page_num: int,
                          max_width: int = 200,
                          highlight_areas: Optional[List[Dict[str, float]]] = None) -> Optional[str]:
        """
        페이지 미리보기 생성 (문제 영역 강조)
        
        Args:
            pdf_path: PDF 파일 경로
            page_num: 페이지 번호 (0부터 시작)
            max_width: 최대 너비
            highlight_areas: 강조할 영역 목록 [{'x': 0, 'y': 0, 'width': 100, 'height': 100}]
            
        Returns:
            str: Base64 인코딩된 이미지 데이터 URL
        """
        if not self.enabled:
            return None
        
        try:
            # PDF 열기
            doc = fitz.open(str(pdf_path))
            page = doc[page_num]
            
            # 해상도 설정
            mat = fitz.Matrix(2.0, 2.0)
            
            # 강조 영역 그리기
            if highlight_areas:
                for area in highlight_areas:
                    rect = fitz.Rect(
                        area['x'], 
                        area['y'], 
                        area['x'] + area['width'], 
                        area['y'] + area['height']
                    )
                    # 빨간 테두리로 강조
                    page.draw_rect(rect, color=(1, 0, 0), width=2)
            
            # 픽스맵 생성
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # PIL 이미지로 변환 및 크기 조정
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Base64 인코딩
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            doc.close()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            self.logger.error(f"페이지 미리보기 생성 오류: {e}")
            return None
    
    def should_generate_thumbnails(self, issues: List[Any]) -> bool:
        """
        썸네일 생성 필요 여부 판단
        
        Args:
            issues: 이슈 목록
            
        Returns:
            bool: 생성 필요 여부
        """
        if not self.enabled:
            return False
        
        # 오류가 있거나 경고가 많으면 생성
        error_count = sum(1 for issue in issues if issue.severity.value == 'error')
        warning_count = sum(1 for issue in issues if issue.severity.value == 'warning')
        
        return error_count > 0 or warning_count > 3
    
    def get_problem_pages(self, issues: List[Any], max_pages: int = 10) -> List[int]:
        """
        문제가 있는 페이지 번호 추출
        
        Args:
            issues: 이슈 목록
            max_pages: 최대 페이지 수
            
        Returns:
            List[int]: 페이지 번호 목록
        """
        problem_pages = set()
        
        for issue in issues:
            if hasattr(issue, 'pages') and issue.pages:
                problem_pages.update(issue.pages)
        
        # 정렬하고 제한
        sorted_pages = sorted(problem_pages)
        return sorted_pages[:max_pages]