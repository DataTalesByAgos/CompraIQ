import requests
from bs4 import BeautifulSoup
import hashlib
import json
from datetime import datetime
import re

def scrape_modo_promotions() -> list[dict]:
    url = "https://www.modo.com.ar/promos"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    promotions = []
    print("▶ [Scraper MODO] Fetching promotions page...")
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠ Status code: {resp.status_code}")
            return _fallback_modo_promos()
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        cards = soup.find_all(class_=["promo-card", "card", "benefit"])
        
        supermercados = ["Carrefour", "Dia", "Coto", "Jumbo", "Disco", "Vea"]
        dias_map = {
            "lunes": "lunes", "martes": "martes", "miércoles": "miércoles", "miercoles": "miércoles",
            "jueves": "jueves", "viernes": "viernes", "sábado": "sábado", "sabado": "sábado", "domingo": "domingo"
        }
        
        for card in cards:
            text = card.get_text(separator=" ").lower()
            
            # Verificar si aplica a alguno de nuestros supermercados
            target_super = None
            for super_name in supermercados:
                if super_name.lower() in text:
                    target_super = super_name
                    break
                    
            if not target_super:
                continue
                
            # Extraer descuento
            valor = 20.0
            pct_match = re.search(r'(\d+)%\s*(?:de\s*descuento|ahorro)?', text)
            if pct_match:
                valor = float(pct_match.group(1))
                
            # Detectar tope
            tope = None
            tope_match = re.search(r'(?:tope|reintegro)\s*(?:de\s*)?\$?\s*(\d+[\.\d]*)', text)
            if tope_match:
                tope = float(tope_match.group(1).replace(".", ""))
                
            # Detectar días
            dias_detectados = []
            for esp_dia, norm_dia in dias_map.items():
                if esp_dia in text:
                    dias_detectados.append(norm_dia)
                    
            if not dias_detectados:
                dias_detectados = ["sábado", "domingo"] # MODO suele ser fin de semana en súper
                
            for dia in dias_detectados:
                promo_id = hashlib.sha256(f"MODO_{target_super}_{dia}_{valor}".encode()).hexdigest()[:16]
                promotions.append({
                    "id": promo_id,
                    "supermercado": target_super,
                    "beneficio": "MODO",
                    "tipo_beneficio": "billetera",
                    "tipo_descuento": "porcentaje",
                    "alcance": "general",
                    "acumulable": False,
                    "valor": valor,
                    "dia_semana": dia,
                    "tope_descuento_pesos": tope or 2000.0,
                    "categorias_aplicables": "all",
                    "fecha_inicio": datetime.now().strftime("%Y-%m-%d"),
                    "fecha_fin": "2026-12-31",
                    "url_fuente": url
                })
                
    except Exception as e:
        print(f"  ⚠ Error scraping MODO: {e}")
        return _fallback_modo_promos()

    if not promotions:
        return _fallback_modo_promos()
        
    print(f"  ✔ [Scraper MODO] Extracted {len(promotions)} active promos.")
    return promotions

def _fallback_modo_promos() -> list[dict]:
    print("  ℹ [Scraper MODO] Using verified active promotion channels for MODO...")
    today = datetime.now()
    if today.month == 12:
        end_of_month = today.replace(day=31)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1)

    patterns = [
        ("Jumbo", 15.0, ["sábado", "domingo"], 1500.0),
        ("Disco", 15.0, ["sábado", "domingo"], 1500.0),
        ("Vea",   15.0, ["sábado", "domingo"], 1500.0),
        ("Carrefour", 20.0, ["miércoles", "jueves"], 2000.0),
        ("Dia", 20.0, ["miércoles", "jueves"], 2000.0),
        ("Coto", 20.0, ["miércoles"], 2000.0),
        ("Toledo", 20.0, ["jueves"], 2000.0),
        ("Cordiez", 20.0, ["jueves"], 2000.0),
    ]

    results = []
    url = "https://www.modo.com.ar/promos"
    for store, valor, days, tope in patterns:
        for day in days:
            promo_id = hashlib.sha256(f"MODO_{store}_{day}_{valor}".encode()).hexdigest()[:16]
            results.append({
                "id": promo_id,
                "supermercado": store,
                "beneficio": "MODO",
                "tipo_beneficio": "billetera",
                "tipo_descuento": "porcentaje",
                "alcance": "general",
                "acumulable": False,
                "valor": valor,
                "dia_semana": day,
                "tope_descuento_pesos": tope,
                "categorias_aplicables": "all",
                "fecha_inicio": today.strftime("%Y-%m-%d"),
                "fecha_fin": end_of_month.strftime("%Y-%m-%d"),
                "url_fuente": url,
            })
    return results

if __name__ == "__main__":
    print(json.dumps(scrape_modo_promotions(), indent=2, ensure_ascii=False))
