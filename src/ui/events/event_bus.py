# src/ui/events/event_bus.py
"""
이벤트 버스 시스템

중앙 집중식 이벤트 관리 시스템으로 컴포넌트 간 느슨한 결합을 제공합니다.
"""

import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
import weakref
from functools import lru_cache

from .event_types import EventType, EventPriority


@dataclass
class Event:
    """이벤트 데이터 클래스"""
    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return f"Event({self.type.value}, source={self.source}, data={self.data})"


class EventBus:
    """
    중앙 이벤트 버스
    
    싱글톤 패턴으로 구현된 이벤트 버스로, 
    애플리케이션 전체에서 하나의 인스턴스만 사용됩니다.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """싱글톤 인스턴스 생성"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """이벤트 버스 초기화"""
        if self._initialized:
            return
            
        self._listeners: Dict[EventType, List[weakref.ref]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 100
        self._debug_mode = False
        self._lock = Lock()
        self.logger = logging.getLogger(__name__)
        self._initialized = True
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None], 
                  weak: bool = True) -> None:
        """
        이벤트 구독
        
        Args:
            event_type: 구독할 이벤트 타입
            callback: 이벤트 발생 시 호출될 콜백 함수
            weak: 약한 참조 사용 여부 (기본: True)
        """
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            
            # 약한 참조 또는 강한 참조 저장
            if weak:
                # 약한 참조 사용 (메모리 누수 방지)
                ref = weakref.ref(callback, self._create_cleanup_callback(event_type))
                self._listeners[event_type].append(ref)
            else:
                # 강한 참조 사용 (특별한 경우에만)
                self._listeners[event_type].append(lambda: callback)
            
            if self._debug_mode:
                self.logger.debug(f"Subscribed to {event_type.value}: {callback}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        이벤트 구독 해제
        
        Args:
            event_type: 구독 해제할 이벤트 타입
            callback: 구독 해제할 콜백 함수
        """
        with self._lock:
            if event_type not in self._listeners:
                return
            
            # 약한 참조 리스트에서 콜백 제거
            self._listeners[event_type] = [
                ref for ref in self._listeners[event_type]
                if ref() is not None and ref() != callback
            ]
            
            # 빈 리스트는 제거
            if not self._listeners[event_type]:
                del self._listeners[event_type]
            
            if self._debug_mode:
                self.logger.debug(f"Unsubscribed from {event_type.value}: {callback}")
    
    def publish(self, event: Event) -> None:
        """
        이벤트 발행
        
        Args:
            event: 발행할 이벤트
        """
        # 이벤트 히스토리에 추가
        self._add_to_history(event)
        
        # 디버그 모드에서 로깅
        if self._debug_mode:
            self.logger.debug(f"Publishing event: {event}")
        
        # 해당 이벤트 타입의 리스너들에게 전달
        listeners = self._get_listeners(event.type)
        
        # 우선순위에 따라 처리
        if event.priority == EventPriority.CRITICAL:
            # 즉시 처리 (동기)
            self._dispatch_to_listeners(event, listeners)
        else:
            # 일반 처리 (나중에 비동기 지원 추가 가능)
            self._dispatch_to_listeners(event, listeners)
    
    def emit(self, event_type: EventType, data: Dict[str, Any] = None, 
             source: str = "", priority: EventPriority = EventPriority.NORMAL) -> None:
        """
        간편한 이벤트 발행 메서드
        
        Args:
            event_type: 이벤트 타입
            data: 이벤트 데이터
            source: 이벤트 소스
            priority: 이벤트 우선순위
        """
        event = Event(
            type=event_type,
            data=data or {},
            source=source,
            priority=priority
        )
        self.publish(event)
    
    def _dispatch_to_listeners(self, event: Event, listeners: List[Callable]) -> None:
        """리스너들에게 이벤트 전달"""
        for callback in listeners:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event.type.value}: {e}")
                if self._debug_mode:
                    import traceback
                    self.logger.error(traceback.format_exc())
    
    def _get_listeners(self, event_type: EventType) -> List[Callable]:
        """특정 이벤트 타입의 리스너 목록 반환"""
        with self._lock:
            if event_type not in self._listeners:
                return []
            
            # 죽은 약한 참조 정리하고 살아있는 콜백 반환
            listeners = []
            dead_refs = []
            
            for ref in self._listeners[event_type]:
                try:
                    # 약한 참조 확인
                    callback = ref()
                    if callback is not None:
                        listeners.append(callback)
                    else:
                        dead_refs.append(ref)
                except TypeError:
                    # 강한 참조 (lambda로 래핑된 경우)
                    listeners.append(ref)
            
            # 죽은 참조 제거
            for dead_ref in dead_refs:
                try:
                    self._listeners[event_type].remove(dead_ref)
                except ValueError:
                    pass
            
            return listeners
    
    def _create_cleanup_callback(self, event_type: EventType) -> Callable:
        """약한 참조가 삭제될 때 호출될 정리 콜백 생성"""
        def cleanup(ref):
            with self._lock:
                if event_type in self._listeners:
                    try:
                        self._listeners[event_type].remove(ref)
                        if not self._listeners[event_type]:
                            del self._listeners[event_type]
                    except (ValueError, KeyError):
                        pass
        return cleanup
    
    def _add_to_history(self, event: Event) -> None:
        """이벤트 히스토리에 추가"""
        with self._lock:
            self._event_history.append(event)
            # 최대 크기 유지
            if len(self._event_history) > self._max_history_size:
                self._event_history.pop(0)
    
    def get_history(self, event_type: Optional[EventType] = None, 
                   limit: int = 10) -> List[Event]:
        """
        이벤트 히스토리 조회
        
        Args:
            event_type: 특정 타입만 필터링 (None이면 전체)
            limit: 반환할 최대 개수
        
        Returns:
            이벤트 리스트
        """
        with self._lock:
            if event_type:
                filtered = [e for e in self._event_history if e.type == event_type]
            else:
                filtered = self._event_history.copy()
            
            return filtered[-limit:]
    
    def clear_history(self) -> None:
        """이벤트 히스토리 초기화"""
        with self._lock:
            self._event_history.clear()
    
    def set_debug_mode(self, enabled: bool) -> None:
        """디버그 모드 설정"""
        self._debug_mode = enabled
        if enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
    
    def get_listener_count(self, event_type: Optional[EventType] = None) -> int:
        """
        리스너 수 조회
        
        Args:
            event_type: 특정 타입의 리스너 수 (None이면 전체)
        
        Returns:
            리스너 수
        """
        with self._lock:
            if event_type:
                return len(self._get_listeners(event_type))
            else:
                return sum(len(self._get_listeners(et)) for et in self._listeners.keys())
    
    def reset(self) -> None:
        """이벤트 버스 초기화 (테스트용)"""
        with self._lock:
            self._listeners.clear()
            self._event_history.clear()
            if self._debug_mode:
                self.logger.debug("Event bus reset")


# 전역 이벤트 버스 인스턴스 (편의를 위한 싱글톤 접근)
@lru_cache(maxsize=1)
def get_event_bus() -> EventBus:
    """전역 이벤트 버스 인스턴스 반환"""
    return EventBus()


# 데코레이터: 메서드를 이벤트 핸들러로 자동 등록
def event_handler(event_type: EventType):
    """
    이벤트 핸들러 데코레이터
    
    사용 예:
        @event_handler(EventType.FILE_OPEN)
        def on_file_open(self, event: Event):
            print(f"File opened: {event.data}")
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # 첫 초기화 시 이벤트 버스에 등록
            if not hasattr(self, '_event_handlers_registered'):
                self._event_handlers_registered = set()
            
            handler_key = (event_type, func.__name__)
            if handler_key not in self._event_handlers_registered:
                event_bus = get_event_bus()
                event_bus.subscribe(event_type, lambda e: func(self, e))
                self._event_handlers_registered.add(handler_key)
            
            return func(self, *args, **kwargs)
        
        wrapper._event_type = event_type
        return wrapper
    return decorator