from typing import List, Dict


def validate_products(products: List[Dict]) -> List[Dict]:
    """Simple validation: remove items without name or price <= 0 and dedupe by url."""
    seen_urls = set()
    out = []
    for p in products:
        if not p.get("nome"):
            continue
        preco = p.get("preco")
        if preco is None:
            continue
        try:
            if float(preco) <= 0:
                continue
        except Exception:
            continue
        url = p.get("url") or p.get("nome")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        out.append(p)
    return out
