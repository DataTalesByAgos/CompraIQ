import csv
import json
import os
import io
import re
import zipfile
import requests
import tempfile
from datetime import datetime

from .vtex_base import NON_FOOD_KEYWORDS

CACHE_DIR = os.environ.get("SEPA_CACHE_DIR", os.path.join(tempfile.gettempdir(), "sepa_cache"))

SEPA_RESOURCE_IDS = {
    "monday":    "0a9069a9-06e8-4f98-874d-da5578693290",
    "tuesday":   "9dc06241-cc83-44f8-8e25-c9b1636b8bc8",
    "wednesday": "1e92cd42-4f94-4071-a165-62c4cb2ce23c",
    "thursday":  "d076720f-a7f0-4af8-b1d6-1b99d5a90c14",
    "friday":    "91bc072a-4726-44a1-85ec-4a8467aad27e",
    "saturday":  "b3c3da5d-213d-41e7-8d74-f23fda0a3c30",
    "sunday":    "f8e75128-515a-436e-bf8d-5c63a62f2005",
}

SEPA_BASE_URL = (
    "https://datos.produccion.gob.ar/dataset/"
    "6f47ec76-d1ce-4e34-a7e1-621fe9b1d0b5/resource/{resource_id}/download/sepa_{day_name}.zip"
)

SEPA_CHAIN_MAP: dict[tuple[int, int], str] = {
    (2, 1):  "La Anonima",
    (13, 1): "Cooperativa Obrera",
    (11, 1): "Changomas",
    (11, 5): "Changomas",
    (47, 1): "Unicoop",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def _day_name() -> str:
    return datetime.now().strftime("%A").lower()

def _is_grocery_by_name(name: str) -> bool:
    lowered = name.lower()
    for kw in NON_FOOD_KEYWORDS:
        if kw in lowered:
            return False
    return True

def _productos_csv_path(inner_zip: zipfile.ZipFile) -> str | None:
    for candidate in ("productos.csv", "./productos.csv"):
        try:
            inner_zip.getinfo(candidate)
            return candidate
        except KeyError:
            pass
    for name in inner_zip.namelist():
        if name.endswith("/productos.csv") or name == "productos.csv":
            return name
    return None

def _parse_sepa_price(raw: str) -> float | None:
    s = raw.strip().replace("$", "").replace(",", ".")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None

def _parse_sepa_presentacion(cantidad: str, unidad: str) -> str:
    c = cantidad.strip() if cantidad else ""
    u = unidad.strip() if unidad else ""
    if c and u:
        return f"{c} {u}"
    if c:
        return c
    return u

def _cache_path() -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    day = _day_name()
    return os.path.join(CACHE_DIR, f"sepa_{day}.json")

def _load_from_cache() -> list[dict] | None:
    path = _cache_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"    [SEPA] Cache cargado: {len(data)} productos")
        return data
    except Exception as e:
        print(f"    [SEPA] Error leyendo cache: {e}")
        return None

def _save_to_cache(products: list[dict]) -> None:
    path = _cache_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False)
        print(f"    [SEPA] Cache guardado: {path}")
    except Exception as e:
        print(f"    [SEPA] Error guardando cache: {e}")

def _download_sepa_zip(target_path: str) -> bool:
    day = _day_name()
    resource_id = SEPA_RESOURCE_IDS.get(day)
    if not resource_id:
        return False
    url = SEPA_BASE_URL.format(resource_id=resource_id, day_name=day)
    print(f"    [SEPA] Descargando ~300MB...")
    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=300) as r:
            if r.status_code != 200:
                print(f"    [SEPA] Error HTTP {r.status_code}")
                return False
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            last_pct = -1
            with open(target_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded * 100 // total
                            if pct != last_pct:
                                last_pct = pct
                                print(f"\r    [SEPA] {pct}% ({downloaded//1024//1024}MB / {total//1024//1024}MB)", end="")
            print()
        print(f"    [SEPA] Descarga completa")
        return True
    except Exception as e:
        print(f"    [SEPA] Error en descarga: {e}")
        return False

def _parse_inner_zip(inner_bytes: bytes, supermarket_name: str) -> list[dict]:
    products = []
    try:
        inner = zipfile.ZipFile(io.BytesIO(inner_bytes))
    except Exception as e:
        print(f"    [SEPA] Error abriendo inner ZIP {supermarket_name}: {e}")
        return products

    csv_path = _productos_csv_path(inner)
    if not csv_path:
        print(f"    [SEPA] No se encontró productos.csv en {supermarket_name}")
        return products

    try:
        raw = inner.read(csv_path)
    except Exception as e:
        print(f"    [SEPA] Error leyendo CSV en {supermarket_name}: {e}")
        return products

    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        text = raw.decode("latin-1", errors="replace")

    lines = text.splitlines()
    if not lines:
        return products

    if lines[-1].startswith("Ultima actualizaci"):
        lines = lines[:-1]

    reader = csv.DictReader(lines, delimiter="|")
    seen_ids: set[str] = set()

    for row in reader:
        id_producto = row.get("id_producto", "").strip()
        productos_ean = row.get("productos_ean", "").strip()
        ean = productos_ean if (productos_ean and productos_ean not in ("1", "0", "") and len(productos_ean) >= 8) else None

        if id_producto:
            if id_producto in seen_ids:
                continue
            seen_ids.add(id_producto)

        name = row.get("productos_descripcion", "").strip()
        if not name:
            continue
        if not _is_grocery_by_name(name):
            continue

        price_raw = row.get("productos_precio_lista", "").strip()
        if not price_raw:
            price_raw = row.get("productos_precio_unitario_promo1", "").strip()
        price = _parse_sepa_price(price_raw)
        if price is None or price <= 0:
            continue

        cantidad = row.get("productos_cantidad_presentacion", "").strip()
        unidad = row.get("productos_unidad_medida_presentacion", "").strip()
        presentacion = _parse_sepa_presentacion(cantidad, unidad)

        products.append({
            "producto":     name,
            "categoria":    "",
            "precio":       str(price),
            "presentacion": presentacion,
            "ean":          ean,
            "supermercado": supermarket_name,
            "fuente":       "sepa",
        })

    inner.close()
    return products

def extract_sepa() -> list[dict]:
    if not os.environ.get("SEPA_ENABLED", "").lower() in ("1", "true", "yes"):
        print("    [SEPA] Deshabilitado (SEPA_ENABLED != true)")
        return []

    cached = _load_from_cache()
    if cached is not None:
        return cached

    print("    [SEPA] Iniciando extracción...")
    os.makedirs(CACHE_DIR, exist_ok=True)
    zip_path = os.path.join(CACHE_DIR, f"sepa_{_day_name()}.zip")

    all_products: list[dict] = []

    if not os.path.exists(zip_path):
        if not _download_sepa_zip(zip_path):
            print("    [SEPA] No se pudo descargar el ZIP. Abortando.")
            return all_products

    print(f"    [SEPA] Procesando ZIP...")
    try:
        with zipfile.ZipFile(zip_path, "r") as outer:
            inner_names = outer.namelist()
            inner_zips = [n for n in inner_names if n.endswith(".zip")]
            print(f"    [SEPA] {len(inner_zips)} inner ZIPs en el archivo")

            for inner_name in inner_zips:
                match = re.search(r"comercio-sepa-(\d+)", inner_name)
                if not match:
                    continue
                comercio_id = int(match.group(1))

                supermarket_name = next(
                    (name for (c_id, b_id), name in SEPA_CHAIN_MAP.items() if c_id == comercio_id),
                    None
                )
                if not supermarket_name:
                    continue

                print(f"    [SEPA] Procesando comercio {comercio_id} -> {supermarket_name}")
                try:
                    inner_bytes = outer.read(inner_name)
                    chain_products = _parse_inner_zip(inner_bytes, supermarket_name)
                    print(f"    [SEPA]   {supermarket_name}: {len(chain_products)} productos")
                    all_products.extend(chain_products)
                except Exception as e:
                    print(f"    [SEPA]   Error en {supermarket_name}: {e}")

    except Exception as e:
        print(f"    [SEPA] Error general: {e}")

    print(f"    [SEPA] Total: {len(all_products)} productos")
    if all_products:
        _save_to_cache(all_products)
    return all_products
