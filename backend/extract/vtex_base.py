"""
vtex_base.py
------------
Extractor genérico para APIs de supermercados basados en VTEX.
Estrategia:
  1. Catálogo general (sin query) — N páginas → ~N*50 productos
  2. Búsqueda por términos — queries adicionales para cubrir categorías
"""

import requests

# Categorías no-góndola a excluir (electrodomésticos, indumentaria, etc.)
NON_GROCERY_KEYWORDS = {
    "electro", "hogar", "textil", "juguetes", "juguete",
    "automotor", "librería", "libreria", "jardín", "jardin",
    "deportes", "indumentaria", "muebles", "herramientas",
    "ferretería", "ferreteria", "electrónica", "electronica",
    "informática", "informatica", "celulares", "telefonía",
    "telefonia", "bazar", "deco", "decoración", "decoracion",
    "automóvil", "automovil", "motos", "bicicletas",
    "iluminación", "iluminacion", "pinturería", "pintureria",
    "tiempo libre", "felices fiestas", "aire libre",
    "muñeca", "muñeco", "peluche", "campana",
}

# Palabras en nombres de producto NO comestibles dentro de categorías válidas
NON_FOOD_KEYWORDS = {
    "collar", "cucha", "arnés", "pretal",
    "juguete perro", "juguete gato", "juguete para perro", "juguete para gato",
    "juguetes perro", "juguetes gato", "juguete vinilico",
}


def _is_grocery_product(item: dict) -> bool:
    """Verifica si un producto es de la góndola (vs electrodomésticos, etc.)."""
    cats = item.get("categories", [])
    if cats:
        top = cats[0].strip("/").split("/")[0].lower()
        for kw in NON_GROCERY_KEYWORDS:
            if kw in top:
                return False
    name = (item.get("productName", "") or "").lower()
    for kw in NON_FOOD_KEYWORDS:
        if kw in name:
            return False
    return True


# Términos de búsqueda que cubren todas las categorías básicas
COMPREHENSIVE_QUERIES = [
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

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}


def extract_vtex_products(
    supermarket_name: str,
    base_url: str,
    queries: list[str] | None = None,
    general_pages: int = 20,
    query_pages: int = 2,
) -> list[dict]:
    """
    Extrae productos usando estrategia dual:
      1. Catálogo general (si el supermercado lo soporta)
      2. Búsqueda por términos (evitando duplicados)

    Args:
        supermarket_name: Nombre del supermercado (ej: "jumbo")
        base_url: URL base de la API VTEX
        queries: Lista de términos de búsqueda. Si es None usa COMPREHENSIVE_QUERIES.
        general_pages: Páginas de catálogo general (0 = desactivado)
        query_pages: Páginas por query (0 = desactivado)
    """
    seen_ids: set[str] = set()
    all_products: list[dict] = []

    # Paso 1: catálogo general
    if general_pages > 0:
        catalog = _extract_general(supermarket_name, base_url, general_pages)
        for p in catalog:
            pid = p.get("producto", "")
            if pid:
                seen_ids.add(pid)
        all_products.extend(catalog)
        print(f"    [{supermarket_name}] Catalogo general -> {len(catalog)} productos")

    if query_pages > 0:
        search_queries = queries if queries is not None else COMPREHENSIVE_QUERIES
        by_queries = _extract_by_queries(supermarket_name, base_url, search_queries, query_pages, seen_ids)
        all_products.extend(by_queries)
        print(f"    [{supermarket_name}] Busqueda adicional -> {len(by_queries)} productos")

    print(f"    [{supermarket_name}] Total -> {len(all_products)} productos")
    return all_products


def _extract_general(supermarket_name: str, base_url: str, max_pages: int) -> list[dict]:
    """Extrae páginas del catálogo general (sin filtro)."""
    products = []
    for page in range(max_pages):
        _from = page * 50
        _to = _from + 49
        url = f"{base_url}?_from={_from}&_to={_to}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code not in (200, 206):
                break
            items = resp.json()
            if not items:
                break
        except Exception as e:
            print(f"    [{supermarket_name}] Error catálogo general pag {page}: {e}")
            break
        for item in items:
            if not _is_grocery_product(item):
                continue
            parsed = _parse_item(item, supermarket_name)
            if parsed:
                products.append(parsed)
    return products


def _extract_by_queries(
    supermarket_name: str,
    base_url: str,
    queries: list[str],
    max_pages: int,
    seen_ids: set[str],
) -> list[dict]:
    """Extrae productos adicionales mediante búsqueda, evitando duplicados."""
    products = []
    for query in queries:
        for page in range(max_pages):
            _from = page * 50
            _to = _from + 49
            url = f"{base_url}?ft={query}&_from={_from}&_to={_to}"
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                if resp.status_code not in (200, 206):
                    break
                items = resp.json()
                if not items:
                    break
            except Exception as e:
                print(f"    [{supermarket_name}] Error query '{query}' pág {page}: {e}")
                break
            for item in items:
                if not _is_grocery_product(item):
                    continue
                product_id = item.get("productId")
                if product_id and product_id in seen_ids:
                    continue
                parsed = _parse_item(item, supermarket_name)
                if parsed:
                    if product_id:
                        seen_ids.add(product_id)
                    products.append(parsed)
    return products


def _parse_item(item: dict, supermarket_name: str) -> dict | None:
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

    marca = item.get("brand") or ""

    if not nombre or not precio:
        return None

    return {
        "producto":     nombre,
        "marca":        marca,
        "categoria":    categoria,
        "precio":       precio,
        "presentacion": presentacion,
        "ean":          ean,
        "supermercado": supermarket_name,
        "fuente":       "api",
    }
