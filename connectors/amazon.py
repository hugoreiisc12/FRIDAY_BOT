import requests
from connectors.base import StoreConnector

class AmazonConnector(StoreConnector):

    BASE_URL = "https://www.amazon.com.br"

    def search(self, query: str):
        response = requests.get(
            self.BASE_URL,
            params={"q": query},
            timeout=5
        )

        data = response.json()

        products = []
        for item in data["results"]:
            products.append({
                "store": "Amazon",
                "product_name": item["tittle"],
                "price": item["price"],
                "currency": item["currency_id"],
                "in_stock": item["available_quantiy"] > 0,
                "shopping_link": None,
                "product_url": item["permalink"]
            })
        
        return products