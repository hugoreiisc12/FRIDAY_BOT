import requests
from connectors.base import StoreConnector


class ShopeeConnector(StoreConnector):
    token_env = "SHOPEE_API_KEY"
    BASE_URL = "https://www.shopee.com.br/api/v1/search"

    def search(self, query: str, limit: int = 5):
        if self.api_key:
            # attach API key if required by real endpoint
            pass
        response = requests.get(
            self.BASE_URL,
            params={"q": query},
            timeout=5,
        )

        data = response.json()
        products = []
        for item in data.get("results", [])[:limit]:
            products.append({
                "store": "Shopee",
                "product_name": item.get("title"),
                "price": item.get("price"),
                "currency": item.get("currency_id"),
                "in_stock": item.get("available_quantity", 0) > 0,
                "shopping_link": None,
                "product_url": item.get("permalink"),
            })
        return products
