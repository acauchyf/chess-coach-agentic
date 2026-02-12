from __future__ import annotations
import os
import httpx
from typing import List

from chess_coach.application.ports.llm_port import LLMPort, ChatMessage


class OllamaLLMAdapter(LLMPort):
    def __init__(self) -> None:
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "120"))

    def chat(self, messages: List[ChatMessage], temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content, **({"name": m.name} if m.name else {})} for m in messages],
            "options": {"temperature": temperature},
            "stream": False,
        }
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(f"{self.base_url}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
            return data["message"]["content"]
