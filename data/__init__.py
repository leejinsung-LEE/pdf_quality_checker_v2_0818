# src/data/__init__.py
"""
데이터 관리 모듈

PDF 처리 이력과 통계 데이터를 관리합니다.
"""

from .data_manager import DataManager, get_data_manager

__all__ = ['DataManager', 'get_data_manager']