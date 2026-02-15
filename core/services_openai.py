import os
from typing import List, Any

class OpenAISimpleService:
    """Simple wrapper around openai.ChatCompletion to be used when LangChain isn't available.

    Provides a callable interface: instance(messages) -> object with .content
    and a generate(prompt: str) -> str method for backward compatibility.
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = 250):
        try:
            import openai
        except Exception as e:
            raise RuntimeError("openai package not available") from e
        self.openai = openai
        self.openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def __call__(self, messages: List[Any]):
        # messages: list of objects with attribute `content` and optionally system/human
        sys_msgs = []
        human_msgs = []
        for m in messages:
            c = getattr(m, "content", "")
            # heuristics: treat text as system if it contains 'OBJETIVO' or 'Você é' or similar
            if isinstance(c, str) and ("objetivo" in c.lower() or "você é" in c.lower() or "histórico" in c.lower()):
                sys_msgs.append(c)
            else:
                human_msgs.append(c)

        system = "\n".join(sys_msgs).strip()
        human = "\n".join(human_msgs).strip()

        # Build messages for OpenAI ChatCompletion
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        if human:
            msgs.append({"role": "user", "content": human})

        # Fallback to just the human prompt
        if not msgs:
            msgs = [{"role": "user", "content": human or ""}]

        try:
            # Use OpenAI v2 Responses API via client
            client = self.openai.OpenAI(api_key=self.openai.api_key)
            # Input can be a list of role/content dicts or a single string
            payload = msgs
            res = client.responses.create(model=self.model, input=payload, temperature=self.temperature, max_output_tokens=self.max_tokens)
            # Try to extract text from response (handle several shapes)
            text = ""
            if hasattr(res, 'output') and res.output:
                # res.output is a list; each item may have 'content' list with dicts that have 'text' or 'content'
                for out in res.output:
                    contents = out.get('content', []) if isinstance(out, dict) else getattr(out, 'content', [])
                    for c in contents:
                        if isinstance(c, dict) and 'text' in c:
                            text += c['text']
                        elif isinstance(c, dict) and 'type' in c and c.get('type') == 'output_text' and 'text' in c:
                            text += c['text']
                        elif isinstance(c, str):
                            text += c
            # Fallback to string representation
            if not text:
                text = str(res)
            return type("R", (), {"content": text.strip()})
        except Exception as e:
            # surface the exception message for debugging
            return type("R", (), {"content": f"Desculpe, tive um problema ao gerar a resposta: {e}"})

    def generate(self, prompt: str) -> str:
        # simple wrapper for backward-compatible usage
        try:
            res = self.openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return res["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Desculpe, tive um problema: {e}"
