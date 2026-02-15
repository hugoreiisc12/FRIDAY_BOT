import pytest
from core.services_hf import HuggingFaceService


class DummyResp:
    def __init__(self):
        self.status_code = 200
    def json(self):
        return [{"generated_text": "Resposta HF simulada"}]


def test_hf_service_monkeypatch(monkeypatch):
    # monkeypatch requests.post
    def fake_post(url, headers=None, json=None, timeout=30):
        return DummyResp()

    monkeypatch.setattr('requests.post', fake_post)
    svc = HuggingFaceService(api_token='test', model='some-model')
    r = svc.generate('Teste HF')
    assert 'Resposta HF simulada' in r
