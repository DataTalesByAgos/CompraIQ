"""
audit_labels.py
---------------
Audita las etiquetas bootstrap comparándolas contra las predicciones del modelo.

Casos de interés para revisión manual:

  1. model_pred != bootstrap_label AND confidence >= 0.80
     → El modelo está MUY seguro de una categoría diferente a la bootstrap.
       Candidatos excelentes a etiquetas incorrectas en el bootstrap.

  2. model_pred != bootstrap_label AND confidence < 0.80
     → Desacuerdo con baja confianza. Pueden ser ambigüedades genuinas
       o errores del modelo. Requieren revisión más cuidadosa.

Uso:
    docker compose run --rm app python audit_labels.py
    docker compose run --rm app python audit_labels.py --export  # exporta CSV
"""

import os
import re
import sys
import csv
import pickle
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# ── Import bootstrap logic from train_model ──────────────────────────────────
# We replicate the CATEGORIES + keyword index here so this script is standalone.
# Keep in sync with train_model.py and transform/classify.py.

CATEGORIES = {
    "Lácteos": [
        "dulce de leche", "port salut", "queso crema", "queso cremoso", "queso rallado",
        "leche", "yogur", "queso", "manteca", "ricota", "musarela", "muzzarella",
        "tregar", "milk", "sancor", "serenisima", "ddl", "cremoso", "activia",
    ],
    "Básicos de Almacén": [
        "caldo de carne", "caldo de verdura", "caldo de pollo",
        "pan rallado", "harina de maiz", "pasta dental",
        "arroz", "fideos", "fideo", "aceite", "azucar", "harina",
        "puré", "salsa", "legumbres", "polenta", "lentejas", "garbanzos", "arvejas",
        "mayonesa", "ketchup", "mostaza", "vinagre", "caldo", "orégano",
        "pimienta", "pimentón", "aderezo", "matarazzo", "lucchetti",
    ],
    "Bebidas con Alcohol": [
        "cerveza", "vino", "fernet", "whisky", "champagne", "licor", "sidra",
        "malbec", "cabernet", "vodka", "aperitivo", "campari",
        "heineken", "quilmes", "stella artois", "brahma",
    ],
    "Bebidas sin Alcohol": [
        "coca cola zero", "coca cola light", "coca cola",
        "villa del sur", "gaseosa", "agua", "jugo", "pepsi", "tonica",
        "aquarius", "levite", "sprite", "fanta", "soda", "terma",
        "cepita", "villavicencio",
    ],
    "Frutas y Verduras": [
        "papa frita",
        "papa", "cebolla", "tomate", "manzana", "banana", "lechuga", "naranja",
        "zanahoria", "limon", "palta", "frutilla", "pera", "verdura", "fruta",
        "zapallo", "espinaca", "acelga", "morrón",
    ],
    "Carnicería y Pescadería": [
        "medallón de carne", "milanesa de pollo", "milanesa de carne",
        "pechuga de pollo", "filet de merluza",
        "carne", "pollo", "paty", "pescado", "asado", "lomo", "peceto", "milanesa",
        "bife", "vacio", "matambre", "cerdo", "chorizo", "merluza", "salmon", "atun", "swift",
    ],
    "Panadería y Galletitas": [
        "pan de hamburguesa", "pan de molde", "pan lactal", "pan integral",
        "pan dulce", "pan negro", "pan blanco", "pan sandwich", "pan triple",
        "galletitas oreo", "galletitas", "alfajor", "lactal", "budin", "magdalenas",
        "chocolinas", "criollitas", "tostadas", "bizcochitos", "artesano", "fargo", "bimbo",
        "pan",
    ],
    "Cuidado Personal": [
        "protector solar", "papel higienico", "jabon tocador", "pasta dental",
        "shampoo", "desodorante", "dentifrico", "pañales",
        "colgate", "dove", "rexona", "toallitas", "acondicionador",
    ],
    "Limpieza del Hogar": [
        "jabon liquido", "rollo cocina",
        "detergente", "lavandina", "desinfectante", "suavizante",
        "skip", "vivere", "cif", "poett", "procacen", "trapo", "magistral", "ayudín",
    ],
    "Congelados y Otros": [
        "papas fritas congeladas", "super congelados",
        "helado", "congelados", "nuggets", "patitas", "franchesco",
    ],
}


def _build_kw_index():
    entries = []
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if " " in kw:
                pattern = re.compile(re.escape(kw), re.IGNORECASE)
            else:
                pattern = re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
            entries.append((kw, category, pattern))
    entries.sort(key=lambda e: len(e[0]), reverse=True)
    return entries


_KW_INDEX = _build_kw_index()


def bootstrap_label(name: str) -> str | None:
    for _kw, category, pattern in _KW_INDEX:
        if pattern.search(name):
            return category
    return None


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "prices"),
    )


def main():
    export_csv = "--export" in sys.argv

    model_path = os.path.join("model", "category_model.pkl")
    if not os.path.exists(model_path):
        print("Error: No trained model found. Run 'python train_model.py' first.")
        return

    print("Loading model...")
    with open(model_path, "rb") as f:
        pipeline = pickle.load(f)

    print("Fetching products from DB...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM dim_product ORDER BY nombre")
    all_names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    print(f"Total products: {len(all_names)}")

    # Predict all at once (faster)
    probas = pipeline.predict_proba(all_names)
    preds = pipeline.classes_[probas.argmax(axis=1)]
    confs = probas.max(axis=1)

    # Audit: find where model disagrees with bootstrap
    disagreements = []
    unlabeled = []

    for name, pred, conf in zip(all_names, preds, confs):
        bl = bootstrap_label(name)
        if bl is None:
            unlabeled.append(name)
            continue
        if pred != bl:
            disagreements.append({
                "product":         name,
                "bootstrap_label": bl,
                "model_pred":      pred,
                "confidence":      float(conf),
            })

    # Sort by confidence descending (high-confidence disagreements = likely wrong bootstrap)
    disagreements.sort(key=lambda x: -x["confidence"])

    total_labeled = len(all_names) - len(unlabeled)
    pct = len(disagreements) / total_labeled * 100 if total_labeled else 0

    print(f"\nUnlabeled by bootstrap (no keyword match): {len(unlabeled)}")
    print(f"Bootstrap-labeled products:               {total_labeled}")
    print(f"Disagreements (model != bootstrap):       {len(disagreements)} ({pct:.1f}%)")

    # Split by confidence threshold
    high_conf = [d for d in disagreements if d["confidence"] >= 0.80]
    low_conf  = [d for d in disagreements if d["confidence"] <  0.80]

    print(f"\n  High-confidence disagreements (>=0.80): {len(high_conf)}")
    print(f"  → These are the strongest candidates for WRONG bootstrap labels.\n")
    print(f"  Low-confidence  disagreements ( <0.80): {len(low_conf)}")
    print(f"  → These may be genuine ambiguities or model uncertainty.\n")

    # ── High-confidence disagreements ─────────────────────────────────────────
    if high_conf:
        print("=" * 110)
        print("HIGH-CONFIDENCE DISAGREEMENTS  (model very sure, bootstrap differs)  — REVIEW THESE FIRST")
        print("=" * 110)
        print(f"{'Product':<55} {'Bootstrap':<25} {'Model Pred':<25} {'Conf':>6}")
        print("-" * 110)
        for d in high_conf:
            print(f"{d['product'][:54]:<55} {d['bootstrap_label']:<25} {d['model_pred']:<25} {d['confidence']:.2f}")

    # ── Low-confidence disagreements ──────────────────────────────────────────
    if low_conf:
        print(f"\n{'='*110}")
        print("LOW-CONFIDENCE DISAGREEMENTS  (model unsure, bootstrap differs)  — REVIEW AFTER")
        print("=" * 110)
        print(f"{'Product':<55} {'Bootstrap':<25} {'Model Pred':<25} {'Conf':>6}")
        print("-" * 110)
        for d in low_conf[:40]:  # cap at 40 to avoid noise flood
            print(f"{d['product'][:54]:<55} {d['bootstrap_label']:<25} {d['model_pred']:<25} {d['confidence']:.2f}")
        if len(low_conf) > 40:
            print(f"  ... and {len(low_conf) - 40} more (use --export to see all)")

    # ── CSV export ────────────────────────────────────────────────────────────
    if export_csv:
        csv_path = "model/label_audit.csv"
        os.makedirs("model", exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["product", "bootstrap_label", "model_pred", "confidence"])
            writer.writeheader()
            writer.writerows(disagreements)
        print(f"\nExported {len(disagreements)} disagreements to '{csv_path}'")
        print("Open it in Excel or Google Sheets to assign correct labels manually.")

    # ── Breakdown by bootstrap label ──────────────────────────────────────────
    print(f"\n{'='*60}")
    print("DISAGREEMENTS BY BOOTSTRAP LABEL")
    print("=" * 60)
    from collections import Counter
    bl_counts = Counter(d["bootstrap_label"] for d in disagreements)
    for label, count in bl_counts.most_common():
        total_in_cat = sum(1 for n in all_names if bootstrap_label(n) == label)
        pct_cat = count / total_in_cat * 100 if total_in_cat else 0
        print(f"  {label:<28} {count:>3} disagreements / {total_in_cat:>4} total  ({pct_cat:.0f}%)")


if __name__ == "__main__":
    main()
