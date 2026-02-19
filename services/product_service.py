"""Serviço de busca de produtos via conectores de API.

Estratégia:
- Se `SERPAPI_KEY` estiver presente, tenta consultar o SerpAPI (Google Shopping).
- Em caso de erro ou ausência de chave, devolve resultados mock para desenvolvimento.

Função principal: `get_products(query: str, limit: int = 5) -> list[dict]`.
Cada produto: { 'nome', 'preco', 'loja', 'url', 'specs' }
"""

from typing import List, Dict, Optional
import os
import re
import requests

SERPAPI_URL = "https://serpapi.com/search.json"


def _parse_price(price_str: Optional[str]) -> Optional[float]:
    if not price_str:
        return None
    # Remove currency symbols and normalize decimals
    s = str(price_str).strip()
    # common formats: "R$ 3.000,00", "$2,499.99", "2.499,00"
    s = re.sub(r"[^0-9,\.]", "", s)
    # if contains ',' and '.' assume thousands separator + decimal (BR format)
    if s.count(",") and s.count("."):
        # remove thousand separators (.) and replace decimal comma
        s = s.replace(".", "").replace(",", ".")
    else:
        # replace comma with dot for decimals
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def _product_from_serp_item(item: dict) -> Dict:
    title = item.get("title") or item.get("name") or item.get("product_title") or "Produto"
    price = item.get("price") or item.get("inline_price") or item.get("price_string") or item.get("currency_price")
    price_f = _parse_price(price) or 0.0
    loja = item.get("source") or item.get("seller") or item.get("store") or item.get("merchant") or "-"
    url = item.get("link") or item.get("product_link") or item.get("product_url") or item.get("link_to_product") or ""
    specs = item.get("snippet") or item.get("description") or ""
    return {"nome": title, "preco": price_f, "loja": loja, "url": url, "specs": specs}


def _mock_products(query: str, limit: int = 5) -> List[Dict]:
    # deterministic but simple mocks for development / tests
    base = [
        {"nome": f"{query.title()} Pro 16GB", "preco": 2999.0, "loja": "Loja A", "url": "https://loja.a/prod/1", "specs": "16GB RAM, SSD 512GB"},
        {"nome": f"{query.title()} Slim 8GB", "preco": 2199.0, "loja": "Loja B", "url": "https://loja.b/prod/2", "specs": "8GB RAM, SSD 256GB"},
        {"nome": f"{query.title()} Basic 4GB", "preco": 1499.0, "loja": "Loja C", "url": "https://loja.c/prod/3", "specs": "4GB RAM, HD 1TB"},
    ]
    return base[:limit]


def get_products(query: str, limit: int = 5) -> List[Dict]:
    """Busca produtos usando conectores de API (ex.: SerpAPI) ou mock.

    Retorna uma lista de dicionários contendo chaves: nome, preco, loja, url, specs.
    """
    if not query or len(query.strip()) < 2:
        return []

    serp_api_key = os.getenv("SERPAPI_KEY")
    if not serp_api_key:
        return _mock_products(query, limit)

    try:
        params = {"engine": "google_shopping", "q": query, "api_key": serp_api_key, "num": limit}
        resp = requests.get(SERPAPI_URL, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("shopping_results") or data.get("product_results") or data.get("organic_results") or []
        results = []
        for it in items:
            results.append(_product_from_serp_item(it))
            if len(results) >= limit:
                break

        if not results:
            # fallback to mock when SerpAPI returns nothing
            return _mock_products(query, limit)

        return results

    except Exception:
        # on any error, return mock results so service remains usable in dev/tests
        return _mock_products(query, limit)
