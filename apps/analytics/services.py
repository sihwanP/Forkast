from django.conf import settings
import logging
import time
import random
import json
import re
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Models to try in order
AVAILABLE_MODELS = [
    'gemini-2.0-flash',      # Latest fast model
    'gemini-1.5-flash',      # Standard fast model
    'gemini-1.5-pro',        # High intelligence fallback
]

def get_gemini_response(prompt: str) -> Optional[str]:
    """
    Simulates or calls Gemini API to get text response.
    Handles retry logic and model fallback.
    """
    # Lazy Import & Config (New SDK)
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        debug_msg = f"Import Error in Analytics Service: {e}"
        # Ideally use proper logging instead of file write in production
        logger.error(debug_msg)
        # In this context, we return None to let caller handle it or raise
        # But keeping existing behavior of raising for import error vs returning None for api error
        # Actually existing code raises Exception on import error.
        raise Exception(debug_msg)

    first_error = None
    
    # Retry configuration
    max_retries = 3
    base_delay = 1  # seconds

    for i, model_name in enumerate(AVAILABLE_MODELS):
        for attempt in range(max_retries + 1):
            try:
                # Enforce 15s timeout via config if possible, or client defaults
                config = types.GenerateContentConfig()
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                # Check for 429 (Resource Exhausted)
                if "429" in error_str or "Resource exhausted" in error_str:
                    if attempt < max_retries:
                        delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                        logger.warning(f"Rate limit hit for {model_name}. Retrying in {delay:.2f}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                
                # Non-retriable error or max retries reached
                logger.warning(f"Failed with model {model_name}: {e}")
                if i == 0 and first_error is None:
                    first_error = e
                break # Move to next model
    
    error_msg = str(first_error) if first_error else "Unknown error"
    logger.error(f"All Gemini models failed. Primary error: {error_msg}")
    return None

def get_mock_dashboard_data(revenue_today: int) -> Dict[str, Any]:
    """
    Returns realistic dummy data when AI is offline.
    """
    return {
        "prediction": int(revenue_today * 1.2),
        "analysis": "☁️ AI 연결 대기 중 (오프라인 모드): 현재 네트워크 상태로 인해 AI 서버에 연결할 수 없습니다. 대신 기본 예측 모델이 작동 중입니다.",
        "strategies": [
            { "category": "인력", "icon": "👥", "title": "현장 중심 운영", "summary": "피크타임 대비", "detail": "평소 데이터를 바탕으로 점심/저녁 피크타임에 집중해주세요.", "score": 80 },
            { "category": "재고", "icon": "📦", "title": "필수 재고 점검", "summary": "주요 품목 확인", "detail": "육안으로 주요 자재를 확인해주세요.", "score": 85 },
            { "category": "마케팅", "icon": "📣", "title": "단골 고객 관리", "summary": "기존 서비스 유지", "detail": "단골 고객 이벤트를 진행해보세요.", "score": 75 }
        ],
        "cheer_msg": "네트워크는 잠시 쉬어가도, 사장님의 열정은 멈추지 않습니다! 힘내세요! 🔥"
    }

def generate_dashboard_analysis(sales_data: Dict, weather_data: str, inventory_data: str, event_data: str) -> Dict[str, Any]:
    """
    Combined AI Analyzer: Predicts revenue, analyzes flow, suggests strategy, and cheers.
    Everything in ONE call.
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
    
    [요청 사항]
    다음 4가지 필드를 포함한 JSON 객체를 반환하세요.
    1. "prediction" (Number): 최종 예상 매출.
    2. "analysis" (String): 실시간 매출 흐름 분석 (한 문단).
    3. "strategies" (Array): 최적 운영 전략 3가지.
    4. "cheer_msg" (String): 사장님을 위한 짧고 감성적인 응원 메시지.
    
    ⚠️ 오직 JSON만 출력하세요. 마크다운 사용 금지.
    """
    
    response_text = get_gemini_response(prompt)
    
    if response_text is None:
        return get_mock_dashboard_data(revenue_today)

    try:
        clean_text = re.sub(r'```json\s*|\s*```', '', response_text).strip()
        data = json.loads(clean_text)
        return data
    except Exception as e:
        logger.error(f"Failed to parse Unified AI JSON: {e}")
        return get_mock_dashboard_data(revenue_today)

def consult_ai(question: str) -> Optional[str]:
    prompt = f"""
    당신은 자영업자를 위한 전문 AI 비서입니다.
    질문: "{question}"
    핵심만 요약해서 답변해줘 (공손한 톤앤매너).
    """
    return get_gemini_response(prompt)
