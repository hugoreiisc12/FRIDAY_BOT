from core.services_hf_router import HuggingFaceRouterService


class DummyResp:
    def __init__(self):
        self.status_code = 200
    def json(self):
        return {"choices":[{"message": {"content": "Resposta router simulada"}}]}


def test_hf_router_requests_monkeypatch(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=30):
        return DummyResp()

    monkeypatch.setattr('requests.post', fake_post)
    svc = HuggingFaceRouterService(api_token='test')
    # force requests fallback in test environment
    svc._openai_client = None
    svc._hf_client = None
    r = svc.generate('Teste router')
    assert 'Resposta router simulada' in r


def test_hf_router_streaming_monkeypatch(monkeypatch):
    class DummyStream:
        def __init__(self):
            self.status_code = 200
            # bytes must be valid ASCII literals; encode Unicode strings instead
            self._lines = ['data: {"choices":[{"delta":{"content":"Olá"}}]}'.encode('utf-8'), b'data: [DONE]']
            self._i = 0
        def iter_lines(self, decode_unicode=True):
            for l in self._lines:
                # emulate requests.Response.iter_lines(decode_unicode=True)
                if decode_unicode and isinstance(l, (bytes, bytearray)):
                    yield l.decode('utf-8')
                else:
                    yield l
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_post(url, headers=None, json=None, stream=False, timeout=30):
        return DummyStream()

    monkeypatch.setattr('requests.post', fake_post)
    svc = HuggingFaceRouterService(api_token='test')
    # force requests fallback in test environment
    svc._openai_client = None
    svc._hf_client = None
    chunks = list(svc.stream_chat([type('M',(),{'content':'Olá'})]))
    assert any('Olá' in c for c in chunks)
