import json, urllib.request

headers = {"User-Agent": "Mozilla/5.0"}
api_key = "key_r6xzz4IAoTWcipni"

# Test pagination with page parameter
for page in [0, 1, 2, 3]:
    url = f"https://ac.cnstrc.com/search/fideos?key={api_key}&num_results_per_page=50&page={page}"
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        results = data.get("response", {}).get("results", [])
        total = data.get("response", {}).get("total_num_results", "?")
        first = results[0].get("value", "N/A") if results else "NONE"
        print(f"page={page}: {len(results)} results (total: {total}), first: {first}")
    except Exception as e:
        print(f"page={page}: ERROR {e}")
