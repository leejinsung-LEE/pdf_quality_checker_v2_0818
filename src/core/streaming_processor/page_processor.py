"""Page-level processing utilities"""

import logging
from typing import Dict, Any, List, Optional, Callable
import pikepdf
import fitz


class PageProcessor:
    """Process individual PDF pages"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize page processor
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze_page(self, 
                    page,
                    page_num: int,
                    analyzer_func: Optional[Callable] = None) -> Dict[str, Any]:
        """Analyze a single page
        
        Args:
            page: Page object (pikepdf or fitz)
            page_num: Page number (0-indexed)
            analyzer_func: Optional custom analyzer function
            
        Returns:
            Dictionary with page analysis data
        """
        try:
            # Basic page data
            page_data = self._extract_basic_info(page, page_num)
            
            # Custom analysis
            if analyzer_func:
                try:
                    additional_data = analyzer_func(page)
                    page_data.update(additional_data)
                except Exception as e:
                    self.logger.error(f"Custom analyzer error on page {page_num}: {e}")
                    page_data['analyzer_error'] = str(e)
            
            return page_data
            
        except Exception as e:
            self.logger.error(f"Page {page_num} analysis error: {e}")
            return {'page_num': page_num + 1, 'error': str(e)}
    
    def check_page(self,
                  page,
                  page_num: int,
                  checker_func: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Check page for quality issues
        
        Args:
            page: Page object
            page_num: Page number (0-indexed)
            checker_func: Optional custom checker function
            
        Returns:
            List of issues found
        """
        try:
            issues = []
            
            # Basic checks
            basic_issues = self._perform_basic_checks(page, page_num)
            issues.extend(basic_issues)
            
            # Custom checks
            if checker_func:
                try:
                    custom_issues = checker_func(page, page_num)
                    if custom_issues:
                        issues.extend(custom_issues)
                except Exception as e:
                    self.logger.error(f"Custom checker error on page {page_num}: {e}")
                    issues.append({
                        'page': page_num + 1,
                        'type': 'checker_error',
                        'message': str(e)
                    })
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Page {page_num} check error: {e}")
            return [{'page': page_num + 1, 'error': str(e)}]
    
    def _extract_basic_info(self, page, page_num: int) -> Dict[str, Any]:
        """Extract basic page information
        
        Args:
            page: Page object
            page_num: Page number
            
        Returns:
            Basic page information
        """
        info = {'page_num': page_num + 1}
        
        try:
            # Handle pikepdf page
            if hasattr(page, 'MediaBox'):
                info.update({
                    'width': float(page.MediaBox[2] - page.MediaBox[0]),
                    'height': float(page.MediaBox[3] - page.MediaBox[1]),
                    'rotation': page.get('/Rotate', 0)
                })
            
            # Handle fitz page
            elif hasattr(page, 'rect'):
                rect = page.rect
                info.update({
                    'width': rect.width,
                    'height': rect.height,
                    'rotation': page.rotation
                })
                
        except Exception as e:
            self.logger.debug(f"Could not extract page info: {e}")
            
        return info
    
    def _perform_basic_checks(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Perform basic quality checks on page
        
        Args:
            page: Page object
            page_num: Page number
            
        Returns:
            List of basic issues found
        """
        issues = []
        
        try:
            # Check page size
            if hasattr(page, 'MediaBox'):
                width = float(page.MediaBox[2] - page.MediaBox[0])
                height = float(page.MediaBox[3] - page.MediaBox[1])
                
                # Check for unusual dimensions
                if width < 100 or height < 100:
                    issues.append({
                        'page': page_num + 1,
                        'type': 'dimension',
                        'message': f'Very small page size: {width:.1f}x{height:.1f}'
                    })
                    
                if width > 5000 or height > 5000:
                    issues.append({
                        'page': page_num + 1,
                        'type': 'dimension',
                        'message': f'Very large page size: {width:.1f}x{height:.1f}'
                    })
                    
        except Exception as e:
            self.logger.debug(f"Basic check error: {e}")
            
        return issues