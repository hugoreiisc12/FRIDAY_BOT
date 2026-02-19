from typing import List, Dict


class CasasBahiaConnector:
    """Stub connector for Casas Bahia (mock behaviour)."""

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        base = [
            {"title": f"{query.title()} Casas Bahia Prime", "price": "R$ 2.399,00", "source": "Casas Bahia", "link": "https://casasbahia/item/1", "snippet": "16GB RAM, SSD 512GB"},
            {"title": f"{query.title()} Casas Bahia Simples", "price": "R$ 1.199,00", "source": "Casas Bahia", "link": "https://casasbahia/item/2", "snippet": "4GB RAM, HD 1TB"},
        ]
        return base[:limit]