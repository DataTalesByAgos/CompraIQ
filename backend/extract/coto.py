"""
coto.py
------------
Extractor para Coto Digital Argentina.
Usa la API pública de Constructor.io.
Estrategia: búsqueda por 30+ términos con paginación (50 resultados x 2 páginas = 100/query).
Campos extraídos: producto, precio, presentacion, supermercado, fuente
"""

import requests

SUPERMERCADO = "coto"
API_KEY = "key_r6xzz4IAoTWcipni"
BASE_URL = f"https://ac.cnstrc.com/search/"

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

HEADERS = {"User-Agent": "Mozilla/5.0"}

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

NON_FOOD_KEYWORDS = {
    "collar", "cucha", "arnés", "pretal",
    "juguete perro", "juguete gato", "juguete para perro", "juguete para gato",
    "juguetes perro", "juguetes gato", "juguete vinilico",
}


def _is_grocery_product(item_data: dict, item_name: str = "") -> bool:
    groups = item_data.get("groups", [])
    if groups:
        for g in groups:
            display = g.get("display_name", "").lower()
            for kw in NON_GROCERY_KEYWORDS:
                if kw in display:
                    return False
    name = item_name.lower()
    for kw in NON_FOOD_KEYWORDS:
        if kw in name:
            return False
    return True


def _extract_by_queries(seen_names: set[str]) -> list[dict]:
    """Extrae productos mediante búsqueda por términos con paginación."""
    products = []

    for query in QUERIES:
        for page in range(1, 6):  # 1-indexed en Constructor.io
            url = f"{BASE_URL}{query}?key={API_KEY}&num_results_per_page=50&page={page}"
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                if resp.status_code != 200:
                    break
                data = resp.json()
                items = data.get("response", {}).get("results", [])
                if not items:
                    break
            except Exception as e:
                print(f"    [Coto] Error en query '{query}' pág {page}: {e}")
                break

            for item in items:
                item_data = item.get("data", {})
                nombre = item.get("value", "").strip()
                if not _is_grocery_product(item_data, nombre):
                    continue
                if not nombre or nombre in seen_names:
                    continue
                seen_names.add(nombre)
                precio = item_data.get("price")
                if not precio or not isinstance(precio, list):
                    continue

                precio_val = precio[0].get("listPrice") or precio[0].get("formatPrice")
                if not precio_val:
                    continue

                precio_str = str(precio_val)

                categoria = ""
                groups = item_data.get("groups", [])
                if groups:
                    categoria = groups[0].get("display_name", "").strip()

                presentacion = ""
                ean = item_data.get("product_main_ean")
                marca = item_data.get("brand", "") or item_data.get("brand_name", "") or ""

                products.append({
                    "producto":     nombre,
                    "marca":        marca,
                    "categoria":    categoria,
                    "precio":       precio_str,
                    "presentacion": presentacion,
                    "ean":          ean,
                    "supermercado": SUPERMERCADO,
                    "fuente":       "api",
                })

    return products


def extract_coto() -> list[dict]:
    print("    [Coto] Intentando API...")
    seen_names: set[str] = set()
    products = _extract_by_queries(seen_names)
    print(f"    [Coto] API OK → {len(products)} productos")
    return products
