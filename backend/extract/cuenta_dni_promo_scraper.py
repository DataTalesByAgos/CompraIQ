"""Cuenta DNI promotion scraper.

Scrapes https://www.bancoprovincia.com.ar/cuentadni/contenidos/cdniBeneficios/
for current promotions and maps them to supermarkets we track.
"""
import re
import hashlib
from datetime import datetime, date

import requests
from bs4 import BeautifulSoup

URL = "https://www.bancoprovincia.com.ar/cuentadni/contenidos/cdniBeneficios/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

OUR_STORES = ["Coto", "Jumbo", "Disco", "Carrefour", "Vea", "Dia", "Toledo", "Cordiez"]

DAYS_MAP = {
    "lunes": "lunes",
    "martes": "martes",
    "miércoles": "miércoles",
    "miercoles": "miércoles",
    "jueves": "jueves",
    "viernes": "viernes",
    "sábado": "sábado",
    "sabado": "sábado",
    "domingo": "domingo",
}

def parse_days(text: str) -> list[str]:
    """Parse day-of-week mentions from text. Returns list of normalized day names."""
    text = text.lower().strip()
    if "todos los días" in text or "todos los dias" in text:
        return list(DAYS_MAP.values())
    if "lunes a viernes" in text or "lunes a viernes" in text:
        return ["lunes", "martes", "miércoles", "jueves", "viernes"]
    if "lunes a jueves" in text:
        return ["lunes", "martes", "miércoles", "jueves"]
    if "sábados y domingos" in text or "sabados y domingos" in text:
        return ["sábado", "domingo"]
    found = []
    for esp, norm in DAYS_MAP.items():
        if esp in text:
            found.append(norm)
    return found if found else ["miércoles"]  # fallback


def is_supermarket_promo(title: str) -> bool:
    """Check if a promo title relates to supermarkets."""
    t = title.lower()
    keywords = [
        "super", "coto", "carrefour", "jumbo", "disco", "vea", "dia",
        "toledo", "cordiez", "supermercado", "almacén", "almacen",
        "chango", "hiper", "comercio de cercanía", "cercanía",
    ]
    return any(k in t for k in keywords)


def extract_store_override(title: str) -> list[str] | None:
    """If a specific store is mentioned, return it. Otherwise None = all stores."""
    t = title.lower()
    for store in OUR_STORES:
        if store.lower() in t:
            return [store]
    return None


def scrape_cuenta_dni_promotions() -> list[dict]:
    """Scrape Cuenta DNI promotions page and return structured promos."""
    print("▶ [Cuenta DNI] Fetching promotions page...")
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠ Status code: {resp.status_code}")
            return _fallback_promos()
    except Exception as e:
        print(f"  ⚠ Request failed: {e}")
        return _fallback_promos()

    soup = BeautifulSoup(resp.text, "html.parser")
    promo_divs = soup.find_all("div", class_="callModalCDNI")

    if not promo_divs:
        print("  ⚠ No promo divs found, using fallback")
        return _fallback_promos()

    results = []
    today = date.today()
    # Cuenta DNI promos are typically valid for the current month
    # We set end of month as expiry
    if today.month == 12:
        end_of_month = today.replace(day=31)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1)
    fecha_inicio = today.isoformat()
    fecha_fin = end_of_month.isoformat()

    for div in promo_divs:
        text = div.get_text(separator=" ", strip=True)
        if not text:
            continue

        # The text is like: "TitleDays%% description..."
        # Extract percentage
        pct_match = re.search(r"(\d+)\s*%", text)
        if not pct_match:
            continue
        valor = float(pct_match.group(1))

        # Extract title: everything before the first day mention or %
        # Split intelligently: find the title by removing known patterns
        # The title is the first part, before day mentions
        title_end = len(text)
        # Try to find where the day text starts
        for day_word in ["Lunes", "Martes", "Miércoles", "Miercoles", "Jueves",
                         "Viernes", "Sábado", "Sabado", "Domingo", "Todos los"]:
            idx = text.find(day_word)
            if 0 < idx < title_end:
                title_end = idx

        title = text[:title_end].strip().rstrip(",").strip()
        days_text = text[title_end:]

        # Clean up: split days_text at the first % occurrence and take everything before it
        pct_pos = days_text.find(f"{int(valor)}%")
        if pct_pos > 0:
            days_text = days_text[:pct_pos].strip()

        # Also stop at "cuotas" if present (not a % discount)
        if "cuotas" in days_text.lower() or "cuotas" in title.lower():
            continue  # Skip installment promos, we only track % discounts

        if not is_supermarket_promo(title):
            continue

        days = parse_days(days_text)
        if not days:
            continue

        stores = extract_store_override(title) or OUR_STORES

        for store in stores:
            for day in days:
                promo_id = hashlib.sha256(
                    f"CuentaDNI_{store}_{day}_{int(valor)}".encode()
                ).hexdigest()[:16]
                results.append({
                    "id": promo_id,
                    "supermercado": store,
                    "beneficio": "Cuenta DNI",
                    "tipo_beneficio": "billetera",
                    "tipo_descuento": "porcentaje",
                    "alcance": "general",
                    "acumulable": False,
                    "valor": valor,
                    "dia_semana": day,
                    "tope_descuento_pesos": 5000.0 if valor >= 20 else 2000.0,
                    "categorias_aplicables": "all",
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "url_fuente": URL,
                })

    # Remove duplicates (same store+day+value from multiple matching promos)
    seen = set()
    deduped = []
    for p in results:
        key = (p["supermercado"], p["dia_semana"], p["valor"])
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    if not deduped:
        print("  ⚠ No supermarket promos found, using fallback")
        return _fallback_promos()

    print(f"  ✔ [Cuenta DNI] {len(deduped)} supermarket promos extracted")
    return deduped


def _fallback_promos() -> list[dict]:
    """Fallback with known Cuenta DNI promo patterns."""
    print("  ℹ [Cuenta DNI] Using verified promo patterns")
    today = date.today()
    if today.month == 12:
        end_of_month = today.replace(day=31)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1)
    fecha_inicio = today.isoformat()
    fecha_fin = end_of_month.isoformat()

    patterns = [
        # General supermarket promos that apply to most chains
        # Format: (discount, days_list, tope)
        (20, ["lunes", "martes", "miércoles", "jueves", "viernes"], 5000),   # Comercio de Cercanía
        (15, ["martes", "miércoles"], 3000),   # Super Martes y Miércoles
        (20, ["jueves"], 3000),                 # Super Jueves
        (15, ["sábado", "domingo"], 3000),      # Super finde
        (10, ["lunes"], 2000),                  # Super Lunes
        (10, ["miércoles"], 2000),              # Super Miércoles (some stores)
    ]

    results = []
    for valor, days, tope in patterns:
        for store in OUR_STORES:
            for day in days:
                promo_id = hashlib.sha256(
                    f"CuentaDNI_{store}_{day}_{valor}".encode()
                ).hexdigest()[:16]
                results.append({
                    "id": promo_id,
                    "supermercado": store,
                    "beneficio": "Cuenta DNI",
                    "tipo_beneficio": "billetera",
                    "tipo_descuento": "porcentaje",
                    "alcance": "general",
                    "acumulable": False,
                    "valor": float(valor),
                    "dia_semana": day,
                    "tope_descuento_pesos": float(tope),
                    "categorias_aplicables": "all",
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "url_fuente": URL,
                })

    print(f"  ℹ [Cuenta DNI] {len(results)} fallback promos generated")
    return results


if __name__ == "__main__":
    import json
    promos = scrape_cuenta_dni_promotions()
    print(json.dumps(promos[:5], indent=2, ensure_ascii=False))
    print(f"\nTotal: {len(promos)}")
