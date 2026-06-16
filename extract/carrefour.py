"""
carrefour.py
------------
Extractor para Carrefour Argentina.
Obtiene datos vía API pública de VTEX.
Campos extraídos: producto, precio, presentacion, supermercado, fuente
"""

import requests

SUPERMERCADO = "carrefour"

# ---------------------------------------------------------------------------
# 1. Intento por API
# ---------------------------------------------------------------------------
def _extract_via_api() -> list[dict] | None:
    """
    Consulta la API pública de Carrefour (VTEX) con paginación.
    Retorna lista de productos o None si falla completamente.
    """
    products = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Extraer hasta 5 páginas de 50 productos (250 productos)
    for page in range(5):
        _from = page * 50
        _to = _from + 49
        url = (
            "https://www.carrefour.com.ar/api/catalog_system/pub/products/search"
            f"?_from={_from}&_to={_to}"
        )

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            items = resp.json()
            if not items:
                break  # Fin de los resultados
        except Exception as e:
            print(f"    [API] Error en página {page}: {e}")
            break

        for item in items:
            nombre = item.get("productName", "").strip()
            # Buscar precio en el primer SKU disponible
            try:
                sku = item["items"][0]
                precio = str(sku["sellers"][0]["commertialOffer"]["Price"])
                # Presentacion: viene en el campo measurementUnit + unitMultiplier
                measure     = sku.get("measurementUnit", "")
                multiplier  = sku.get("unitMultiplier", 1)
                presentacion = f"{multiplier} {measure}".strip() if measure else ""
                ean         = sku.get("ean")
            except (IndexError, KeyError):
                continue
            
            # Extraer categoria
            categoria = ""
            if item.get("categories"):
                categoria = item["categories"][0].replace("/", " ").strip()

            if not nombre or not precio:
                continue

            products.append({
                "producto":     nombre,
                "categoria":    categoria,
                "precio":       precio,
                "presentacion": presentacion,
                "ean":          ean,
                "supermercado": SUPERMERCADO,
                "fuente":       "api",
            })

    return products if products else None


# ---------------------------------------------------------------------------
# 2. Interfaz pública
# ---------------------------------------------------------------------------
def extract_carrefour() -> list[dict]:
    print("    Intentando API...")
    data = _extract_via_api()

    if data:
        print(f"    API OK → {len(data)} productos")
        return data

    print("    API falló o no retornó productos")
    return []