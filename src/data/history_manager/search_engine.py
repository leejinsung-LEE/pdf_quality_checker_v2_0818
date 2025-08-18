# -*- coding: utf-8 -*-
"""
이력 검색 및 필터링 엔진
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional
import logging

from .models import ProcessHistory
from .database import DatabaseManager


class SearchEngine:
    """검색 엔진"""
    
    def __init__(self, db_manager: DatabaseManager, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            db_manager: 데이터베이스 관리자
            logger: 로거
        """
        self.db = db_manager
        self.logger = logger or logging.getLogger(__name__)
    
    def search_history(self, 
                       file_name: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       min_quality_score: Optional[float] = None,
                       max_quality_score: Optional[float] = None,
                       status: Optional[str] = None,
                       process_type: Optional[str] = None,
                       profile_used: Optional[str] = None,
                       user: Optional[str] = None,
                       limit: Optional[int] = None) -> List[ProcessHistory]:
        """
        이력 검색
        
        Args:
            file_name: 파일명 (부분 일치)
            start_date: 시작 날짜
            end_date: 종료 날짜
            min_quality_score: 최소 품질 점수
            max_quality_score: 최대 품질 점수
            status: 처리 상태
            process_type: 처리 유형
            profile_used: 사용된 프로파일
            user: 사용자
            limit: 최대 결과 수
            
        Returns:
            List[ProcessHistory]: 검색 결과
        """
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM process_history WHERE 1=1"
            params = []
            
            # 파일명 검색 (부분 일치)
            if file_name:
                query += " AND file_name LIKE ?"
                params.append(f"%{file_name}%")
            
            # 날짜 범위
            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND created_at <= ?"
                params.append(end_date.isoformat())
            
            # 품질 점수 범위
            if min_quality_score is not None:
                query += " AND quality_score >= ?"
                params.append(min_quality_score)
            
            if max_quality_score is not None:
                query += " AND quality_score <= ?"
                params.append(max_quality_score)
            
            # 상태 필터
            if status:
                query += " AND status = ?"
                params.append(status)
            
            # 처리 유형 필터
            if process_type:
                query += " AND process_type = ?"
                params.append(process_type)
            
            # 프로파일 필터
            if profile_used:
                query += " AND profile_used = ?"
                params.append(profile_used)
            
            # 사용자 필터
            if user:
                query += " AND user = ?"
                params.append(user)
            
            # 정렬 및 제한
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        histories = []
        for row in rows:
            data = dict(row)
            if data.get('metadata'):
                try:
                    data['metadata'] = json.loads(data['metadata'])
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    self.logger.warning(f"메타데이터 파싱 실패: {e}")
                    data['metadata'] = {}
            histories.append(ProcessHistory.from_dict(data))
        
        self.logger.debug(f"검색 결과: {len(histories)}개 이력 발견")
        return histories
    
    def search_by_quality_issues(self,
                                 min_issues: Optional[int] = None,
                                 max_issues: Optional[int] = None,
                                 has_fixed_issues: Optional[bool] = None) -> List[ProcessHistory]:
        """
        품질 이슈 기준 검색
        
        Args:
            min_issues: 최소 이슈 수
            max_issues: 최대 이슈 수
            has_fixed_issues: 수정된 이슈가 있는지 여부
            
        Returns:
            List[ProcessHistory]: 검색 결과
        """
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM process_history WHERE 1=1"
            params = []
            
            if min_issues is not None:
                query += " AND issues_found >= ?"
                params.append(min_issues)
            
            if max_issues is not None:
                query += " AND issues_found <= ?"
                params.append(max_issues)
            
            if has_fixed_issues is not None:
                if has_fixed_issues:
                    query += " AND issues_fixed > 0"
                else:
                    query += " AND issues_fixed = 0"
            
            query += " ORDER BY issues_found DESC, created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        histories = []
        for row in rows:
            data = dict(row)
            if data.get('metadata'):
                try:
                    data['metadata'] = json.loads(data['metadata'])
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    self.logger.warning(f"메타데이터 파싱 실패: {e}")
                    data['metadata'] = {}
            histories.append(ProcessHistory.from_dict(data))
        
        return histories
    
    def search_failed_processes(self,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[ProcessHistory]:
        """
        실패한 처리 검색
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            List[ProcessHistory]: 실패한 처리 목록
        """
        return self.search_history(
            status='failed',
            start_date=start_date,
            end_date=end_date
        )
    
    def search_by_processing_time(self,
                                  min_time: Optional[float] = None,
                                  max_time: Optional[float] = None) -> List[ProcessHistory]:
        """
        처리 시간 기준 검색
        
        Args:
            min_time: 최소 처리 시간 (초)
            max_time: 최대 처리 시간 (초)
            
        Returns:
            List[ProcessHistory]: 검색 결과
        """
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM process_history WHERE 1=1"
            params = []
            
            if min_time is not None:
                query += " AND processing_time >= ?"
                params.append(min_time)
            
            if max_time is not None:
                query += " AND processing_time <= ?"
                params.append(max_time)
            
            query += " ORDER BY processing_time DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        histories = []
        for row in rows:
            data = dict(row)
            if data.get('metadata'):
                try:
                    data['metadata'] = json.loads(data['metadata'])
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    self.logger.warning(f"메타데이터 파싱 실패: {e}")
                    data['metadata'] = {}
            histories.append(ProcessHistory.from_dict(data))
        
        return histories
    
    def get_unique_values(self, column: str) -> List[str]:
        """
        특정 컬럼의 고유 값 조회
        
        Args:
            column: 컬럼 이름
            
        Returns:
            List[str]: 고유 값 목록
        """
        # SQL 인젝션 방지를 위한 컬럼 이름 검증
        allowed_columns = ['process_type', 'status', 'profile_used', 'user']
        if column not in allowed_columns:
            raise ValueError(f"허용되지 않은 컬럼: {column}")
        
        query = f"SELECT DISTINCT {column} FROM process_history WHERE {column} IS NOT NULL"
        results = self.db.fetchall(query)
        
        return [row[0] for row in results if row[0]]