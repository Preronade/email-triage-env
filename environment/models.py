from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PriorityLevel(str, Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class Category(str, Enum):
    URGENT = "urgent"
    REGULAR = "regular"
    INFORMATIONAL = "informational"

class ActionType(str, Enum):
    PRIORITIZE_HIGH = "prioritize_high"
    PRIORITIZE_NORMAL = "prioritize_normal"
    PRIORITIZE_LOW = "prioritize_low"
    CATEGORIZE_URGENT = "categorize_urgent"
    CATEGORIZE_REGULAR = "categorize_regular"
    CATEGORIZE_INFORMATIONAL = "categorize_informational"
    DELEGATE = "delegate"
    ARCHIVE = "archive"
    REQUEST_INFO = "request_info"

class Email(BaseModel):
    id: str
    from_address: str
    subject: str
    body: str
    received_at: datetime
    has_attachment: bool = False
    thread_length: int = 1
    priority_hints: List[str] = Field(default_factory=list)

class Observation(BaseModel):
    current_email: Email
    inbox_queue: int
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    time_remaining: float = 1.0

class Action(BaseModel):
    type: ActionType
    reasoning: Optional[str] = None
    confidence: float = 1.0

class Reward(BaseModel):
    value: float
    breakdown: Dict[str, float] = Field(default_factory=dict)
    terminal: bool = False
