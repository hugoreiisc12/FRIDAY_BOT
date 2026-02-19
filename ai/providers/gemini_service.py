import os
import requests
from typing import List, Any, Optional


class GeminiService:
    """Wrapper mínimo para Google Gemini / Generative Language API.

    Uses GEMINI_API_KEY from environment (or api_key param) and GEMINI_MODEL (optional).
    Falls back to a generic REST call to the Generative Language API v1beta2.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not provided")
        # default to a safe model name; user can override via env GEMINI_MODEL
        self.model = model or os.getenv("GEMINI_MODEL") or "models/text-bison-001"
        self.timeout = timeout
        # base url
        self._base = "https://generativelanguage.googleapis.com/v1beta2"

    def _build_prompt(self, messages: List[Any]) -> str:
        parts = []
        for m in messages:
            content = getattr(m, "content", None) or str(m)
            if hasattr(m, "role") and getattr(m, "role") == "system":
                parts.append(f"System: {content}\n")
            else:
                parts.append(content)
        return "\n".join(parts)

    def generate(self, prompt: str) -> str:
        url = f"{self._base}/{self.model}:generate?key={self.api_key}"
        payload = {
            "prompt": {"text": prompt},
            "temperature": 0.7,
            "maxOutputTokens": 512,
        }
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini returned status {resp.status_code}: {resp.text}")
            data = resp.json()
            # v1beta2 shape: may contain 'candidates' or 'outputs'
            if isinstance(data, dict):
                if "candidates" in data and isinstance(data["candidates"], list) and data["candidates"]:
                    return data["candidates"][0].get("output", "").strip()
                if "outputs" in data and isinstance(data["outputs"], list) and data["outputs"]:
                    # each output may have 'content' list of dicts
                    out = data["outputs"][0]
                    if isinstance(out, dict):
                        # join text fields
                        if "text" in out:
                            return out["text"].strip()
                        if "content" in out and isinstance(out["content"], list):
                            texts = []
                            for c in out["content"]:
                                if isinstance(c, dict) and "text" in c:
                                    texts.append(c["text"])
                            return "".join(texts).strip()
            return str(data)
        except Exception as e:
            return f"Desculpe, erro Gemini: {e}"

    def __call__(self, messages: List[Any]):
        prompt = self._build_prompt(messages)
        text = self.generate(prompt)
        return type("R", (), {"content": text})
