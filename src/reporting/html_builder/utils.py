# src/reporting/html_builder/utils.py
"""
HTML 보고서 유틸리티 함수
"""

from typing import List, Optional


class ReportUtils:
    """보고서 유틸리티"""
    
    @staticmethod
    def get_category_display_name(category: str) -> str:
        """
        카테고리 표시 이름
        
        Args:
            category: 카테고리 코드
            
        Returns:
            표시용 이름
        """
        category_names = {
            'font_embedding': '🔤 폰트 임베딩',
            'font_type': '🔤 폰트 타입',
            'text_rendering': '📝 텍스트 렌더링',
            'color_space': '🎨 색상 공간',
            'spot_color': '🎨 별색',
            'ink_coverage': '🎨 잉크 사용량',
            'image_quality': '🖼️ 이미지 품질',
            'image_compression': '🖼️ 이미지 압축',
            'page_layout': '📐 페이지 레이아웃',
            'print_production': '🖨️ 인쇄 제작',
            'transparency': '🔍 투명도',
            'overprint': '🖨️ 오버프린트'
        }
        return category_names.get(category, category)
    
    @staticmethod
    def format_pages_text(pages: List[int], max_display: int = 10) -> str:
        """
        페이지 목록을 텍스트로 포맷팅
        
        Args:
            pages: 페이지 번호 목록
            max_display: 최대 표시 개수
            
        Returns:
            포맷팅된 페이지 텍스트
        """
        if not pages:
            return ""
        
        pages_text = f"페이지: {', '.join(map(str, pages[:max_display]))}"
        if len(pages) > max_display:
            pages_text += f" 외 {len(pages) - max_display}개"
        
        return pages_text
    
    @staticmethod
    def get_severity_emoji(severity: str) -> str:
        """
        심각도에 따른 이모지 반환
        
        Args:
            severity: 심각도
            
        Returns:
            이모지
        """
        emoji_map = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        }
        return emoji_map.get(severity.lower(), '❓')
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        파일 크기를 읽기 쉬운 형식으로 변환
        
        Args:
            size_bytes: 바이트 단위 크기
            
        Returns:
            포맷팅된 크기 문자열
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def get_javascript_code() -> str:
        """JavaScript 코드 반환"""
        return """
        <script>
            // 인쇄 기능
            function printReport() {
                window.print();
            }
            
            // 페이지 로드 시 애니메이션
            document.addEventListener('DOMContentLoaded', function() {
                const cards = document.querySelectorAll('.summary-card, .issue-item');
                cards.forEach((card, index) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.transition = 'all 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, index * 50);
                });
            });
            
            // 스크롤 애니메이션
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver(function(entries) {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, observerOptions);
            
            document.querySelectorAll('.section').forEach(section => {
                observer.observe(section);
            });
        </script>
        """