from typing import List, Dict, Any


def analyze_products(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Lightweight decision engine: pick best product by lowest price and
    return a short rationale.
    """
    if not products:
        return {"best": None, "reason": "no products"}

    best = min(products, key=lambda p: p.get("preco", float("inf")))
    reason = f"Menor preço: R$ {best.get('preco'):.2f} — {best.get('nome')} ({best.get('loja')})"
    return {"best": best, "reason": reason}
