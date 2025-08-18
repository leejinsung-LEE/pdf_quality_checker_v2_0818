# src/utils/alarm_manager/models.py
"""
알람 관련 데이터 모델 및 기록 관리
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque


class NotificationHistory:
    """알림 기록 관리"""
    
    def __init__(self, max_items: int = 1000):
        """
        초기화
        
        Args:
            max_items: 최대 기록 개수
        """
        self.max_items = max_items
        self.history: deque = deque(maxlen=max_items)
        
    def add(self, notification: Dict[str, Any]):
        """
        알림 기록 추가
        
        Args:
            notification: 알림 데이터
        """
        notification['timestamp'] = datetime.now().isoformat()
        self.history.append(notification)
        
    def get_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        최근 알림 가져오기
        
        Args:
            count: 가져올 개수
            
        Returns:
            최근 알림 목록
        """
        return list(self.history)[-count:]
        
    def clear(self):
        """기록 초기화"""
        self.history.clear()
        
    def save_to_file(self, filepath: Path):
        """
        파일로 저장
        
        Args:
            filepath: 저장할 파일 경로
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(list(self.history), f, ensure_ascii=False, indent=2)
            
    def load_from_file(self, filepath: Path):
        """
        파일에서 로드
        
        Args:
            filepath: 로드할 파일 경로
        """
        if not filepath.exists():
            return
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = deque(data, maxlen=self.max_items)
        except Exception as e:
            logging.warning(f"알림 기록 로드 실패: {e}")
            
    def get_statistics(self) -> Dict[str, Any]:
        """
        통계 정보 반환
        
        Returns:
            통계 딕셔너리
        """
        if not self.history:
            return {
                'total': 0,
                'by_type': {},
                'recent_hour': 0,
                'recent_day': 0
            }
            
        now = datetime.now()
        hour_ago = (now.timestamp() - 3600) * 1000
        day_ago = (now.timestamp() - 86400) * 1000
        
        by_type = {}
        recent_hour = 0
        recent_day = 0
        
        for item in self.history:
            # 타입별 카운트
            condition_type = item.get('condition_type', 'unknown')
            by_type[condition_type] = by_type.get(condition_type, 0) + 1
            
            # 시간별 카운트
            timestamp = datetime.fromisoformat(item['timestamp']).timestamp() * 1000
            if timestamp > hour_ago:
                recent_hour += 1
            if timestamp > day_ago:
                recent_day += 1
                
        return {
            'total': len(self.history),
            'by_type': by_type,
            'recent_hour': recent_hour,
            'recent_day': recent_day
        }


class NotificationData:
    """알림 데이터 모델"""
    
    def __init__(self, 
                 condition_type: str,
                 title: str,
                 message: str,
                 value: Any = None,
                 severity: str = 'info',
                 metadata: Optional[Dict[str, Any]] = None):
        """
        초기화
        
        Args:
            condition_type: 조건 유형
            title: 제목
            message: 메시지
            value: 관련 값
            severity: 심각도 (info, warning, error, critical)
            metadata: 추가 메타데이터
        """
        self.condition_type = condition_type
        self.title = title
        self.message = message
        self.value = value
        self.severity = severity
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'condition_type': self.condition_type,
            'title': self.title,
            'message': self.message,
            'value': self.value,
            'severity': self.severity,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationData':
        """딕셔너리에서 생성"""
        obj = cls(
            condition_type=data['condition_type'],
            title=data['title'],
            message=data['message'],
            value=data.get('value'),
            severity=data.get('severity', 'info'),
            metadata=data.get('metadata', {})
        )
        if 'timestamp' in data:
            obj.timestamp = datetime.fromisoformat(data['timestamp'])
        return obj


class RateLimiter:
    """알림 속도 제한 관리"""
    
    def __init__(self, max_per_minute: int = 10):
        """
        초기화
        
        Args:
            max_per_minute: 분당 최대 알림 수
        """
        self.max_per_minute = max_per_minute
        self.recent_notifications: deque = deque()
        
    def check_limit(self) -> bool:
        """
        속도 제한 확인
        
        Returns:
            제한 내에 있으면 True
        """
        now = datetime.now()
        one_minute_ago = now.timestamp() - 60
        
        # 1분 이상 지난 알림 제거
        while self.recent_notifications and self.recent_notifications[0] < one_minute_ago:
            self.recent_notifications.popleft()
            
        return len(self.recent_notifications) < self.max_per_minute
        
    def add_notification(self):
        """알림 추가"""
        self.recent_notifications.append(datetime.now().timestamp())
        
    def reset(self):
        """초기화"""
        self.recent_notifications.clear()