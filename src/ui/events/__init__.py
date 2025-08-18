# src/ui/events/__init__.py
"""
이벤트 시스템 모듈

중앙 집중식 이벤트 버스를 통한 컴포넌트 간 통신을 제공합니다.
"""

from .event_types import EventType, EventPriority, EVENT_CATEGORIES, get_event_category
from .event_bus import Event, EventBus, get_event_bus, event_handler

# 편의를 위한 전역 인스턴스
event_bus = get_event_bus()

__all__ = [
    # 타입 정의
    'EventType',
    'EventPriority', 
    'EVENT_CATEGORIES',
    'get_event_category',
    
    # 이벤트 버스
    'Event',
    'EventBus',
    'get_event_bus',
    'event_bus',
    
    # 데코레이터
    'event_handler',
]

# 모듈 정보
__version__ = "1.0.0"
__author__ = "PDF Quality Checker Team"
__description__ = "Event Bus System for GUI Architecture"