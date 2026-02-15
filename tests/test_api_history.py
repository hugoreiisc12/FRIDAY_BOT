from fastapi.testclient import TestClient
from interfaces.api import app, CM


class FakeStore:
    def __init__(self):
        self._msgs = [
            {"id": "m1", "role": "user", "content": "Oi", "created_at": "now"},
            {"id": "m2", "role": "assistant", "content": "Olá", "created_at": "now"},
        ]
        self.client = None

    def get_messages(self, session_id):
        return self._msgs


def test_history_endpoint_with_inmemory_context(monkeypatch):
    client = TestClient(app)
    # ensure CM has a context with session_id
    uid = 'test_hist_user'
    CM.iniciar_conversa(uid, 'Tester')
    ctx = CM.obter_contexto(uid)
    ctx.session_id = 'sess-1'

    # attach fake store
    fake = FakeStore()
    CM.store = fake

    r = client.get('/history', params={'user_id': uid})
    assert r.status_code == 200
    data = r.json()
    assert data['session_id'] == 'sess-1'
    assert any(m['role'] == 'assistant' for m in data['messages'])


def test_history_endpoint_no_store_returns_404(monkeypatch):
    client = TestClient(app)
    # remove store
    CM.store = None
    r = client.get('/history', params={'user_id': 'nope'})
    assert r.status_code == 404
