from typing import List, Dict


class ShopeeConnector:
    """Stub connector for Shopee (mock behaviour)."""

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        base = [
            {"title": f"{query.title()} Shopee Express", "price": "R$ 2.599,00", "source": "Shopee", "link": "https://shopee/item/1", "snippet": "16GB RAM, SSD 512GB"},
            {"title": f"{query.title()} Shopee Basic", "price": "R$ 1.299,00", "source": "Shopee", "link": "https://shopee/item/2", "snippet": "4GB RAM, HD 1TB"},
        ]
        return base[:limit]