from extract.vtex_base import extract_vtex_products

SUPERMERCADO = "jumbo"
BASE_URL = "https://www.jumbo.com.ar/api/catalog_system/pub/products/search"
QUERIES = ["leche", "arroz", "carne", "pan"]

def extract_jumbo() -> list[dict]:
    return extract_vtex_products(SUPERMERCADO, BASE_URL, queries=QUERIES, max_pages=2)
