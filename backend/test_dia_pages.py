import json, urllib.request

headers = {"User-Agent": "Mozilla/5.0"}

# Check product variety across pages
seen_names = set()
for page in range(5):
    _from = page * 50
    _to = _from + 49
    req = urllib.request.Request(
        f"https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?_from={_from}&_to={_to}",
        headers=headers
    )
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    new_names = set()
    for item in data:
        name = item.get("productName", "")
        new_names.add(name)
        seen_names.add(name)
    print(f"Page {page} (_from={_from}, _to={_to}): {len(data)} items, {len(new_names)} unique new, {len(seen_names)} total unique")
"""
    # Print first 3 items
    for item in data[:3]:
        cat = item.get("categories", ["N/A"])[0].replace("/", " > ") if item.get("categories") else "N/A"
        print(f"  {item.get('productName', 'N/A')}  [{cat}]")
"""
