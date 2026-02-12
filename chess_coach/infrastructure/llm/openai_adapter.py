from __future__ import annotations
import os
import httpx
from typing import List

from chess_coach.application.ports.llm_port import LLMPort, ChatMessage


class OpenAILLMAdapter(LLMPort):
    """Minimal OpenAI Chat Completions adapter via HTTP.

    Env:
      OPENAI_API_KEY
      OPENAI_MODEL (default: gpt-4o-mini)
      OPENAI_BASE_URL (default: https://api.openai.com/v1)
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.timeout = float(os.getenv("OPENAI_TIMEOUT", "60"))

    def chat(self, messages: List[ChatMessage], temperature: float = 0.4) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
