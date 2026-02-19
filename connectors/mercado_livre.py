from typing import List, Dict


class MercadoLivreConnector:
    """Stub connector for Mercado Livre (mock behaviour).

    In a real implementation this would call Mercado Livre APIs and map
    results into the project product schema.
    """

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        # deterministic mock results for testing/dev
        base = [
            {"title": f"{query.title()} ML Plus", "price": "R$ 2.799,00", "source": "MercadoLivre", "link": "https://ml/item/1", "snippet": "16GB RAM, SSD 512GB"},
            {"title": f"{query.title()} ML Basic", "price": "R$ 1.599,00", "source": "MercadoLivre", "link": "https://ml/item/2", "snippet": "8GB RAM, SSD 256GB"},
        ]
        return base[:limit]
