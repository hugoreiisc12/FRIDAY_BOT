import os
import requests
from typing import List, Any


class HuggingFaceService:
    """Wrapper minimal da Hugging Face Inference API.

    Usa o endpoint `POST https://api-inference.huggingface.co/models/{model}`
    Espera `HF_API_TOKEN` no ambiente (ou token passado no construtor).
    Interface:
      - __call__(messages) -> obj com .content
      - generate(prompt) -> str
    """

    def __init__(self, api_token: str = None, model: str = None, timeout: int = 30):
        self.api_token = api_token or os.getenv("HF_API_TOKEN")
        self.model = model or os.getenv("HF_MODEL", "google/flan-t5-large")
        self.timeout = timeout
        if not self.api_token:
            raise RuntimeError("HF_API_TOKEN not provided")
        self.url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _prompt_from_messages(self, messages: List[Any]) -> str:
        # flatten message-like objects to a single prompt (system + human)
        parts = []
        for m in messages:
            c = getattr(m, "content", None)
            if c:
                parts.append(str(c))
        return "\n".join(parts)

    def __call__(self, messages: List[Any]):
        prompt = self._prompt_from_messages(messages)
        return self._call_prompt(prompt)

    def generate(self, prompt: str) -> str:
        return self._call_prompt(prompt).content

    def _call_prompt(self, prompt: str):
        payload = {"inputs": prompt}
        try:
            resp = requests.post(self.url, headers=self.headers, json=payload, timeout=self.timeout)
        except Exception as e:
            return type("R", (), {"content": f"Desculpe, tive um problema ao conectar HF: {e}"})

        if resp.status_code == 200:
            # response can be various shapes: string, dict, list
            try:
                data = resp.json()
            except Exception:
                return type("R", (), {"content": resp.text})

            # Many models return a list of generated texts or a dict with generated_text
            if isinstance(data, list):
                # typical: [{"generated_text": "..."}]
                parts = []
                for item in data:
                    if isinstance(item, dict) and "generated_text" in item:
                        parts.append(item["generated_text"])
                    elif isinstance(item, str):
                        parts.append(item)
                text = "\n".join(parts)
                return type("R", (), {"content": text.strip()})
            if isinstance(data, dict):
                # try to find a sensible string representation
                if "generated_text" in data:
                    return type("R", (), {"content": data["generated_text"].strip()})
                # some endpoints return {'data':[...]} or similar
                if "data" in data and isinstance(data["data"], list):
                    parts = []
                    for item in data["data"]:
                        if isinstance(item, dict):
                            # try common field names
                            for k in ("generated_text", "text", "content", "answer"):
                                if k in item:
                                    parts.append(str(item[k]))
                                    break
                        elif isinstance(item, str):
                            parts.append(item)
                    return type("R", (), {"content": "\n".join(parts).strip()})
                # fallback
                return type("R", (), {"content": str(data)})

        # non-200
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        return type("R", (), {"content": f"Desculpe, HF retornou erro ({resp.status_code}): {err}"})
