# -*- coding: utf-8 -*-
"""
CRUD (Create, Read, Update, Delete) 작업
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List
import logging

from .models import ProcessHistory
from .database import DatabaseManager


class CRUDOperations:
    """CRUD 작업 관리자"""
    
    def __init__(self, db_manager: DatabaseManager, logger: Optional[logging.Logger] = None):
        """
        초기화
        
        Args:
            db_manager: 데이터베이스 관리자
            logger: 로거
        """
        self.db = db_manager
        self.logger = logger or logging.getLogger(__name__)
    
    def add_history(self, history: ProcessHistory) -> int:
        """
        처리 이력 추가
        
        Args:
            history: 처리 이력
            
        Returns:
            int: 생성된 이력 ID
            
        Raises:
            ValueError: 유효하지 않은 데이터
        """
        # 유효성 검증
        history.validate()
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 현재 시간
            now = datetime.now().isoformat()
            history.created_at = now
            history.updated_at = now
            
            # 메타데이터를 JSON 문자열로 변환
            if history.metadata and isinstance(history.metadata, dict):
                history.metadata = json.dumps(history.metadata, ensure_ascii=False)
            
            # 데이터 삽입
            cursor.execute("""
                INSERT INTO process_history (
                    file_path, file_name, file_size, process_type, status,
                    quality_score, issues_found, issues_fixed, processing_time,
                    error_message, profile_used, user, created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                history.file_path, history.file_name, history.file_size,
                history.process_type, history.status, history.quality_score,
                history.issues_found, history.issues_fixed, history.processing_time,
                history.error_message, history.profile_used, history.user,
                history.created_at, history.updated_at, history.metadata
            ))
            
            history_id = cursor.lastrowid
            conn.commit()
            
            # 일일 통계 업데이트 (Statistics 모듈에서 처리)
            
        self.logger.debug(f"처리 이력 추가: ID={history_id}, 파일={history.file_name}")
        return history_id
    
    def update_history(self, history_id: int, **kwargs) -> bool:
        """
        처리 이력 업데이트
        
        Args:
            history_id: 이력 ID
            **kwargs: 업데이트할 필드들
            
        Returns:
            bool: 성공 여부
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 업데이트 시간 추가
            kwargs['updated_at'] = datetime.now().isoformat()
            
            # 메타데이터 JSON 변환
            if 'metadata' in kwargs and isinstance(kwargs['metadata'], dict):
                kwargs['metadata'] = json.dumps(kwargs['metadata'], ensure_ascii=False)
            
            # UPDATE 쿼리 생성
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            values = list(kwargs.values()) + [history_id]
            
            cursor.execute(f"""
                UPDATE process_history 
                SET {set_clause}
                WHERE id = ?
            """, values)
            
            success = cursor.rowcount > 0
            conn.commit()
            
        if success:
            self.logger.debug(f"처리 이력 업데이트: ID={history_id}")
        return success
    
    def get_history(self, history_id: int) -> Optional[ProcessHistory]:
        """
        특정 이력 조회
        
        Args:
            history_id: 이력 ID
            
        Returns:
            ProcessHistory: 처리 이력
        """
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM process_history WHERE id = ?
            """, (history_id,))
            
            row = cursor.fetchone()
            
        if row:
            data = dict(row)
            # JSON 문자열을 딕셔너리로 변환
            if data.get('metadata'):
                try:
                    data['metadata'] = json.loads(data['metadata'])
                except:
                    pass
            return ProcessHistory.from_dict(data)
        return None
    
    def get_recent_history(self, limit: int = 100, 
                          status: Optional[str] = None,
                          process_type: Optional[str] = None) -> List[ProcessHistory]:
        """
        최근 이력 조회
        
        Args:
            limit: 조회 개수
            status: 상태 필터
            process_type: 처리 유형 필터
            
        Returns:
            List[ProcessHistory]: 처리 이력 목록
        """
        with self.db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 쿼리 생성
            query = "SELECT * FROM process_history WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
                
            if process_type:
                query += " AND process_type = ?"
                params.append(process_type)
                
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
        histories = []
        for row in rows:
            data = dict(row)
            if data.get('metadata'):
                try:
                    data['metadata'] = json.loads(data['metadata'])
                except:
                    pass
            histories.append(ProcessHistory.from_dict(data))
            
        return histories
    
    def delete_history(self, history_id: int) -> bool:
        """
        특정 이력 삭제
        
        Args:
            history_id: 이력 ID
            
        Returns:
            bool: 성공 여부
        """
        rows_affected = self.db.execute(
            "DELETE FROM process_history WHERE id = ?",
            (history_id,)
        )
        
        if rows_affected > 0:
            self.logger.debug(f"처리 이력 삭제: ID={history_id}")
            return True
        return False
    
    def get_history_count(self, **filters) -> int:
        """
        이력 개수 조회
        
        Args:
            **filters: 필터 조건
            
        Returns:
            int: 이력 개수
        """
        query = "SELECT COUNT(*) FROM process_history WHERE 1=1"
        params = []
        
        for key, value in filters.items():
            if value is not None:
                query += f" AND {key} = ?"
                params.append(value)
        
        result = self.db.fetchone(query, tuple(params))
        return result[0] if result else 0