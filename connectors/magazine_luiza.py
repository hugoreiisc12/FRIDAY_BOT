from typing import List, Dict


class MagazineLuizaConnector:
    """Stub connector for Magazine Luiza (mock behaviour)."""

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        base = [
            {"title": f"{query.title()} Magalu Premium", "price": "R$ 2.499,00", "source": "MagazineLuiza", "link": "https://magalu/item/1", "snippet": "16GB RAM, SSD 512GB"},
            {"title": f"{query.title()} Magalu Econômico", "price": "R$ 1.799,00", "source": "MagazineLuiza", "link": "https://magalu/item/2", "snippet": "8GB RAM, SSD 256GB"},
        ]
        return base[:limit]