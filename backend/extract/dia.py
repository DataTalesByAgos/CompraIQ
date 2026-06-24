"""
dia.py
------------
Extractor para Supermercados Dia Argentina.
Usa la API pública de VTEX.
Estrategia:
  1. Catálogo general (sin query) — 5 páginas → ~250 productos
  2. Búsqueda por términos — 30+ queries, 2 páginas c/u → productos adicionales
Campos extraídos: producto, precio, presentacion, supermercado, fuente
"""

import requests

from .vtex_base import _is_grocery_product

SUPERMERCADO = "dia"
BASE_URL = "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search"

# Términos de búsqueda que cubren todas las categorías básicas
QUERIES = [
    "leche", "yogur", "queso", "manteca", "crema", "dulce de leche",
    "pan", "galletitas", "harina", "arroz", "fideos", "polenta",
    "aceite", "azucar", "sal", "cafe", "te", "mate", "yerba",
    "gaseosa", "agua", "cerveza", "vino", "jugo",
    "carne", "pollo", "pescado", "huevo", "milanesa",
    "papa", "tomate", "cebolla", "zanahoria", "lechuga",
    "jabon", "shampoo", "dentifrico", "papel higienico",
    "detergente", "lavandina", "limpiavidrios", "esponja",
    "comida para perro", "comida para gato",
    "congelados", "helado", "pizza",
]

def _extract_general_catalog() -> list[dict]:
    """Extrae el catálogo general sin filtro (como Carrefour)."""
    products = []
    headers = {"User-Agent": "Mozilla/5.0"}

    page = 0
    while page < 20:
        _from = page * 50
        _to = _from + 49
        url = f"{BASE_URL}?_from={_from}&_to={_to}"

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code not in (200, 206):
                break
            items = resp.json()
            if not items:
                break
        except Exception as e:
            print(f"    [Dia] Error en catálogo general pag {page}: {e}")
            break

        for item in items:
            if not _is_grocery_product(item):
                continue
            parsed = _parse_item(item)
            if parsed:
                products.append(parsed)

        if len(items) < 50:
            break
        page += 1

    return products


def _extract_by_queries(seen_ids: set) -> list[dict]:
    """Extrae productos adicionales mediante búsqueda por términos."""
    products = []
    headers = {"User-Agent": "Mozilla/5.0"}
    base_url = f"{BASE_URL}?ft="

    for query in QUERIES:
        for page in range(5):
            _from = page * 50
            _to = _from + 49
            url = f"{base_url}{query}&_from={_from}&_to={_to}"

            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code not in (200, 206):
                    break
                items = resp.json()
                if not items:
                    break
            except Exception as e:
                print(f"    [Dia] Error en query '{query}' pág {page}: {e}")
                break

            for item in items:
                if not _is_grocery_product(item):
                    continue
                product_id = item.get("productId")
                if product_id and product_id in seen_ids:
                    continue
                parsed = _parse_item(item)
                if parsed:
                    if product_id:
                        seen_ids.add(product_id)
                    products.append(parsed)

    return products


def _parse_item(item: dict) -> dict | None:
    """Parsea un item de VTEX al dict estándar."""
    nombre = item.get("productName", "").strip()
    try:
        sku = item["items"][0]
        precio = str(sku["sellers"][0]["commertialOffer"]["Price"])
        measure     = sku.get("measurementUnit", "")
        multiplier  = sku.get("unitMultiplier", 1)
        presentacion = f"{multiplier} {measure}".strip() if measure else ""
        ean         = sku.get("ean")
    except (IndexError, KeyError):
        return None

    categoria = ""
    if item.get("categories"):
        categoria = item["categories"][0].replace("/", " ").strip()

    if not nombre or not precio:
        return None

    product_id = item.get("productId")

    marca = item.get("brand") or ""

    return {
        "producto":     nombre,
        "product_id":   product_id,
        "marca":        marca,
        "categoria":    categoria,
        "precio":       precio,
        "presentacion": presentacion,
        "ean":          ean,
        "supermercado": SUPERMERCADO,
        "fuente":       "api",
    }


def extract_dia() -> list[dict]:
    print("    [Dia] Intentando API...")
    seen_ids: set[str] = set()

    # Paso 1: catálogo general
    general = _extract_general_catalog()
    for p in general:
        pid = p.get("product_id")
        if pid:
            seen_ids.add(pid)
    print(f"    [Dia] Catálogo general → {len(general)} productos")

    # Paso 2: búsqueda por términos (evitando duplicados)
    by_queries = _extract_by_queries(seen_ids)
    print(f"    [Dia] Búsqueda adicional → {len(by_queries)} productos")

    all_products = general + by_queries
    print(f"    [Dia] Total → {len(all_products)} productos")
    return all_products
