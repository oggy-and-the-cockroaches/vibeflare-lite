"""Settings API endpoints for user-configured Gemini API Key and Gemma model."""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.database.schema import get_db
from backend.services.llm import GemmaProvider, set_llm_provider, get_llm

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsPayload(BaseModel):
    api_key: Optional[str] = None
    model_name: Optional[str] = "gemma-4-31b-it"
    endpoint: Optional[str] = ""


def get_stored_setting(key: str, default: str = "") -> str:
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row and row[0]:
                return row[0]
    except Exception:
        pass
    return default


def set_stored_setting(key: str, value: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))


def load_settings_on_startup():
    """Load persisted API key and model from SQLite into environment."""
    key = get_stored_setting("gemini_api_key")
    model = get_stored_setting("gemma_model", "gemma-4-31b-it")
    endpoint = get_stored_setting("gemma_endpoint", "")

    if key:
        os.environ["GEMINI_API_KEY"] = key
    if model:
        os.environ["GEMMA_MODEL"] = model
    if endpoint:
        os.environ["GEMMA_ENDPOINT"] = endpoint

    set_llm_provider(GemmaProvider(
        api_key=key or os.environ.get("GEMINI_API_KEY", ""),
        model=model,
        endpoint=endpoint
    ))


@router.get("")
async def get_settings():
    """Retrieve current AI provider and model settings."""
    api_key = get_stored_setting("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
    model_name = get_stored_setting("gemma_model", "gemma-4-31b-it") or os.environ.get("GEMMA_MODEL", "gemma-4-31b-it")
    endpoint = get_stored_setting("gemma_endpoint") or os.environ.get("GEMMA_ENDPOINT", "")

    has_key = bool(api_key and api_key != "your_gemini_api_key_here")
    masked = f"{api_key[:6]}...{api_key[-4:]}" if (has_key and len(api_key) > 10) else ("Configured" if has_key else "")

    return {
        "model_name": model_name,
        "has_api_key": has_key,
        "masked_key": masked,
        "endpoint": endpoint,
        "provider": "gemma",
        "offline_fallback_active": not has_key,
        "supported_models": [
            "gemma-4-31b-it",
            "gemma-2-27b-it",
            "gemma-2-9b-it",
            "gemini-2.5-flash",
            "gemini-2.5-pro"
        ]
    }


@router.post("")
async def save_settings(payload: SettingsPayload):
    """Save user-provided Gemini API Key and Gemma model configuration."""
    model = (payload.model_name or "gemma-4-31b-it").strip()
    key = (payload.api_key or "").strip()
    endpoint = (payload.endpoint or "").strip()

    # Update SQLite store
    set_stored_setting("gemma_model", model)
    set_stored_setting("gemma_endpoint", endpoint)
    if key:
        set_stored_setting("gemini_api_key", key)
        os.environ["GEMINI_API_KEY"] = key
    elif payload.api_key == "":
        # Explicit empty string clears key to use offline fallback
        set_stored_setting("gemini_api_key", "")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

    os.environ["GEMMA_MODEL"] = model
    os.environ["GEMMA_ENDPOINT"] = endpoint

    # Update runtime LLM provider
    active_key = key if key else os.environ.get("GEMINI_API_KEY", "")
    set_llm_provider(GemmaProvider(
        api_key=active_key,
        model=model,
        endpoint=endpoint
    ))

    has_key = bool(active_key and active_key != "your_gemini_api_key_here")
    return {
        "success": True,
        "message": f"Settings saved. Model: {model}. Mode: {'Live AI' if has_key else 'Offline Fallback'}.",
        "has_api_key": has_key,
        "model_name": model
    }


@router.post("/test")
async def test_api_key(payload: SettingsPayload):
    """Test connection with the user-provided Gemini API key."""
    key = (payload.api_key or "").strip() or os.environ.get("GEMINI_API_KEY", "")
    model = (payload.model_name or "gemma-4-31b-it").strip()

    if not key or key == "your_gemini_api_key_here":
        return {
            "success": False,
            "error": "No API key provided. Vibeflare Lite will use deterministic offline fallback."
        }

    provider = GemmaProvider(api_key=key, model=model)
    prompt = "Respond with the word 'READY' and nothing else."
    try:
        response = provider.generate(prompt)
        if "API Error" in response or "unavailable" in response:
            return {"success": False, "error": response}
        return {
            "success": True,
            "message": f"Successfully connected to {model}!",
            "sample_response": response.strip()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
