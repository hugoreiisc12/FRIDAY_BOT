import os
import sys
# ensure project root is importable when tests run in different contexts
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.product_service import get_products


def test_get_products_mock_no_serpapi():
    # ensure SERPAPI_KEY is not set so fallback mock is used
    if 'SERPAPI_KEY' in os.environ:
        del os.environ['SERPAPI_KEY']

    res = get_products('notebook', limit=3)
    assert isinstance(res, list)
    assert len(res) == 3
    assert all('nome' in p and 'preco' in p for p in res)


def test_get_products_empty_query_returns_empty():
    assert get_products('') == []
    assert get_products('a') == []  # min length guard
