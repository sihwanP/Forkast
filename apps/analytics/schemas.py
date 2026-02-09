from ninja import Schema
from typing import List, Optional

class DashboardAnalysisRequest(Schema):
    revenue_today: int
    history_sales: List[str]
    weather: str = "맑음"
    inventory_status: str = "적정"
    local_event: str = "없음"

class StrategyItem(Schema):
    category: str
    icon: str
    title: str
    summary: str
    detail: str
    score: int

class DashboardAnalysisResponse(Schema):
    prediction: int
    analysis: str
    strategies: List[StrategyItem]
    cheer_msg: str

class ChatConsultRequest(Schema):
    question: str

class ChatConsultResponse(Schema):
    answer: str
