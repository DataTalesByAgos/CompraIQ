import json, urllib.request

req = urllib.request.Request(
    "https://ac.cnstrc.com/search/leche?key=key_r6xzz4IAoTWcipni",
    headers={"User-Agent": "Mozilla/5.0"}
)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
results = data.get("response", {}).get("results", [])
for item in results[:3]:
    item_data = item.get("data", {})
    precio = item_data.get("price")
    if precio and isinstance(precio, list):
        list_price = precio[0].get("listPrice")
        format_price = precio[0].get("formatPrice")
        print(f'{item.get("value", "N/A")}')
        print(f'  listPrice: {list_price!r} (type: {type(list_price).__name__})')
        print(f'  formatPrice: {format_price!r} (type: {type(format_price).__name__})')
        print()
