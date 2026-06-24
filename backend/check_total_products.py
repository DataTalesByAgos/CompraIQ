import json, urllib.request, sys

headers = {"User-Agent": "Mozilla/5.0"}

stores = [
    ("Dia", "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search"),
    ("Carrefour", "https://www.carrefour.com.ar/api/catalog_system/pub/products/search"),
    ("Jumbo", "https://www.jumbo.com.ar/api/catalog_system/pub/products/search"),
    ("Disco", "https://www.disco.com.ar/api/catalog_system/pub/products/search"),
    ("Vea", "https://www.vea.com.ar/api/catalog_system/pub/products/search"),
]

for name, base_url in stores:
    total = 0
    page = 0
    categories_found = set()
    first_item = None

    while page < 20:
        _from = page * 50
        _to = _from + 49
        url = f"{base_url}?_from={_from}&_to={_to}"
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            if not data:
                break
            if page == 0 and data:
                first_item = data[0].get("productName", "N/A")
            total += len(data)
            for item in data:
                cats = item.get("categories", [])
                if cats:
                    parts = cats[0].strip("/").split("/")
                    if len(parts) > 0 and parts[0]:
                        categories_found.add(parts[0])
            sys.stdout.write(f"\r{name}: page {page+1}, {total} total")
            sys.stdout.flush()
            if len(data) < 50:
                page += 1
                break
            page += 1
        except Exception as e:
            print(f"\n{name} page {page}: {e}")
            break

    print(f"\n{name}: {total} products in {page+1} pages")
    print(f"  first: {first_item}")
    print(f"  categories ({len(categories_found)}): {sorted(categories_found)[:10]}...")

print("\nDone!")
