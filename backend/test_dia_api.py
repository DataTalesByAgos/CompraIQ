import json, urllib.request

headers = {"User-Agent": "Mozilla/5.0"}

# Test 1: search by query
req = urllib.request.Request(
    "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?ft=fideo&_from=0&_to=2",
    headers=headers
)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
print(f'Query "fideo": {len(data)} items')
for item in data[:3]:
    name = item.get("productName", "N/A")
    sku = item["items"][0]
    seller = sku["sellers"][0]["commertialOffer"]
    price = seller["Price"]
    print(f"  {name} -> ${price}")

# Test 2: product cluster (category browsing)
req2 = urllib.request.Request(
    "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?fq=productClusterIds:572&_from=0&_to=3",
    headers=headers
)
resp2 = urllib.request.urlopen(req2, timeout=10)
data2 = json.loads(resp2.read())
print(f'\nCluster 572: {len(data2)} items')
for item in data2[:3]:
    name = item.get("productName", "N/A")
    sku = item["items"][0]
    seller = sku["sellers"][0]["commertialOffer"]
    price = seller["Price"]
    print(f"  {name} -> ${price}")

# Test 3: general catalog (no query)
req3 = urllib.request.Request(
    "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?_from=0&_to=3",
    headers=headers
)
resp3 = urllib.request.urlopen(req3, timeout=10)
data3 = json.loads(resp3.read())
print(f'\nGeneral catalog (no query): {len(data3)} items')
for item in data3[:3]:
    name = item.get("productName", "N/A")
    sku = item["items"][0]
    seller = sku["sellers"][0]["commertialOffer"]
    price = seller["Price"]
    print(f"  {name} -> ${price}")

# Test 4: more pages
req4 = urllib.request.Request(
    "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?ft=leche&_from=0&_to=49",
    headers=headers
)
resp4 = urllib.request.urlopen(req4, timeout=10)
data4 = json.loads(resp4.read())
print(f'\nQuery "leche" page 0-49: {len(data4)} items')

# Check total products by trying to find how many pages exist
import re
# The VTEX API returns a total count in the header or we can use _from=0&_to=0 to check
req5 = urllib.request.Request(
    "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?ft=leche&_from=0&_to=0",
    headers=headers
)
resp5 = urllib.request.urlopen(req5, timeout=10)
try:
    total = resp5.headers.get("X-Total-Count", resp5.headers.get("Total-Results", "unknown"))
    print(f'\nTotal "leche" products: {resp5.headers}')
except:
    pass
