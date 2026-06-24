"""
carrefour.py
------------
Extractor para Carrefour Argentina.
Obtiene datos vía API pública de VTEX.
Campos extraídos: producto, precio, presentacion, supermercado, fuente
"""

from extract.vtex_base import extract_vtex_products

SUPERMERCADO = "carrefour"
BASE_URL = "https://www.carrefour.com.ar/api/catalog_system/pub/products/search"

def extract_carrefour() -> list[dict]:
    return extract_vtex_products(SUPERMERCADO, BASE_URL, query_pages=2)