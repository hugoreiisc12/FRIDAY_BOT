import os
import json
import requests
from typing import List, Any, Generator, Optional


class HuggingFaceRouterService:
    """Wrapper for Hugging Face Router Chat Completions.

    Provides three usage modes demonstrated by the user:
      - Using openai.OpenAI client with base_url set to Hugging Face router
      - Using huggingface_hub.InferenceClient
      - Direct HTTP streaming to router endpoint

    Interface:
      - __call__(messages) -> object with .content (synchronous, non-stream)
      - generate(prompt) -> str
      - stream_chat(messages) -> Generator of text chunks (for streaming)
    """

    def __init__(self, api_token: Optional[str] = None, model: Optional[str] = None, timeout: int = 60):
        self.api_token = api_token or os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
        if not self.api_token:
            raise RuntimeError("HF_TOKEN or HF_API_TOKEN not provided")
        self.model = model or os.getenv("HF_MODEL", "openai/gpt-oss-120b:together")
        self.timeout = timeout

        # try to initialize openai.Client-style wrapper
        self._openai_client = None
        try:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=self.api_token, base_url="https://router.huggingface.co/v1")
        except Exception:
            self._openai_client = None

        # try to initialize huggingface_hub InferenceClient
        self._hf_client = None
        try:
            from huggingface_hub import InferenceClient
            self._hf_client = InferenceClient(api_key=self.api_token)
        except Exception:
            self._hf_client = None

        # fallback will use requests directly to router
        self._url = f"https://router.huggingface.co/v1/chat/completions"
        self._headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}

    def _messages_to_payload(self, messages: List[Any]) -> dict:
        # Flatten message-like objects to role/content dicts
        msgs = []
        for m in messages:
            content = getattr(m, "content", None)
            role = getattr(m, "role", None) or "user"
            if content:
                msgs.append({"role": role, "content": content})
        return {"model": self.model, "messages": msgs}

    def __call__(self, messages: List[Any]):
        payload = self._messages_to_payload(messages)
        # prefer openai client
        if self._openai_client is not None:
            try:
                res = self._openai_client.chat.completions.create(**payload)
                # Try to extract text
                text = self._extract_text_from_openai_response(res)
                return type("R", (), {"content": text})
            except Exception as e:
                return type("R", (), {"content": f"Desculpe, HF router erro: {e}"})

        if self._hf_client is not None:
            try:
                res = self._hf_client.chat_completions.create(model=self.model, messages=payload["messages"])
                text = self._extract_text_from_hf_response(res)
                return type("R", (), {"content": text})
            except Exception as e:
                return type("R", (), {"content": f"Desculpe, HF client erro: {e}"})

        # fallback to requests
        try:
            resp = requests.post(self._url, headers=self._headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                text = self._extract_text_from_hf_response(data)
                return type("R", (), {"content": text})
            else:
                return type("R", (), {"content": f"Desculpe, HF retornou erro ({resp.status_code}): {resp.text}"})
        except Exception as e:
            return type("R", (), {"content": f"Desculpe, erro de conexão com HF router: {e}"})

    def generate(self, prompt: str) -> str:
        # simple wrapper that creates a single-user message
        messages = [type('M', (), {'role': 'user', 'content': prompt})]
        res = self.__call__(messages)
        return getattr(res, 'content', '')

    def stream_chat(self, messages: List[Any]) -> Generator[str, None, None]:
        payload = self._messages_to_payload(messages)
        payload["stream"] = True
        # Direct streaming via requests
        try:
            with requests.post(self._url, headers=self._headers, json=payload, stream=True, timeout=self.timeout) as response:
                if response.status_code != 200:
                    yield f"Desculpe, HF retornou erro ({response.status_code}): {response.text}"
                    return
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.strip() == "data: [DONE]":
                        return
                    if line.startswith("data:"):
                        chunk = line.lstrip("data:").strip()
                        try:
                            item = json.loads(chunk)
                            delta = item.get('choices', [{}])[0].get('delta', {})
                            c = delta.get('content') or delta.get('text')
                            if c:
                                yield c
                        except Exception:
                            # try raw
                            yield chunk
        except Exception as e:
            yield f"Desculpe, erro de stream HF: {e}"

    def _extract_text_from_openai_response(self, res: Any) -> str:
        # OpenAI-style response shape
        try:
            return res.choices[0].message.content
        except Exception:
            try:
                return str(res)
            except Exception:
                return ""

    def _extract_text_from_hf_response(self, data: Any) -> str:
        # HF client or requests -> normalize
        if isinstance(data, dict):
            # try different fields
            if 'choices' in data and isinstance(data['choices'], list) and data['choices']:
                ch = data['choices'][0]
                # delta/content or message
                if 'message' in ch and isinstance(ch['message'], dict):
                    # message contains 'content' perhaps list
                    msg = ch['message']
                    if 'content' in msg:
                        c = msg['content']
                        if isinstance(c, list):
                            # join text fields
                            texts = []
                            for item in c:
                                if isinstance(item, dict) and 'text' in item:
                                    texts.append(item['text'])
                                elif isinstance(item, str):
                                    texts.append(item)
                            return '\n'.join(texts)
                        elif isinstance(c, str):
                            return c
                if 'text' in ch:
                    return ch['text']
            # fallback to string
            return json.dumps(data)
        if isinstance(data, list):
            texts = []
            for item in data:
                if isinstance(item, dict) and 'generated_text' in item:
                    texts.append(item['generated_text'])
                elif isinstance(item, str):
                    texts.append(item)
            return '\n'.join(texts)
        return str(data)
