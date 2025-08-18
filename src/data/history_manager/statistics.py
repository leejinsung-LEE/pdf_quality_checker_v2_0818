# -*- coding: utf-8 -*-
"""
통계 계산 및 집계
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from .models import ProcessHistory, ProcessStatus
from .database import DatabaseManager


class StatisticsManager:
    """통계 관리자"""
    
    def __init__(self, db_manager: DatabaseManager, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            db_manager: 데이터베이스 관리자
            logger: 로거
        """
        self.db = db_manager
        self.logger = logger or logging.getLogger(__name__)
    
    def get_statistics(self, 
                       period: str = "day",
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        통계 조회
        
        Args:
            period: 기간 (day, week, month, year)
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            Dict: 통계 데이터
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 기본 날짜 설정
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                if period == "day":
                    start_date = end_date - timedelta(days=1)
                elif period == "week":
                    start_date = end_date - timedelta(weeks=1)
                elif period == "month":
                    start_date = end_date - timedelta(days=30)
                elif period == "year":
                    start_date = end_date - timedelta(days=365)
                else:
                    start_date = end_date - timedelta(days=7)
            
            # 전체 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_processed,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as total_succeeded,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as total_failed,
                    SUM(issues_found) as total_issues_found,
                    SUM(issues_fixed) as total_issues_fixed,
                    AVG(quality_score) as average_quality_score,
                    SUM(processing_time) as total_processing_time,
                    SUM(file_size) as total_file_size
                FROM process_history
                WHERE created_at BETWEEN ? AND ?
            """, (start_date.isoformat(), end_date.isoformat()))
            
            result = cursor.fetchone()
            
            # 일별 통계 (그래프용)
            if period == "day":
                date_format = "%Y-%m-%d %H:00:00"
                group_by = "strftime('%Y-%m-%d %H:00:00', created_at)"
            elif period in ["week", "month"]:
                date_format = "%Y-%m-%d"
                group_by = "date(created_at)"
            else:  # year
                date_format = "%Y-%m"
                group_by = "strftime('%Y-%m', created_at)"
            
            cursor.execute(f"""
                SELECT 
                    {group_by} as period,
                    COUNT(*) as count,
                    AVG(quality_score) as avg_score
                FROM process_history
                WHERE created_at BETWEEN ? AND ?
                GROUP BY {group_by}
                ORDER BY period
            """, (start_date.isoformat(), end_date.isoformat()))
            
            daily_stats = cursor.fetchall()
            
            # 처리 유형별 통계
            cursor.execute("""
                SELECT 
                    process_type,
                    COUNT(*) as count,
                    AVG(quality_score) as avg_score
                FROM process_history
                WHERE created_at BETWEEN ? AND ?
                GROUP BY process_type
            """, (start_date.isoformat(), end_date.isoformat()))
            
            type_stats = cursor.fetchall()
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'summary': {
                'total_processed': result[0] or 0,
                'total_succeeded': result[1] or 0,
                'total_failed': result[2] or 0,
                'total_issues_found': result[3] or 0,
                'total_issues_fixed': result[4] or 0,
                'average_quality_score': result[5] or 0,
                'total_processing_time': result[6] or 0,
                'total_file_size': result[7] or 0,
                'success_rate': (result[1] / result[0] * 100) if result[0] else 0
            },
            'timeline': [
                {
                    'period': row[0],
                    'count': row[1],
                    'avg_score': row[2]
                } for row in daily_stats
            ],
            'by_type': [
                {
                    'type': row[0],
                    'count': row[1],
                    'avg_score': row[2]
                } for row in type_stats
            ]
        }
    
    def update_daily_statistics(self, history: ProcessHistory):
        """
        일일 통계 업데이트
        
        Args:
            history: 처리 이력
        """
        if history.status != ProcessStatus.COMPLETED.value:
            return
        
        today = datetime.now().date()
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 기존 통계 확인
            cursor.execute("""
                SELECT * FROM daily_statistics WHERE date = ?
            """, (today,))
            
            existing = cursor.fetchone()
            
            if existing:
                # 업데이트
                cursor.execute("""
                    UPDATE daily_statistics SET
                        total_processed = total_processed + 1,
                        total_succeeded = total_succeeded + ?,
                        total_failed = total_failed + ?,
                        total_issues_found = total_issues_found + ?,
                        total_issues_fixed = total_issues_fixed + ?,
                        total_processing_time = total_processing_time + ?,
                        total_file_size = total_file_size + ?
                    WHERE date = ?
                """, (
                    1 if history.status == ProcessStatus.COMPLETED.value else 0,
                    1 if history.status == ProcessStatus.FAILED.value else 0,
                    history.issues_found or 0,
                    history.issues_fixed or 0,
                    history.processing_time or 0,
                    history.file_size or 0,
                    today
                ))
            else:
                # 새로 추가
                cursor.execute("""
                    INSERT INTO daily_statistics (
                        date, total_processed, total_succeeded, total_failed,
                        total_issues_found, total_issues_fixed, 
                        total_processing_time, total_file_size
                    ) VALUES (?, 1, ?, ?, ?, ?, ?, ?)
                """, (
                    today,
                    1 if history.status == ProcessStatus.COMPLETED.value else 0,
                    1 if history.status == ProcessStatus.FAILED.value else 0,
                    history.issues_found or 0,
                    history.issues_fixed or 0,
                    history.processing_time or 0,
                    history.file_size or 0
                ))
            
            # 평균 품질 점수 업데이트
            if history.quality_score:
                cursor.execute("""
                    UPDATE daily_statistics SET
                        average_quality_score = (
                            SELECT AVG(quality_score) 
                            FROM process_history 
                            WHERE date(created_at) = ?
                            AND quality_score IS NOT NULL
                        )
                    WHERE date = ?
                """, (today, today))
            
            conn.commit()
    
    def get_top_issues(self, limit: int = 10, days: int = 30) -> list:
        """
        가장 많이 발생한 이슈 조회
        
        Args:
            limit: 조회 개수
            days: 최근 일수
            
        Returns:
            list: 이슈 목록
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT 
                COUNT(*) as count,
                AVG(issues_found) as avg_issues,
                AVG(quality_score) as avg_score
            FROM process_history
            WHERE created_at >= ?
            AND issues_found > 0
            GROUP BY DATE(created_at)
            ORDER BY count DESC
            LIMIT ?
        """
        
        results = self.db.fetchall(query, (cutoff_date.isoformat(), limit))
        
        return [
            {
                'count': row[0],
                'avg_issues': row[1],
                'avg_score': row[2]
            }
            for row in results
        ]
    
    def get_performance_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        성능 메트릭 조회
        
        Args:
            days: 최근 일수
            
        Returns:
            Dict: 성능 메트릭
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT 
                AVG(processing_time) as avg_time,
                MIN(processing_time) as min_time,
                MAX(processing_time) as max_time,
                AVG(file_size) as avg_size,
                COUNT(*) as total_files
            FROM process_history
            WHERE created_at >= ?
            AND status = 'completed'
        """
        
        result = self.db.fetchone(query, (cutoff_date.isoformat(),))
        
        if result:
            return {
                'avg_processing_time': result[0] or 0,
                'min_processing_time': result[1] or 0,
                'max_processing_time': result[2] or 0,
                'avg_file_size': result[3] or 0,
                'total_files': result[4] or 0,
                'throughput': (result[4] / days) if days > 0 else 0  # 일평균 처리량
            }
        
        return {
            'avg_processing_time': 0,
            'min_processing_time': 0,
            'max_processing_time': 0,
            'avg_file_size': 0,
            'total_files': 0,
            'throughput': 0
        }