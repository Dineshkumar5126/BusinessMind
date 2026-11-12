import os
import requests
import json
import time
import re
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure environment variables are loaded from project root .env
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
load_dotenv(ENV_PATH)

DEFAULT_PRIMARY_MODEL = "gemini-flash-lite-latest"
DEFAULT_FALLBACK_MODEL = "gemini-3.6-flash"

# In-memory diagnostic tracker for GET /ai/health (never stores keys or secrets)
AI_DIAGNOSTICS = {
    "last_status": "idle",
    "last_source": None,
    "last_model_used": None,
    "last_error": None,
    "last_timestamp": None,
    "total_requests": 0,
    "gemini_success_count": 0,
    "fallback_count": 0
}

def get_ai_health():
    """
    Returns safe diagnostic information about GenAI status without exposing API keys.
    """
    load_dotenv(ENV_PATH)
    api_key = os.environ.get("GEMINI_API_KEY")
    is_configured = bool(api_key and api_key.strip() not in ["your_gemini_api_key_here", "your_api_key_here", ""])
    
    return {
        "status": "healthy",
        "api_key_configured": is_configured,
        "primary_model": os.environ.get("GEMINI_MODEL", DEFAULT_PRIMARY_MODEL),
        "fallback_model": os.environ.get("GEMINI_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL),
        "last_request_status": AI_DIAGNOSTICS["last_status"],
        "last_source": AI_DIAGNOSTICS["last_source"],
        "last_model_used": AI_DIAGNOSTICS["last_model_used"],
        "last_error": AI_DIAGNOSTICS["last_error"],
        "last_request_time": AI_DIAGNOSTICS["last_timestamp"],
        "total_requests": AI_DIAGNOSTICS["total_requests"],
        "gemini_success_count": AI_DIAGNOSTICS["gemini_success_count"],
        "fallback_count": AI_DIAGNOSTICS["fallback_count"]
    }

def sanitize_html_report(raw_text):
    """
    Safely sanitizes LLM-generated report text before returning to the frontend.
    Strips markdown code fences (```html ... ```) and ensures clean HTML tags.
    """
    if not raw_text:
        return ""
    
    cleaned = raw_text.strip()
    
    # Remove leading ```html or ``` markdown fences
    if cleaned.startswith("```html"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
        
    # Remove trailing ```
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
        
    return cleaned.strip()

def generate_local_fallback(data, prediction, reason=None):
    """
    Heuristic rule-based fallback generating a complete 6-section business report
    when external AI services are unavailable or unconfigured.
    """
    store_id = data.get("store_id", "Unknown")
    date = data.get("date", "Unknown")
    promo_status = "active" if str(data.get("promo")) == "1" else "inactive"
    state_holiday = data.get("state_holiday", "None")
    
    report = f"""
<div class="ai-report-section">
    <h4 class="ai-report-heading">Sales Forecast Summary</h4>
    <p class="ai-report-text">For Store {store_id}, the model estimates daily sales of approximately ${prediction:,.2f} for {date}. The prediction is generated using the trained XGBoost model together with engineered historical features and the supplied business/calendar conditions.</p>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Key Factors</h4>
    <p class="ai-report-text">The {promo_status} promotion status may influence promotional uplift. The {state_holiday} condition represents a calendar factor that is likely to affect customer activity. These factors are considered by the model alongside historical lag features.</p>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Business Interpretation</h4>
    <p class="ai-report-text">Based on the available inputs, this forecast indicates the expected baseline volume. Staffing and inventory should be calibrated to support this expected level of demand, ensuring operational readiness without unnecessary overhead.</p>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Recommended Actions</h4>
    <ul class="ai-report-list">
        <li>Align inventory planning with the projected demand volume for this date.</li>
        <li>Review staffing levels for the specified date based on the expected foot traffic.</li>
        <li>Monitor actual sales against this forecast to adapt future operational strategies.</li>
    </ul>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Risk and Limitations</h4>
    <p class="ai-report-text">This value is a machine-learning model prediction and not guaranteed actual sales. External factors not present in the current input data (e.g., unexpected local events or extreme weather) can affect real sales.</p>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Final Business Insight</h4>
    <p class="ai-report-text">Managers should use this forecast as a data-driven baseline for operational planning on {date}, while remaining adaptable to real-time, on-the-ground conditions.</p>
</div>
"""
    return report.strip()

def _record_diagnostic(status, source, model=None, error=None):
    """Updates internal diagnostic state safely without storing secrets."""
    AI_DIAGNOSTICS["total_requests"] += 1
    AI_DIAGNOSTICS["last_status"] = status
    AI_DIAGNOSTICS["last_source"] = source
    AI_DIAGNOSTICS["last_model_used"] = model
    AI_DIAGNOSTICS["last_error"] = error
    AI_DIAGNOSTICS["last_timestamp"] = datetime.now(timezone.utc).isoformat()
    if source == "gemini":
        AI_DIAGNOSTICS["gemini_success_count"] += 1
    else:
        AI_DIAGNOSTICS["fallback_count"] += 1

def generate_insights(data):
    """
    Calls the Google Gemini Generative Language API to generate business insights
    based on prediction and calendar data, with automatic retries and local fallback.
    """
    # Always reload environment variables freshly from project root
    load_dotenv(ENV_PATH)
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    primary_model = os.environ.get("GEMINI_MODEL", DEFAULT_PRIMARY_MODEL)
    fallback_model = os.environ.get("GEMINI_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL)
    
    prediction = data.get("predicted_sales", data.get("prediction", 0))
    if isinstance(prediction, str):
        try:
            prediction = float(prediction.replace(',', ''))
        except ValueError:
            prediction = 0

    date = data.get("date", "Unknown")
    store_id = data.get("store_id", "Unknown")
    promo = "Yes" if str(data.get("promo")) == "1" else "No"
    holiday = data.get("state_holiday", "None")
    school_holiday = "Yes" if str(data.get("school_holiday")) == "1" else "No"
    comp_dist = data.get("competition_distance", "Standard")

    print(f"[GenAI] Request started | Store: {store_id} | Date: {date} | Forecast: ${prediction:,.2f}")

    if not gemini_api_key or gemini_api_key.strip() in ["your_gemini_api_key_here", "your_api_key_here", ""]:
        print("[GenAI] API key unconfigured. Activating local heuristic fallback.")
        _record_diagnostic(status="fallback", source="local", error="API key unconfigured")
        return {
            "insights": generate_local_fallback(data, prediction, reason="API key unconfigured"),
            "status": "fallback",
            "source": "local",
            "is_fallback": True,
            "model": None
        }, 200

    prompt = f"""
You are the BusinessMind Business Sales Analysis Advisor.

Your task is to interpret a machine-learning sales forecast and provide a detailed business analysis.

Use ONLY the supplied project data.
Do not invent sales history, competitors, market statistics, customer numbers, profits, costs, or causal relationships.

Clearly distinguish prediction from interpretation.

Write a professional but easy-to-understand business report suitable for a college capstone demonstration.

Prediction Details:
- Target Date: {date}
- Store ID: {store_id}
- Active Promotion: {promo}
- State Holiday: {holiday}
- School Holiday: {school_holiday}
- Competition Distance: {comp_dist}
- PREDICTED SALES: ${prediction:,.2f}

Return a detailed report of approximately 200–350 words, structured with EXACTLY these HTML headings and tags (do not use Markdown hashes or asterisks):

<div class="ai-report-section">
    <h4 class="ai-report-heading">Sales Forecast Summary</h4>
    <p class="ai-report-text">[Explain predicted sales value, store ID, prediction date, promotion status, holiday statuses, and what it means in business terms]</p>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Key Factors</h4>
    <p class="ai-report-text">[Explain how the supplied business/calendar conditions may affect sales. Use careful language like "may influence", "is likely to affect".]</p>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Business Interpretation</h4>
    <p class="ai-report-text">[Explain practical interpretation. Do not invent profits, costs, etc.]</p>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Recommended Actions</h4>
    <ul class="ai-report-list">
        <li>[Action 1]</li>
        <li>[Action 2]</li>
        <li>[Action 3]</li>
    </ul>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Risk and Limitations</h4>
    <p class="ai-report-text">[Clearly explain that the value is a model prediction and not guaranteed actual sales. Mention external factors.]</p>
</div>

<div class="ai-report-section">
    <h4 class="ai-report-heading">Final Business Insight</h4>
    <p class="ai-report-text">[One concise paragraph summarizing the main takeaway for a business manager.]</p>
</div>

Do NOT use Markdown formatting (like **bold**, ### heading). Use only the HTML format requested above.
"""

    models_to_try = [primary_model]
    for alt in ["gemini-3.5-flash-lite", fallback_model, "gemini-flash-lite-latest"]:
        if alt and alt not in models_to_try:
            models_to_try.append(alt)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 2500,
            "temperature": 0.3
        }
    }

    delays = [2, 4]
    last_error_desc = None

    for current_model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={gemini_api_key}"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": gemini_api_key
        }

        print(f"[GenAI] Selected model: '{current_model}'")

        for attempt in range(2):
            start_time = time.time()
            try:
                print(f"[GenAI] Calling Gemini API (Model: {current_model}, Attempt {attempt + 1}/2)...")
                response = requests.post(url, json=payload, headers=headers, timeout=25)
                elapsed = time.time() - start_time

                if response.status_code == 200:
                    result_json = response.json()
                    try:
                        parts = result_json["candidates"][0]["content"]["parts"]
                        text_response = "".join(part.get("text", "") for part in parts)
                        sanitized_html = sanitize_html_report(text_response)
                        print(f"[GenAI] Request succeeded | Model: {current_model} | Status: 200 | Time: {elapsed:.2f}s")
                        _record_diagnostic(status="success", source="gemini", model=current_model)
                        return {
                            "insights": sanitized_html,
                            "status": "success",
                            "source": "gemini",
                            "is_fallback": False,
                            "model": current_model
                        }, 200
                    except (KeyError, IndexError) as parse_err:
                        last_error_desc = f"Response parse error: {str(parse_err)}"
                        print(f"[GenAI] Response parsing error on 200 OK: {last_error_desc}")
                        break

                elif response.status_code == 503:
                    last_error_desc = f"HTTP 503 Service Unavailable"
                    print(f"[GenAI] Model '{current_model}' HTTP 503 | Attempt {attempt + 1}/3")
                    if attempt < 2:
                        time.sleep(delays[attempt])
                        continue
                    break

                elif response.status_code == 429:
                    last_error_desc = "HTTP 429 Rate limit / Quota exceeded"
                    print(f"[GenAI] Model '{current_model}' HTTP 429: Rate limited or quota exhausted")
                    break

                elif response.status_code in [400, 401, 403]:
                    safe_msg = "Invalid API key or unauthorized request"
                    try:
                        err_json = response.json()
                        msg = err_json.get("error", {}).get("message", "")
                        if "API key not valid" in msg:
                            safe_msg = "API key not valid"
                        elif "unregistered callers" in msg:
                            safe_msg = "Unregistered caller / identity required"
                    except Exception:
                        pass
                    last_error_desc = f"HTTP {response.status_code}: {safe_msg}"
                    print(f"[GenAI] Model '{current_model}' authentication/client error: {last_error_desc}")
                    break

                elif response.status_code == 404:
                    last_error_desc = f"HTTP 404: Model '{current_model}' not found"
                    print(f"[GenAI] {last_error_desc}")
                    break

                else:
                    last_error_desc = f"HTTP {response.status_code}: Google API error"
                    print(f"[GenAI] Model '{current_model}' returned unexpected {last_error_desc}")
                    break

            except requests.exceptions.Timeout:
                last_error_desc = f"Request timed out after 25s"
                print(f"[GenAI] Timeout while contacting '{current_model}' on attempt {attempt + 1}")
                if attempt < 1:
                    time.sleep(delays[0])
                    continue
                break

            except requests.exceptions.RequestException as req_err:
                last_error_desc = f"Network failure: {type(req_err).__name__}"
                print(f"[GenAI] Network failure on '{current_model}': {last_error_desc}")
                break

    # If all models and retries fail, activate local fallback
    print(f"[GenAI] Fallback activated. Reason: {last_error_desc}")
    _record_diagnostic(status="fallback", source="local", model=primary_model, error=last_error_desc)
    
    return {
        "insights": generate_local_fallback(data, prediction, reason=last_error_desc),
        "status": "fallback",
        "source": "local",
        "is_fallback": True,
        "model": None,
        "fallback_reason": last_error_desc
    }, 200
