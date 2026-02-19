from typing import List, Dict
import re


def _parse_price(value) -> float:
    if value is None:
        return 0.0
    s = str(value)
    s = re.sub(r"[^0-9,\.]", "", s)
    if s.count(",") and s.count("."):
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def normalize_products(raw: List[Dict]) -> List[Dict]:
    """Normalize various connector payloads into project schema.

    Schema: { nome, preco, loja, url, specs }
    """
    out = []
    for item in raw:
        nome = item.get("nome") or item.get("title") or item.get("product_title") or item.get("name")
        preco = _parse_price(item.get("preco") or item.get("price") or item.get("currency_price") or item.get("inline_price"))
        loja = item.get("loja") or item.get("source") or item.get("merchant") or item.get("seller") or "-"
        url = item.get("url") or item.get("link") or item.get("product_url") or item.get("product_link") or ""
        specs = item.get("specs") or item.get("snippet") or item.get("description") or ""
        out.append({"nome": nome, "preco": preco, "loja": loja, "url": url, "specs": specs})
    return out
