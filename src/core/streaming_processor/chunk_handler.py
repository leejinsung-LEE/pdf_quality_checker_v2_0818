"""Chunk processing handler"""

import time
import logging
from typing import Iterator, Optional, Callable, Dict, Any
from pathlib import Path
import pikepdf

from .models import ChunkResult
from .page_processor import PageProcessor
from .memory_monitor import MemoryMonitor


class ChunkHandler:
    """Handle chunk-based PDF processing"""
    
    def __init__(self,
                 chunk_size: int = 10,
                 memory_monitor: Optional[MemoryMonitor] = None,
                 page_processor: Optional[PageProcessor] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize chunk handler
        
        Args:
            chunk_size: Default pages per chunk
            memory_monitor: Memory monitor instance
            page_processor: Page processor instance
            logger: Logger instance
        """
        self.chunk_size = chunk_size
        self.memory_monitor = memory_monitor or MemoryMonitor()
        self.page_processor = page_processor or PageProcessor()
        self.logger = logger or logging.getLogger(__name__)
        
    def process_pdf_chunks(self,
                          pdf_path: Path,
                          analyzer_func: Optional[Callable] = None,
                          checker_func: Optional[Callable] = None) -> Iterator[ChunkResult]:
        """Process PDF in chunks
        
        Args:
            pdf_path: Path to PDF file
            analyzer_func: Optional page analysis function
            checker_func: Optional page checking function
            
        Yields:
            ChunkResult for each processed chunk
        """
        try:
            with pikepdf.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                self.logger.info(f"Processing {total_pages} pages in chunks of {self.chunk_size}")
                
                # Dynamic chunk size based on memory
                dynamic_chunk_size = self.chunk_size
                
                # Process chunks
                chunk_index = 0
                start_page = 0
                
                while start_page < total_pages:
                    # Adjust chunk size if needed
                    if self.memory_monitor.should_reduce_load():
                        old_size = dynamic_chunk_size
                        dynamic_chunk_size = max(1, dynamic_chunk_size // 2)
                        if old_size != dynamic_chunk_size:
                            self.logger.info(f"Reduced chunk size to {dynamic_chunk_size}")
                    
                    # Calculate end page
                    end_page = min(start_page + dynamic_chunk_size, total_pages)
                    
                    # Process chunk
                    chunk_result = self._process_single_chunk(
                        pdf=pdf,
                        start_page=start_page,
                        end_page=end_page,
                        chunk_index=chunk_index,
                        analyzer_func=analyzer_func,
                        checker_func=checker_func
                    )
                    
                    yield chunk_result
                    
                    # Update counters
                    start_page = end_page
                    chunk_index += 1
                    
                    # Clean up memory
                    self.memory_monitor.cleanup_memory()
                    
                    # Log progress
                    progress = (end_page / total_pages) * 100
                    self.logger.debug(f"Progress: {progress:.1f}% ({end_page}/{total_pages} pages)")
                    
        except Exception as e:
            self.logger.error(f"Chunk processing error: {e}")
            raise
    
    def _process_single_chunk(self,
                            pdf: pikepdf.Pdf,
                            start_page: int,
                            end_page: int,
                            chunk_index: int,
                            analyzer_func: Optional[Callable],
                            checker_func: Optional[Callable]) -> ChunkResult:
        """Process a single chunk of pages
        
        Args:
            pdf: PDF object
            start_page: Starting page index
            end_page: Ending page index
            chunk_index: Chunk index
            analyzer_func: Analysis function
            checker_func: Checking function
            
        Returns:
            ChunkResult with processing results
        """
        start_time = time.time()
        initial_memory = self.memory_monitor.get_memory_usage()
        
        analysis_data = {}
        issues_found = []
        
        # Process each page in chunk
        for page_num in range(start_page, end_page):
            try:
                page = pdf.pages[page_num]
                
                # Analyze page
                if analyzer_func:
                    page_data = self.page_processor.analyze_page(
                        page, page_num, analyzer_func
                    )
                    analysis_data[f'page_{page_num + 1}'] = page_data
                
                # Check page
                if checker_func:
                    page_issues = self.page_processor.check_page(
                        page, page_num, checker_func
                    )
                    issues_found.extend(page_issues)
                    
            except Exception as e:
                self.logger.error(f"Error processing page {page_num}: {e}")
                issues_found.append({
                    'page': page_num + 1,
                    'type': 'processing_error',
                    'message': str(e)
                })
        
        # Calculate metrics
        processing_time = time.time() - start_time
        memory_used = self.memory_monitor.get_memory_usage() - initial_memory
        
        return ChunkResult(
            chunk_index=chunk_index,
            page_range=(start_page, end_page),
            analysis_data=analysis_data,
            issues_found=issues_found,
            memory_used=memory_used,
            processing_time=processing_time
        )
    
    def estimate_chunks(self, pdf_path: Path) -> Dict[str, Any]:
        """Estimate number of chunks needed for PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Estimation information
        """
        try:
            with pikepdf.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                num_chunks = (total_pages + self.chunk_size - 1) // self.chunk_size
                
                return {
                    'total_pages': total_pages,
                    'chunk_size': self.chunk_size,
                    'num_chunks': num_chunks,
                    'estimated_time': num_chunks * 5,  # Rough estimate
                    'estimated_memory': self.chunk_size * 10  # Rough estimate
                }
        except Exception as e:
            self.logger.error(f"Estimation error: {e}")
            return {'error': str(e)}