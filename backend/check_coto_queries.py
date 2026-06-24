import json, urllib.request

headers = {"User-Agent": "Mozilla/5.0"}
api_key = "key_r6xzz4IAoTWcipni"

queries = ["fideos", "aceite", "harina", "leche", "arroz", "carne", "pan",
           "yogur", "queso", "galletitas", "azucar", "sal", "cafe", "te",
           "gaseosa", "agua", "cerveza", "pollo", "huevo", "papa",
           "tomate", "jabon", "detergente", "shampoo", "papel"]

for q in queries:
    url = f"https://ac.cnstrc.com/search/{q}?key={api_key}"
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        results = data.get("response", {}).get("results", [])
        total = data.get("response", {}).get("total_num_results", len(results))
        if results:
            first = results[0].get("value", "N/A")
        else:
            first = "N/A"
        print(f"'{q}': {len(results)} results (total: {total}), first: {first}")
    except Exception as e:
        print(f"'{q}': ERROR {e}")
