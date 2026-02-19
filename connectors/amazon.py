from typing import List, Dict


class AmazonConnector:
    """Stub connector for Amazon (mock behaviour)."""

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        base = [
            {"product_title": f"{query.title()} Amazon Pro", "currency_price": "$2,699.99", "merchant": "Amazon", "product_url": "https://amazon/item/1", "description": "16GB RAM, SSD 512GB"},
            {"product_title": f"{query.title()} Amazon Lite", "currency_price": "$1,499.00", "merchant": "Amazon", "product_url": "https://amazon/item/2", "description": "8GB RAM, HD 1TB"},
        ]
        return base[:limit]
