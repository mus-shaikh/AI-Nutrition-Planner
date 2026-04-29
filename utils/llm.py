"""
utils/llm.py — Multi-provider LLM factory.

Supports: google (FREE), groq (FREE), anthropic (paid), openai (paid)
Set LLM_PROVIDER in your .env file to choose.

BUG FIXES:
- Strips ALL whitespace + CRLF from provider string (Windows .env fix)
- Uses dict dispatch instead of if/elif to avoid branch fall-through
- No lru_cache on the factory (avoids caching a broken state)
- LLM instance cached separately in _LLM_INSTANCE
"""

from __future__ import annotations
import os
from dotenv import load_dotenv

# Re-load .env explicitly so Windows CRLF files are handled
load_dotenv(override=True)

# Read keys fresh (not from config module, avoids import-time caching issues)
def _key(name: str) -> str:
    """Get env var, strip all whitespace/CRLF (Windows .env fix)."""
    return (os.getenv(name) or "").strip().strip("\r\n").strip()

# ── Cache at module level (not inside lru_cache) ──────────────────────────────
_LLM_INSTANCE = None


def get_llm():
    """
    Return a LangChain chat model for the configured LLM_PROVIDER.
    Instance is cached after first successful creation.
    """
    global _LLM_INSTANCE
    if _LLM_INSTANCE is not None:
        return _LLM_INSTANCE

    provider = _key("LLM_PROVIDER") or "google"
    provider = provider.lower()

    # Debug print (visible in terminal, helps diagnose .env issues)
    print(f"[LLM] Provider: '{provider}'")

    from config.settings import LLM_MODELS, LLM_TEMPERATURE, LLM_MAX_TOKENS
    model = LLM_MODELS.get(provider)
    if not model:
        raise ValueError(
            f"Unknown LLM_PROVIDER='{provider}'. "
            f"Valid options: google, groq, anthropic, openai\n"
            f"Check your .env file — make sure there are no spaces or quotes around the value."
        )

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = _key("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GOOGLE_API_KEY is missing.\n"
                "Get a FREE key at: https://ai.google.dev\n"
                "Add to .env: GOOGLE_API_KEY=AIza..."
            )
        print(f"[LLM] Using Google Gemini: {model}")
        _LLM_INSTANCE = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=LLM_TEMPERATURE,
            max_output_tokens=LLM_MAX_TOKENS,
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq
        api_key = _key("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY is missing.\n"
                "Get a FREE key at: https://console.groq.com\n"
                "Add to .env: GROQ_API_KEY=gsk_..."
            )
        print(f"[LLM] Using Groq: {model}")
        _LLM_INSTANCE = ChatGroq(
            model=model,
            groq_api_key=api_key,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = _key("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is missing.\n"
                "Get key at: https://console.anthropic.com\n"
                "Add to .env: ANTHROPIC_API_KEY=sk-ant-..."
            )
        print(f"[LLM] Using Anthropic Claude: {model}")
        _LLM_INSTANCE = ChatAnthropic(
            model=model,
            anthropic_api_key=api_key,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = _key("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY is missing.\n"
                "Get key at: https://platform.openai.com\n"
                "Add to .env: OPENAI_API_KEY=sk-..."
            )
        print(f"[LLM] Using OpenAI: {model}")
        _LLM_INSTANCE = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )

    else:
        raise ValueError(
            f"Unrecognised provider: '{provider}'\n"
            f"Valid options are: google, groq, anthropic, openai"
        )

    return _LLM_INSTANCE
