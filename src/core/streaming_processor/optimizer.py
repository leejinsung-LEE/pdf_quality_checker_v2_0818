"""PDF optimization utilities"""

import fitz
import logging
from pathlib import Path
from typing import Optional, Dict, Any


class PDFOptimizer:
    """Optimize PDF files for size and performance"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize PDF optimizer
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.optimization_stats = {
            'pages_processed': 0,
            'images_optimized': 0,
            'size_before': 0,
            'size_after': 0
        }
    
    def optimize_page(self, page) -> bool:
        """Optimize a single page
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            True if optimization was performed
        """
        optimized = False
        
        try:
            # Optimize images in page
            if self._optimize_page_images(page):
                optimized = True
                
            # Clean up page content
            if self._clean_page_content(page):
                optimized = True
                
            self.optimization_stats['pages_processed'] += 1
            
        except Exception as e:
            self.logger.error(f"Page optimization error: {e}")
            
        return optimized
    
    def _optimize_page_images(self, page) -> bool:
        """Optimize images in a page
        
        Args:
            page: Page object
            
        Returns:
            True if any images were optimized
        """
        optimized = False
        
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(page.parent, xref)
                    
                    # Check if optimization is needed
                    if self._should_optimize_image(pix):
                        # Resize if too large
                        if pix.width > 2000 or pix.height > 2000:
                            pix = self._resize_image(pix, 2000, 2000)
                            optimized = True
                            self.optimization_stats['images_optimized'] += 1
                    
                    # Clean up
                    pix = None
                    
                except Exception as e:
                    self.logger.debug(f"Image optimization skipped: {e}")
                    
        except Exception as e:
            self.logger.debug(f"Image list error: {e}")
            
        return optimized
    
    def _should_optimize_image(self, pix) -> bool:
        """Check if image should be optimized
        
        Args:
            pix: Pixmap object
            
        Returns:
            True if optimization is recommended
        """
        # Large dimensions
        if pix.width > 2000 or pix.height > 2000:
            return True
            
        # High resolution for small images
        if pix.width < 500 and pix.height < 500:
            if pix.xres > 300 or pix.yres > 300:
                return True
                
        return False
    
    def _resize_image(self, pix, max_width: int, max_height: int):
        """Resize image to fit within bounds
        
        Args:
            pix: Pixmap object
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            Resized pixmap
        """
        # Calculate scale factor
        scale_x = max_width / pix.width if pix.width > max_width else 1
        scale_y = max_height / pix.height if pix.height > max_height else 1
        scale = min(scale_x, scale_y)
        
        if scale < 1:
            # Apply transformation
            mat = fitz.Matrix(scale, scale)
            pix = pix.transform(mat)
            
        return pix
    
    def _clean_page_content(self, page) -> bool:
        """Clean unnecessary page content
        
        Args:
            page: Page object
            
        Returns:
            True if content was cleaned
        """
        try:
            # Remove invisible text
            page.clean_contents()
            return True
        except:
            return False
    
    def optimize_file(self,
                     input_path: Path,
                     output_path: Path,
                     **options) -> Dict[str, Any]:
        """Optimize entire PDF file
        
        Args:
            input_path: Input PDF path
            output_path: Output PDF path
            **options: Optimization options
            
        Returns:
            Optimization results
        """
        results = {
            'success': False,
            'input_size': 0,
            'output_size': 0,
            'compression_ratio': 0
        }
        
        try:
            # Get input size
            results['input_size'] = input_path.stat().st_size
            
            # Open and optimize
            doc = fitz.open(input_path)
            
            # Process each page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                self.optimize_page(page)
            
            # Save optimized version
            doc.save(
                output_path,
                garbage=4,  # Maximum garbage collection
                deflate=True,  # Compress streams
                clean=True  # Clean up
            )
            doc.close()
            
            # Get output size
            results['output_size'] = output_path.stat().st_size
            results['compression_ratio'] = (
                1 - results['output_size'] / results['input_size']
            ) * 100
            results['success'] = True
            
            self.logger.info(
                f"Optimized PDF: {results['compression_ratio']:.1f}% reduction"
            )
            
        except Exception as e:
            self.logger.error(f"File optimization error: {e}")
            results['error'] = str(e)
            
        return results