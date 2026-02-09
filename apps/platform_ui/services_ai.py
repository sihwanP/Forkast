from django.conf import settings
import logging
import time
import random
import json
import re

logger = logging.getLogger(__name__)

# Models to try in order
AVAILABLE_MODELS = [
    'gemini-2.0-flash',      # Latest fast model
    'gemini-1.5-flash',      # Standard fast model
    'gemini-1.5-pro',        # High intelligence fallback
]

def get_gemini_response(prompt):
    """
    Hybrid Client: Tries google.genai (New) -> Falls back to google.generativeai (Legacy).
    """
    response_text = None
    
    # ---------------------------------------------------------
    # STRATEGY 1: New SDK (google.genai)
    # ---------------------------------------------------------
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        for model_name in AVAILABLE_MODELS:
            try:
                config = types.GenerateContentConfig()
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                if response.text:
                    return response.text
            except Exception as e:
                # 429 logic or continue
                continue
                
    except ImportError:
        logger.warning("google.genai SDK not found or broken. Falling back to Legacy SDK.")
    except Exception as e:
         logger.warning(f"New SDK failed: {e}. Falling back to Legacy SDK.")
    # STRATEGY 2: Legacy SDK (google.generativeai)
    # ---------------------------------------------------------
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=settings.GEMINI_API_KEY)
        
        for model_name in AVAILABLE_MODELS:
            try:
                model = genai_legacy.GenerativeModel(model_name)
                response = model.generate_content(prompt, request_options={'timeout': 15})
                if response.text:
                    return response.text
            except Exception:
                continue
                
    except ImportError:
         logger.error("CRITICAL: Both New and Legacy SDKs failed to import.")
    except Exception as e:
         logger.error(f"Legacy SDK failed: {e}")

    return None

def get_mock_dashboard_data(revenue_today):
    """
    Returns realistic dummy data when AI is offline.
    """
    return {
        "prediction": int(revenue_today * 1.2),
        "analysis": "☁️ AI 연결 대기 중 (오프라인 모드): 현재 네트워크 상태로 인해 AI 서버에 연결할 수 없습니다. 대신 기본 예측 모델이 작동 중입니다. 날씨와 매출 추이를 기반으로 상승세가 예상됩니다.",
        "strategies": [
            { "category": "인력", "icon": "👥", "title": "현장 중심 운영", "summary": "피크타임 대비", "detail": "AI 연결이 원활하지 않습니다. 평소 데이터를 바탕으로 점심/저녁 피크타임에 집중해주세요.", "score": 80 },
            { "category": "재고", "icon": "📦", "title": "필수 재고 점검", "summary": "주요 품목 확인", "detail": "네트워크 이슈로 실시간 재고 분석이 지연되고 있습니다. 육안으로 주요 자재를 확인해주세요.", "score": 85 },
            { "category": "마케팅", "icon": "📣", "title": "단골 고객 관리", "summary": "기존 서비스 유지", "detail": "문자나 SNS를 통해 금일 영업 시간을 안내하고 단골 고객 이벤트를 진행해보세요.", "score": 75 }
        ],
        "cheer_msg": "네트워크는 잠시 쉬어가도, 사장님의 열정은 멈추지 않습니다! 힘내세요! 🔥"
    }

def generate_dashboard_analysis(sales_data, weather_data, inventory_data, event_data):
    """
    Combined AI Analyzer: Predicts revenue, analyzes flow, suggests strategy, and cheers.
    Everything in ONE call to speed up loading time (< 10s).
    """
    history_str = "\n".join(sales_data.get('history', []))
    revenue_today = sales_data.get('revenue', 0)
    
    prompt = f"""
    당신은 'Forkast AI'의 수석 분석가입니다.
    다음 매장 데이터를 종합 분석하여, 4가지 핵심 정보를 **JSON 포맷**으로 한 번에 출력하세요.
    
    [입력 데이터]
    1. 30일 매출 추이:
    {history_str}
    
    2. 오늘 현황:
    - 현재 매출: {revenue_today}원
    - 날씨: {weather_data}
    - 재고: {inventory_data}
    - 이벤트: {event_data}
    
    [분석 핵심 요구사항]
    - **가장 중요:** '30일 매출 추이' 데이터를 기반으로 오늘의 '날씨'와 '이벤트'가 매출에 미칠 영향을 분석하세요. 단순히 현재 수치만 보지 말고, 과거 패턴(요일/날씨 등)과 비교하여 인사이트를 도출해야 합니다.
    
    [요청 사항]
    다음 4가지 필드를 포함한 JSON 객체를 반환하세요.
    
    1. "prediction" (Number): 과거 추세와 오늘 변수(날씨/이벤트)를 종합한 최종 예상 매출.
    2. "analysis" (String): 실시간 매출 흐름 분석 (한 문단). "📈 상승세/하락세: 날씨와 이벤트 영향으로 ~~~." 형식.
    3. "strategies" (Array): 최적 운영 전략 3가지 (인력/재고/마케팅).
        - 각 객체: {{ "category": "인력", "icon": "👥", "title": "...", "summary": "...", "detail": "...", "score": 85 }}
    4. "cheer_msg" (String): 오늘 총매출({revenue_today}원)을 기준으로, 매출이 높으면 축하하고 낮으면 격려하는 구체적이고 따뜻한 힐링 메시지 (50자 이내).
    
    [JSON 출력 예시 - 엄격 준수]
    {{
      "prediction": 1250000,
      "analysis": "📈 상승세: 맑은 날씨로 유동 인구가 늘어 전주 대비 15% 상승 흐름입니다.",
      "strategies": [
        {{ "category": "인력", "icon": "👥", "title": "피크타임 집중", "summary": "12시~2시 알바 추가", "detail": "점심 피크가 예상되니...", "score": 90 }},
        ...
      ],
      "cheer_msg": "사장님, 오늘 대박 조짐이 보여요! 힘내세요! 🌟"
    }}
    
    ⚠️ 오직 JSON만 출력하세요. 마크다운 코드 블록(```json)을 사용하지 마세요.
    """
    
    response_text = get_gemini_response(prompt)
    
    if response_text is None:
        return get_mock_dashboard_data(revenue_today)

    # JSON Parsing Logic
    try:
        # Clean potential markdown
        clean_text = re.sub(r'```json\s*|\s*```', '', response_text).strip()
        data = json.loads(clean_text)
        return data
    except Exception as e:
        logger.error(f"Failed to parse Unified AI JSON: {e}. Raw: {response_text}")
        return get_mock_dashboard_data(revenue_today)

# Legacy functions kept for individual testing if needed, or can be removed.
def analyze_sales_flow(sales_data, weather_data): pass
def suggest_operational_strategy(sales_data, inventory_data, weather_data): pass
def get_emotional_care_message(): pass
def predict_revenue_with_ai(history_data, weather_data, inventory_data, event_data): pass
def consult_ai(question):
    prompt = f"질문: {question}. 답변:"
    return get_gemini_response(prompt)
