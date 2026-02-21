import requests
from connectors.base import StoreConnector


class CasasBahiaConnector(StoreConnector):
    token_env = "CASAS_BAHIA_API_KEY"
    BASE_URL= "https://www.casasbahia.com.br/api/v1/search"

    def search(self, query: str, limit: int = 5):
        if self.api_key:
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
                "store": "Casas Bahia",
                "product_name": item.get("title") or item.get("tittle"),
                "price": item.get("price"),
                "currency": item.get("currency_id"),
                "in_stock": item.get("available_quantity", 0) > 0,
                "shopping_link": None,
                "product_url": item.get("permalink"),
            })
        return products
