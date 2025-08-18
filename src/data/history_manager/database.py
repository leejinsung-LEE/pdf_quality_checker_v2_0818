# -*- coding: utf-8 -*-
"""
데이터베이스 연결 및 초기화 관리
"""

import sqlite3
from pathlib import Path
import logging
from typing import Optional
from contextlib import contextmanager


class DatabaseManager:
    """데이터베이스 관리자"""
    
    def __init__(self, db_path: Optional[Path] = None, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
            logger: 로거
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # DB 경로 설정
        if db_path is None:
            db_dir = Path("data/database")
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "history.db"
            
        self.db_path = db_path
        
        # 데이터베이스 초기화
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 처리 이력 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS process_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    process_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    quality_score REAL,
                    issues_found INTEGER DEFAULT 0,
                    issues_fixed INTEGER DEFAULT 0,
                    processing_time REAL DEFAULT 0.0,
                    error_message TEXT,
                    profile_used TEXT,
                    user TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # 인덱스 생성
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON process_history(created_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON process_history(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_name 
                ON process_history(file_name)
            """)
            
            # 통계 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_statistics (
                    date DATE PRIMARY KEY,
                    total_processed INTEGER DEFAULT 0,
                    total_succeeded INTEGER DEFAULT 0,
                    total_failed INTEGER DEFAULT 0,
                    total_issues_found INTEGER DEFAULT 0,
                    total_issues_fixed INTEGER DEFAULT 0,
                    average_quality_score REAL,
                    total_processing_time REAL DEFAULT 0.0,
                    total_file_size INTEGER DEFAULT 0
                )
            """)
            
            conn.commit()
            
        self.logger.info(f"작업 이력 데이터베이스 초기화 완료: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """
        데이터베이스 연결 컨텍스트 매니저
        
        Yields:
            sqlite3.Connection: 데이터베이스 연결
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_cursor(self, row_factory=None):
        """
        데이터베이스 커서 컨텍스트 매니저
        
        Args:
            row_factory: Row factory (예: sqlite3.Row)
            
        Yields:
            sqlite3.Cursor: 데이터베이스 커서
        """
        with self.get_connection() as conn:
            if row_factory:
                conn.row_factory = row_factory
            cursor = conn.cursor()
            yield cursor
            conn.commit()
    
    def execute(self, query: str, params: tuple = ()):
        """
        쿼리 실행
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            int: 영향받은 행 수
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def fetchone(self, query: str, params: tuple = ()):
        """
        단일 행 조회
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            tuple: 조회 결과
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetchall(self, query: str, params: tuple = ()):
        """
        모든 행 조회
        
        Args:
            query: SQL 쿼리
            params: 쿼리 파라미터
            
        Returns:
            list: 조회 결과 목록
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()