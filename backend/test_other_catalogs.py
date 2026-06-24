import json, urllib.request

headers = {"User-Agent": "Mozilla/5.0"}

stores = [
    ("Jumbo", "https://www.jumbo.com.ar/api/catalog_system/pub/products/search"),
    ("Disco", "https://www.disco.com.ar/api/catalog_system/pub/products/search"),
    ("Vea", "https://www.vea.com.ar/api/catalog_system/pub/products/search"),
]

for name, base_url in stores:
    total = 0
    for page in range(3):
        _from = page * 50
        _to = _from + 49
        req = urllib.request.Request(
            f"{base_url}?_from={_from}&_to={_to}",
            headers=headers
        )
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            total += len(data)
            first = data[0].get("productName", "N/A") if data else "N/A"
            print(f"{name} page {page}: {len(data)} items, first: {first}")
        except Exception as e:
            print(f"{name} page {page}: ERROR {e}")
    print(f"{name} total: {total} items in 3 pages")
    print()
