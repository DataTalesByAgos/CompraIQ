"""
Category Probe Script
Fetches first 200 products from each supermarket and shows all categories found.
"""
import json, urllib.request, sys
from collections import defaultdict

HEADERS = {"User-Agent": "Mozilla/5.0"}

STORES = [
    ("🛒 Carrefour", "https://www.carrefour.com.ar/api/catalog_system/pub/products/search"),
    ("🛒 Dia",       "https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search"),
    ("🛒 Jumbo",     "https://www.jumbo.com.ar/api/catalog_system/pub/products/search"),
    ("🛒 Disco",     "https://www.disco.com.ar/api/catalog_system/pub/products/search"),
    ("🛒 Vea",       "https://www.vea.com.ar/api/catalog_system/pub/products/search"),
]

# Coto uses Constructor.io — different format
COTO_API = "https://ac.cnstrc.com/search/"
COTO_KEY = "key_r6xzz4IAoTWcipni"
COTO_QUERIES = ["leche", "arroz", "pan", "aceite", "carne", "pollo", "fideos", "harina",
                "yogur", "queso", "gaseosa", "detergente", "jabon", "shampoo", "papel"]

def probe_vtex(name, base_url, sample_size=200):
    print(f"\n{'='*70}")
    print(f"{name}")
    print(f"{'='*70}")
    
    top_cats = defaultdict(lambda: defaultdict(int))
    pages_needed = (sample_size + 49) // 50
    
    for page in range(pages_needed):
        _from = page * 50
        _to = _from + 49
        url = f"{base_url}?_from={_from}&_to={_to}"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
        except Exception as e:
            print(f"  Error page {page}: {e}")
            break
        
        for item in data:
            cats = item.get("categories", [])
            if not cats:
                top_cats["(sin categoria)"]["(sin subcategoria)"] += 1
                continue
            full_path = cats[0].strip("/")
            parts = full_path.split("/")
            top = parts[0] if parts else "(sin)"
            sub = parts[1] if len(parts) > 1 else "(raiz)"
            top_cats[top][sub] += 1
        
        if len(data) < 50:
            break
    
    total = sum(sum(v.values()) for v in top_cats.values())
    print(f"  Total: {total} productos, {len(top_cats)} categorías principales\n")
    
    for top, subs in sorted(top_cats.items()):
        sub_total = sum(subs.values())
        pct = sub_total / total * 100
        print(f"  📁 {top} ({sub_total} prods, {pct:.0f}%)")
        for sub, count in sorted(subs.items(), key=lambda x: -x[1]):
            print(f"      └─ {sub}: {count}")


def probe_coto():
    print(f"\n{'='*70}")
    print("🛒 Coto (Constructor.io)")
    print(f"{'='*70}")
    
    groups_found = defaultdict(int)
    
    for query in COTO_QUERIES:
        url = f"{COTO_API}{query}?key={COTO_KEY}&num_results_per_page=50"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            results = data.get("response", {}).get("results", [])
        except Exception as e:
            continue
        
        for item in results:
            item_data = item.get("data", {})
            groups = item_data.get("groups", [])
            if groups:
                for g in groups:
                    display = g.get("display_name", "N/A")
                    groups_found[display] += 1
            else:
                groups_found["(sin grupo)"] += 1
    
    total = sum(groups_found.values())
    print(f"  Total: {total} productos, {len(groups_found)} grupos\n")
    for g, count in sorted(groups_found.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  📁 {g}: {count} ({pct:.0f}%)")


# Run
for name, url in STORES:
    probe_vtex(name, url)

probe_coto()

print(f"\n{'='*70}")
print("DONE")
print(f"{'='*70}")
