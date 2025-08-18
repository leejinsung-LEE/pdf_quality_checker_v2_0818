# -*- coding: utf-8 -*-
"""
데이터베이스 성능 최적화 스크립트

인덱스 추가 및 쿼리 최적화를 수행합니다.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional


class DatabaseOptimizer:
    """데이터베이스 최적화 클래스"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
        """
        if db_path is None:
            # 기본 데이터베이스 경로 사용
            data_dir = Path.home() / ".pdf_quality_checker" / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / "history.db"
        else:
            self.db_path = db_path
            
        self.logger = logging.getLogger(__name__)
        
    def add_indexes(self):
        """성능 향상을 위한 인덱스 추가"""
        indexes = [
            # 날짜 범위 검색 최적화
            "CREATE INDEX IF NOT EXISTS idx_history_date ON process_history(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_history_timestamp ON process_history(timestamp)",
            
            # 상태별 검색 최적화
            "CREATE INDEX IF NOT EXISTS idx_history_status ON process_history(status)",
            
            # 파일명 검색 최적화
            "CREATE INDEX IF NOT EXISTS idx_history_filename ON process_history(file_name)",
            
            # 프로파일별 검색 최적화
            "CREATE INDEX IF NOT EXISTS idx_history_profile ON process_history(profile_used)",
            
            # 복합 인덱스 (자주 함께 사용되는 컬럼)
            "CREATE INDEX IF NOT EXISTS idx_history_date_status ON process_history(created_at, status)",
            "CREATE INDEX IF NOT EXISTS idx_history_status_date ON process_history(status, created_at)",
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    self.logger.info(f"인덱스 생성 성공: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    self.logger.error(f"인덱스 생성 실패: {e}")
                    
            # 통계 업데이트 (쿼리 최적화)
            cursor.execute("ANALYZE")
            
            # VACUUM으로 데이터베이스 정리
            cursor.execute("VACUUM")
            
            conn.commit()
            
    def check_indexes(self):
        """현재 인덱스 상태 확인"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 모든 인덱스 조회
            cursor.execute(
                "SELECT name, tbl_name FROM sqlite_master WHERE type='index'"
            )
            
            indexes = cursor.fetchall()
            
            self.logger.info("현재 인덱스 목록:")
            for index_name, table_name in indexes:
                self.logger.info(f"  - {index_name} (테이블: {table_name})")
                
            return indexes
            
    def analyze_query_performance(self, query: str):
        """쿼리 실행 계획 분석"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # EXPLAIN QUERY PLAN 실행
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            
            plan = cursor.fetchall()
            
            self.logger.info("쿼리 실행 계획:")
            for row in plan:
                self.logger.info(f"  {row}")
                
            return plan
            
    def optimize_database(self):
        """데이터베이스 종합 최적화"""
        self.logger.info("데이터베이스 최적화 시작...")
        
        # 1. 인덱스 추가
        self.add_indexes()
        
        # 2. 인덱스 확인
        indexes = self.check_indexes()
        
        # 3. 결과 보고
        self.logger.info(f"최적화 완료: {len(indexes)}개 인덱스")
        
        return True


def optimize_history_database():
    """히스토리 데이터베이스 최적화 실행"""
    optimizer = DatabaseOptimizer()
    return optimizer.optimize_database()


if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 최적화 실행
    optimize_history_database()