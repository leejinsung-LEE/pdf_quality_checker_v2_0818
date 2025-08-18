"""Main streaming PDF processor"""

import logging
from pathlib import Path
from typing import Iterator, Optional, Callable, Dict, Any
import fitz

from .models import ChunkResult, ProcessingConfig
from .memory_monitor import MemoryMonitor
from .page_processor import PageProcessor
from .chunk_handler import ChunkHandler
from .optimizer import PDFOptimizer
from .adaptive import AdaptiveChunkProcessor


class StreamingPDFProcessor:
    """Stream-based PDF processor for memory-efficient processing"""
    
    def __init__(self,
                 chunk_size: int = 10,
                 max_memory_mb: int = 500,
                 logger: Optional[logging.Logger] = None):
        """Initialize streaming processor
        
        Args:
            chunk_size: Pages per chunk
            max_memory_mb: Maximum memory usage (MB)
            logger: Logger instance
        """
        self.config = ProcessingConfig(
            chunk_size=chunk_size,
            max_memory_mb=max_memory_mb
        )
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.memory_monitor = MemoryMonitor(max_memory_mb, self.logger)
        self.page_processor = PageProcessor(self.logger)
        self.chunk_handler = ChunkHandler(
            chunk_size=chunk_size,
            memory_monitor=self.memory_monitor,
            page_processor=self.page_processor,
            logger=self.logger
        )
        self.optimizer = PDFOptimizer(self.logger)
        self.adaptive_processor = AdaptiveChunkProcessor(base_chunk_size=chunk_size)
        
    def process_pdf_streaming(self,
                             pdf_path: Path,
                             analyzer_func: Optional[Callable] = None,
                             checker_func: Optional[Callable] = None) -> Iterator[ChunkResult]:
        """Process PDF in streaming mode
        
        Args:
            pdf_path: Path to PDF file
            analyzer_func: Page analysis function
            checker_func: Page checking function
            
        Yields:
            ChunkResult for each processed chunk
        """
        self.logger.info(f"Starting streaming processing of {pdf_path}")
        
        # Reset memory baseline
        self.memory_monitor.reset()
        
        # Process chunks
        for chunk_result in self.chunk_handler.process_pdf_chunks(
            pdf_path, analyzer_func, checker_func
        ):
            # Record performance for adaptation
            if self.config.adaptive_chunking:
                self.adaptive_processor.record_performance(
                    chunk_result.pages_processed,
                    chunk_result.processing_time,
                    chunk_result.memory_used
                )
                
                # Adjust chunk size if needed
                if self.adaptive_processor.should_adjust():
                    new_size = self.adaptive_processor.get_optimal_chunk_size()
                    self.chunk_handler.chunk_size = new_size
                    self.logger.info(f"Adjusted chunk size to {new_size}")
            
            yield chunk_result
    
    def process_large_pdf_optimized(self,
                                   pdf_path: Path,
                                   output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Process and optimize large PDF
        
        Args:
            pdf_path: Input PDF path
            output_path: Optional output path for optimized PDF
            
        Returns:
            Processing results
        """
        results = {
            'total_pages': 0,
            'total_issues': 0,
            'chunks_processed': 0,
            'total_memory_used': 0,
            'total_time': 0,
            'optimization': None
        }
        
        try:
            # Get page count
            with fitz.open(pdf_path) as doc:
                results['total_pages'] = doc.page_count
            
            # Process in chunks
            all_issues = []
            total_time = 0
            total_memory = 0
            
            for chunk_result in self.process_pdf_streaming(pdf_path):
                all_issues.extend(chunk_result.issues_found)
                total_time += chunk_result.processing_time
                total_memory = max(total_memory, chunk_result.memory_used)
                results['chunks_processed'] += 1
            
            results['total_issues'] = len(all_issues)
            results['total_time'] = total_time
            results['total_memory_used'] = total_memory
            
            # Optimize if output path provided
            if output_path and self.config.enable_optimization:
                self.logger.info("Starting PDF optimization")
                opt_results = self.optimizer.optimize_file(pdf_path, output_path)
                results['optimization'] = opt_results
            
        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            results['error'] = str(e)
        
        return results
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.memory_monitor.get_memory_usage()
    
    def should_reduce_chunk_size(self) -> bool:
        """Check if chunk size should be reduced"""
        return self.memory_monitor.should_reduce_load()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics
        
        Returns:
            Dictionary with various statistics
        """
        return {
            'memory': self.memory_monitor.get_memory_info(),
            'adaptive': self.adaptive_processor.get_statistics(),
            'optimization': self.optimizer.optimization_stats,
            'config': {
                'chunk_size': self.config.chunk_size,
                'max_memory_mb': self.config.max_memory_mb,
                'adaptive_chunking': self.config.adaptive_chunking,
                'enable_optimization': self.config.enable_optimization
            }
        }
    
    def reset(self):
        """Reset processor state"""
        self.memory_monitor.reset()
        self.adaptive_processor.reset()
        self.optimizer.optimization_stats = {
            'pages_processed': 0,
            'images_optimized': 0,
            'size_before': 0,
            'size_after': 0
        }