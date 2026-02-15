import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from interfaces.api import app, CM
from tests.test_flow_purchase import MockRAGForFlow

client = TestClient(app)


def setup_module(module):
    # Inject mock RAG for deterministic responses
    CM.rag = MockRAGForFlow()


def test_start_and_message_flow():
    r = client.post("/start", json={"user_id": "api_user", "name": "APIUser"})
    assert r.status_code == 200

    r2 = client.post("/message", json={"user_id": "api_user", "message": "1"})
    assert r2.status_code == 200
    assert "BUSCAR" in r2.json().get("resposta").upper()

    r3 = client.post("/message", json={"user_id": "api_user", "message": "Quero notebook Dell até R$3000 com 16GB"})
    assert r3.status_code == 200
    assert r3.json().get("estado") == "aguardando_selecao_produto"
    assert "1)" in r3.json().get("resposta")

    # select
    r4 = client.post("/message", json={"user_id": "api_user", "message": "1"})
    assert r4.status_code == 200
    assert r4.json().get("estado") == "aguardando_confirmacao_adicao"

    # confirm
    r5 = client.post("/message", json={"user_id": "api_user", "message": "sim"})
    assert r5.status_code == 200
    assert r5.json().get("carrinho") and len(r5.json().get("carrinho")) >= 1

    # checkout
    r6 = client.post("/checkout/api_user")
    assert r6.status_code == 200
    assert (r6.json().get("manual_checkout") is True) or ("manual" in r6.json().get("resposta", "").lower())
