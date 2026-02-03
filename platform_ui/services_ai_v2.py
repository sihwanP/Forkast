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
    # Lazy Import & Config (New SDK)
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        debug_msg = f"Import Error in V2: {e}"
        with open('ai_debug_v2.log', 'a', encoding='utf-8') as f:
             f.write(f"[{time.strftime('%H:%M:%S')}] {debug_msg}\n")
        logger.error(debug_msg)
        raise Exception(debug_msg)

    with open('ai_debug_v2.log', 'a', encoding='utf-8') as f:
         f.write(f"[{time.strftime('%H:%M:%S')}] Client initialized successfully. Prompting...\n")

    first_error = None
    
    # Retry configuration
    max_retries = 3
    base_delay = 1  # seconds

    for i, model_name in enumerate(AVAILABLE_MODELS):
        for attempt in range(max_retries + 1):
            try:
                # New SDK Usage
                # Enforce 15s timeout
                config = types.GenerateContentConfig(
                    # additional_params if needed, but timeout is often client-side in requests
                )
                
                # Note: The new SDK generates content via client.models
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                return response.text
            except Exception as e:
                # Check for 429 (Resource Exhausted)
                error_str = str(e)
                if "429" in error_str or "Resource exhausted" in error_str:
                    if attempt < max_retries:
                        delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                        logger.warning(f"Rate limit hit for {model_name}. Retrying in {delay:.2f}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                
                # Non-retriable error or max retries reached for this model
                logger.warning(f"Failed with model {model_name}: {e}")
                if i == 0 and first_error is None:
                    first_error = e
                break # Move to next model
    
    # If all fail
    error_msg = str(first_error) if first_error else "Unknown error"
    logger.error(f"All Gemini models failed. Primary error: {error_msg}")
    
    # DEBUG: Write to file to ensure we see the error
    try:
        with open('ai_error.log', 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Connection Error: {error_msg}\n")
    except:
        pass
        
    return None # Return None to trigger Mock Fallback in caller

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
    4. "cheer_msg" (String): 사장님을 위한 짧고 감성적인 위로/응원 메시지 (30자 이내).
    
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
    
    with open('ai_debug_v2.log', 'a', encoding='utf-8') as f:
         f.write(f"[{time.strftime('%H:%M:%S')}] AI Response: {str(response_text)[:100]}...\n")

    if response_text is None:
        logger.warning("Falling back to Mock Data due to AI connection failure.")
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
# For now, we keep them but they won't be used in the main flow.
def analyze_sales_flow(sales_data, weather_data):
    pass
def suggest_operational_strategy(sales_data, inventory_data, weather_data):
    pass
def get_emotional_care_message():
    pass
def predict_revenue_with_ai(history_data, weather_data, inventory_data, event_data):
    pass
def consult_ai(question):
    # Only this one is still used individually by the chat
    prompt = f"""
    당신은 자영업자를 위한 전문 AI 비서입니다. (법률, 노무, 세무, 마케팅 지식 보유)
    질문: "{question}"
    핵심만 요약해서 답변해줘 (공손한 톤앤매너).
    """
    return get_gemini_response(prompt)
