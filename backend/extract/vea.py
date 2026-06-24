from extract.vtex_base import extract_vtex_products

SUPERMERCADO = "vea"
BASE_URL = "https://www.vea.com.ar/api/catalog_system/pub/products/search"

def extract_vea() -> list[dict]:
    return extract_vtex_products(SUPERMERCADO, BASE_URL, query_pages=2)
