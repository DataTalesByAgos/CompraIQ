import json, urllib.request

headers = {"User-Agent": "Mozilla/5.0"}
api_key = "key_r6xzz4IAoTWcipni"

# Test different pagination approaches
tests = [
    {"num_results": 50},
    {"num_results": 50, "page": 2},
    {"num_results": 50, "offset": 0},
    {"num_results": 50, "offset": 50},
    {"num_results": 50, "offset": 100},
    {"num_results": 50, "page": 1},
    {"num_results": 20, "page": 0},
]

for params in tests:
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"https://ac.cnstrc.com/search/fideos?key={api_key}&{qs}"
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        results = data.get("response", {}).get("results", [])
        total = data.get("response", {}).get("total_num_results", "?")
        first = results[0].get("value", "N/A") if results else "N/A"
        print(f"{params}: {len(results)} results (total: {total}), first: {first}")
    except Exception as e:
        print(f"{params}: ERROR {e}")
