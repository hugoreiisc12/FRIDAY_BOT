import os
import sys
# ensure project root is importable when tests run in different contexts
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.products import get_products


def test_orchestrator_returns_structure():
    out = get_products("notebook")
    assert isinstance(out, dict)
    assert out["query"] == "notebook"
    assert "results" in out and isinstance(out["results"], list)
    assert "decision" in out and isinstance(out["decision"], dict)
    # results must contain normalized keys
    if out["results"]:
        p = out["results"][0]
        assert all(k in p for k in ("nome", "preco", "loja", "url", "specs"))

    # ensure connectors contributed products (at least mock ones; Amazon may fail in CI)
    lojas = {p['loja'] for p in out['results']}
    expected = {"MercadoLivre", "MagazineLuiza", "Shopee", "Casas Bahia"}
    assert expected.issubset(lojas), f"missing expected stores, got {lojas}"

def test_orchestrator_handles_empty():
    out = get_products("")
    assert out["query"] == ""
    assert out["results"] == []
    assert out["decision"]["best"] is None
