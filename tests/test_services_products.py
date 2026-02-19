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


def test_orchestrator_handles_empty():
    out = get_products("")
    assert out["query"] == ""
    assert out["results"] == []
    assert out["decision"]["best"] is None
