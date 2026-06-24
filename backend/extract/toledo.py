from extract.vtex_base import extract_vtex_products

SUPERMERCADO = "toledo"
BASE_URL = "https://toledodigitalar.vtexcommercestable.com.br/api/catalog_system/pub/products/search"

def extract_toledo() -> list[dict]:
    return extract_vtex_products(SUPERMERCADO, BASE_URL, query_pages=2)
