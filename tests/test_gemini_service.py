import requests
import pytest
from core.services_gemini import GeminiService


class DummyResp:
    def __init__(self, json_data, status=200):
        self._json = json_data
        self.status_code = status
        self.text = str(json_data)

    def json(self):
        return self._json


def test_generate_parses_candidates(monkeypatch):
    data = {"candidates": [{"output": "Resposta Gemini simulada"}]}

    def fake_post(url, json=None, timeout=30):
        return DummyResp(data)

    monkeypatch.setattr('requests.post', fake_post)

    svc = GeminiService(api_key='test', model='models/text-bison-001')
    out = svc.generate('Teste de geração')
    assert 'Resposta Gemini simulada' in out


def test_call_returns_object(monkeypatch):
    data = {"candidates": [{"output": "Hi"}]}

    def fake_post(url, json=None, timeout=30):
        return DummyResp(data)

    monkeypatch.setattr('requests.post', fake_post)

    svc = GeminiService(api_key='test')
    r = svc([type('M',(),{'content':'hello','role':'user'})])
    assert hasattr(r, 'content') and 'Hi' in r.content
