# src/processing/pipeline/enums.py
"""
파이프라인 열거형 정의
"""

from enum import Enum


class ProcessingStatus(Enum):
    """처리 상태"""
    WAITING = "waiting"
    ANALYZING = "analyzing"
    CHECKING = "checking"
    FIXING = "fixing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    ERROR = "error"