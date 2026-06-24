import json, urllib.request

headers = {"User-Agent": "Mozilla/5.0"}

# Test general catalog for Dia (no query)
req = urllib.request.Request(
    "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?_from=0&_to=49",
    headers=headers
)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
print(f"General catalog page 0-49: {len(data)} items")
for item in data[:5]:
    name = item.get("productName", "N/A")
    categories = item.get("categories", [])
    cat = categories[0].replace("/", " > ") if categories else "N/A"
    print(f"  {name}  ({cat})")

print()

# Test cluster IDs that might map to departments
for cluster_id in [1, 2, 3, 100, 138, 139, 572]:
    req = urllib.request.Request(
        f"https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?fq=productClusterIds:{cluster_id}&_from=0&_to=2",
        headers=headers
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data:
            print(f"Cluster {cluster_id}: {len(data)} items")
            for item in data[:2]:
                print(f"  {item.get('productName', 'N/A')}")
    except:
        pass

print()

# Test with category filter
req2 = urllib.request.Request(
    "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?fq=C%3A%2F100%2F&_from=0&_to=2",
    headers=headers
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=10)
    data2 = json.loads(resp2.read())
    print(f"Category C/100: {len(data2)} items")
except Exception as e:
    print(f"Category filter failed: {e}")
