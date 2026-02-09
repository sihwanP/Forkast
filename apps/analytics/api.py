from ninja import Router
from .schemas import (
    DashboardAnalysisRequest, DashboardAnalysisResponse,
    ChatConsultRequest, ChatConsultResponse
)
from .services import generate_dashboard_analysis, consult_ai

router = Router(tags=["Analytics"])

@router.post("/analyze", response=DashboardAnalysisResponse)
def analyze_dashboard(request, payload: DashboardAnalysisRequest):
    """
    Generate comprehensive dashboard analysis using Gemini AI.
    Inputs: Sales data, weather, inventory, events.
    Outputs: Prediction, Analysis text, Strategies, Cheer message.
    """
    sales_data_dict = {
        'revenue': payload.revenue_today,
        'history': payload.history_sales
    }
    
    result = generate_dashboard_analysis(
        sales_data=sales_data_dict,
        weather_data=payload.weather,
        inventory_data=payload.inventory_status,
        event_data=payload.local_event
    )
    return result

@router.post("/consult", response=ChatConsultResponse)
def chat_consult(request, payload: ChatConsultRequest):
    """
    Ask a question to the AI consultant.
    """
    answer_text = consult_ai(payload.question)
    if not answer_text:
        return {"answer": "죄송합니다. 현재 AI 서버 연결이 원활하지 않습니다. 잠시 후 다시 시도해주세요."}
    return {"answer": answer_text}
