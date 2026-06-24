from extract.vtex_base import extract_vtex_products

SUPERMERCADO = "jumbo"
BASE_URL = "https://www.jumbo.com.ar/api/catalog_system/pub/products/search"

def extract_jumbo() -> list[dict]:
    return extract_vtex_products(SUPERMERCADO, BASE_URL, query_pages=2)
