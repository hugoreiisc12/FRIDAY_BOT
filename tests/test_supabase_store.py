import types
import pytest
from core.supabase_store import SupabaseConversationStore


class DummyRes:
    def __init__(self, data=None):
        self.data = data or []
        self.status_code = 201


class FakeTable:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, payload):
        # store the payload and return an object with execute()
        self._payload = payload
        return self

    def select(self, *args, **kwargs):
        return self

    def eq(self, k, v):
        self._filter = (k, v)
        return self

    def order(self, *args, **kwargs):
        return self

    def execute(self):
        # simple behavior: if inserting into sessions, return created id
        if 'user_id' in getattr(self, '_payload', {}):
            # create fake id
            row = dict(self._payload)
            row['id'] = '1111-2222-3333'
            return DummyRes([row])
        return DummyRes([])


class FakeClient:
    def __init__(self):
        self.tables = {}

    def table(self, name):
        return FakeTable(self.tables.setdefault(name, []))


class DummyCtx:
    def __init__(self, user_id='u1'):
        self.user_id = user_id
        self.estado = types.SimpleNamespace(value='inicial')
        self.modo_acao = None
        self.nome_usuario = 'Test'
        self.session_id = None


def test_create_session_and_save_message_monkeypatch(monkeypatch):
    fake_client = FakeClient()

    # monkeypatch create_client to return our fake client
    monkeypatch.setattr('core.supabase_store.create_client', lambda url, key: fake_client)

    store = SupabaseConversationStore(url='url', key='key')
    ctx = DummyCtx()

    sess = store.create_session(ctx)
    assert sess['id'] == '1111-2222-3333'
    assert ctx.session_id == '1111-2222-3333'

    # saving a message should not raise
    msg = store.save_message(ctx, 'user', 'Hello')
    assert isinstance(msg, dict)

    # get_messages should return a list (fake table returns [])
    msgs = store.get_messages(ctx.session_id)
    assert isinstance(msgs, list)
