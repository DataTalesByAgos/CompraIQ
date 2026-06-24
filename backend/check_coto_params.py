import json, urllib.request

headers = {"User-Agent": "Mozilla/5.0"}
api_key = "key_r6xzz4IAoTWcipni"

# Try different parameter names for results per page
tests = [
    {"num_results": 50},
    {"num_results_per_page": 50},
    {"results_per_page": 50},
    {"limit": 50},
    {"size": 50},
    {"count": 50},
    {"max_results": 50},
    {"per_page": 50},
    {"page_size": 50},
    {"n": 50},
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
        print(f"{list(params.keys())[0]}={list(params.values())[0]}: {len(results)} results (total: {total})")
    except Exception as e:
        print(f"{list(params.keys())[0]}: ERROR {e}")
