"""
llm.py — Groq API setup and LLM caller for ActionForge AI.
Uses Llama3-8b as primary model with Mixtral-8x7b as fallback.
"""

import os
from dotenv import load_dotenv
from groq import Groq
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client with the API key
_api_key = os.getenv("GROQ_API_KEY")
if not _api_key:
    raise RuntimeError("GROQ_API_KEY not found in environment. Check your .env file.")

client = Groq(api_key=_api_key)

# Model configuration (updated — old models were decommissioned by Groq)
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"


def call_llm(prompt: str, system: str, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """
    Call the Groq LLM with a system prompt and user prompt.
    Tries the primary model first, falls back to Mixtral on failure.

    Args:
        prompt: The user message / task-specific prompt.
        system: The system message defining the LLM's persona.
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative).
        max_tokens: Maximum number of tokens in the response.

    Returns:
        The LLM's response content as a string.

    Raises:
        HTTPException: If both primary and fallback models fail.
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    # Try primary model first
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
        except Exception as e:
            # If primary model fails, try fallback
            if model == PRIMARY_MODEL:
                print(f"[ActionForge] Primary model ({PRIMARY_MODEL}) failed: {e}. Trying fallback...")
                continue
            else:
                raise HTTPException(
                    status_code=502,
                    detail=f"LLM service unavailable. Both {PRIMARY_MODEL} and {FALLBACK_MODEL} failed. Error: {str(e)}"
                )

    raise HTTPException(status_code=502, detail="LLM returned empty response from both models.")
