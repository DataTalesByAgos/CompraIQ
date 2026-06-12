import requests

def extract_vtex_products(supermarket_name: str, base_url: str, queries: list[str] = None, max_pages: int = 5) -> list[dict]:
    """
    Generic extractor for VTEX-based supermarket APIs (Carrefour, Dia, Jumbo, Disco, Vea).
    If queries are provided, it performs term-based searches.
    Otherwise, it paginates through the general catalog.
    """
    products = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}

    if queries:
        print(f"    [{supermarket_name}] Extracting via API using queries...")
        for query in queries:
            for page in range(max_pages):
                _from = page * 50
                _to = _from + 49
                url = f"{base_url}?ft={query}&_from={_from}&_to={_to}"
                
                try:
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code not in (200, 206):
                        break
                    items = resp.json()
                    if not items:
                        break
                except Exception as e:
                    print(f"    [{supermarket_name}] Error in query '{query}' pág {page}: {e}")
                    break

                for item in items:
                    parsed = _parse_item(item, supermarket_name)
                    if parsed:
                        products.append(parsed)
    else:
        print(f"    [{supermarket_name}] Extracting general catalog via API...")
        for page in range(max_pages):
            _from = page * 50
            _to = _from + 49
            url = f"{base_url}?_from={_from}&_to={_to}"

            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code not in (200, 206):
                    break
                items = resp.json()
                if not items:
                    break
            except Exception as e:
                print(f"    [{supermarket_name}] Error in page {page}: {e}")
                break

            for item in items:
                parsed = _parse_item(item, supermarket_name)
                if parsed:
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

    if not nombre or not precio:
        return None

    return {
        "producto":     nombre,
        "categoria":    categoria,
        "precio":       precio,
        "presentacion": presentacion,
        "ean":          ean,
        "supermercado": supermarket_name,
        "fuente":       "api",
    }
