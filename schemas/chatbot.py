from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class ChartItem(BaseModel):
    label: str
    value: int
    candidate_id: Optional[int] = None
    email: Optional[str] = None


class ChartSummary(BaseModel):
    total_candidates: Optional[int] = 0
    total_resumes: Optional[int] = 0
    most_active_candidate: Optional[str] = None
    max_resumes: Optional[int] = 0
    average_resumes_per_candidate: Optional[float] = 0.0


class ChartData(BaseModel):
    chart_type: str = "bar"
    title: str = "Candidate Resumes"
    items: List[ChartItem] = []
    summary: Optional[ChartSummary] = None


class ChatMessageResponse(BaseModel):
    session_id: str
    reply: str
    chart_data: Optional[ChartData] = None
    tool_called: Optional[str] = None


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    timestamp: str
    chart_data: Optional[ChartData] = None


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatHistoryItem]
