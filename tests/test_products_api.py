import os
import sys
import pytest
from fastapi.testclient import TestClient

# ensure project root is importable in test runner
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from interfaces.api import app

client = TestClient(app)


def test_products_search_route_returns_list():
    r = client.get('/products/search', params={'query': 'notebook'})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'nome' in data[0]
    assert 'preco' in data[0]
