from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChatMessage:
    role: str  # system|user|assistant|tool
    content: str
    name: Optional[str] = None


class LLMPort:
    def chat(self, messages: List[ChatMessage], temperature: float = 0.4) -> str:
        raise NotImplementedError
