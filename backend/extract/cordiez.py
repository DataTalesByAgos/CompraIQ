from extract.vtex_base import extract_vtex_products

SUPERMERCADO = "cordiez"
BASE_URL = "https://arcordiezb2c.vtexcommercestable.com.br/api/catalog_system/pub/products/search"

def extract_cordiez() -> list[dict]:
    return extract_vtex_products(SUPERMERCADO, BASE_URL, query_pages=2)
