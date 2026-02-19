from fastapi import APIRouter, Query
from services.product_service import get_products

router = APIRouter()


@router.get("/products/search")
def search_products(query: str = Query(..., min_length=2)):
    """Search products by query using configured connectors (SerpAPI fallback -> mock).

    Returns a list of product objects: {nome, preco, loja, url, specs}
    """
    return get_products(query)
