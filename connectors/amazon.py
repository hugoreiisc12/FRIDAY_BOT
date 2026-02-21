import requests
from connectors.base import StoreConnector


class AmazonConnector(StoreConnector):
    token_env = "AMAZON_API_KEY"
    BASE_URL = "https://www.amazon.com.br"

    def search(self, query: str, limit: int = 5):
        # require that an API key is available
        self.require_key()
        response = requests.get(
            self.BASE_URL,
            params={"q": query, "api_key": self.api_key},
            timeout=5,
        )

        data = response.json()
        products = []
        for item in data.get("results", [])[:limit]:
            products.append({
                "store": "Amazon",
                "product_name": item.get("title") or item.get("tittle"),
                "price": item.get("price"),
                "currency": item.get("currency_id"),
                "in_stock": item.get("available_quantity", 0) > 0,
                "shopping_link": None,
                "product_url": item.get("permalink"),
            })
        return products
