import os
import re
import pickle
import numpy as np
import mysql.connector
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

load_dotenv()

# Define keyword patterns for bootstrap labeling.
# IMPORTANT: use whole-word or multi-word phrases as much as possible.
# Ambiguous single words (e.g. 'sal', 'pan', 'carne') are superseded by longer
# multi-word keywords that appear in the same list — longest match always wins.
CATEGORIES = {
    "Lácteos": [
        "dulce de leche", "port salut", "queso crema", "queso cremoso", "queso rallado",
        "leche", "yogur", "queso", "manteca", "ricota", "musarela", "muzzarella",
        "tregar", "milk", "sancor", "serenisima", "ddl", "cremoso", "activia",
    ],
    "Básicos de Almacén": [
        # multi-word first to avoid false substring matches
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
        # 'coca cola zero' and 'coca cola light' are NOT alcohol — list before lone 'corona'
        "coca cola zero", "coca cola light", "coca cola",
        "villa del sur", "gaseosa", "agua", "jugo", "pepsi", "tonica",
        "aquarius", "levite", "sprite", "fanta", "soda", "terma",
        "cepita", "villavicencio",
    ],
    "Frutas y Verduras": [
        "papa frita",  # long form before 'papa' alone
        "papa", "cebolla", "tomate", "manzana", "banana", "lechuga", "naranja",
        "zanahoria", "limon", "palta", "frutilla", "pera", "verdura", "fruta",
        "zapallo", "espinaca", "acelga", "morrón",
    ],
    "Carnicería y Pescadería": [
        # multi-word before lone keywords to avoid 'pollo' matching 'caldo de pollo'
        "medallón de carne", "milanesa de pollo", "milanesa de carne",
        "pechuga de pollo", "filet de merluza",
        "carne", "pollo", "paty", "pescado", "asado", "lomo", "peceto", "milanesa",
        "bife", "vacio", "matambre", "cerdo", "chorizo", "merluza", "salmon", "atun", "swift",
    ],
    "Panadería y Galletitas": [
        # long forms first: 'pan de hamburguesa' beats lone 'hamburguesa' (Carnicería)
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


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "prices"),
    )


def _build_keyword_index() -> list[tuple[str, str, re.Pattern]]:
    """
    Builds a flat (keyword, category, pattern) list sorted by keyword length descending.
    Longest keywords are tried first so multi-word phrases beat lone words.
    Short single-word keywords use word boundaries (\b) to avoid substring false matches
    (e.g. 'sal' should NOT match inside 'salvado').
    """
    entries = []
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if " " in kw:
                # multi-word phrase: plain substring search is fine
                pattern = re.compile(re.escape(kw), re.IGNORECASE)
            else:
                # single word: require word boundaries
                pattern = re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
            entries.append((kw, category, pattern))
    # Sort by keyword length descending — longest/most-specific first
    entries.sort(key=lambda e: len(e[0]), reverse=True)
    return entries


_KW_INDEX = _build_keyword_index()


def bootstrap_labels(product_names: list[str]) -> list[tuple[str, str]]:
    """
    Assign target categories using longest-match-wins logic with word boundaries.
    For each product name, tries all keywords from longest to shortest and
    returns the first (most specific) match found.
    """
    labeled_data = []
    for name in product_names:
        matched_category = None
        for _kw, category, pattern in _KW_INDEX:
            if pattern.search(name):
                matched_category = category
                break
        if matched_category:
            labeled_data.append((name, matched_category))
    return labeled_data




def make_group_key(name: str) -> str:
    """
    Creates a group key from a product name to prevent data leakage.
    Strips size/quantity info (numbers + units) and normalizes to a base identifier.
    Example:
        "Leche Entera La Serenísima 1L"  → "leche entera la serenísima"
        "Leche Entera La Serenísima 500ml" → "leche entera la serenísima"
    """
    # Remove numbers, units, and extra punctuation
    cleaned = re.sub(r'\d+[\.,]?\d*\s*(g|kg|ml|l|lt|cc|un|x|pack|uni|u)\b', '', name, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b\d+\b', '', cleaned)             # remove standalone numbers
    cleaned = re.sub(r'[^a-záéíóúüñ\s]', '', cleaned.lower())  # keep only letters
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else name.lower()


def print_confusion_matrix(y_true, y_pred, labels):
    """Prints a readable text-based confusion matrix."""
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    label_width = max(len(l) for l in labels)
    title = "Actual / Predicted"
    col_headers = "  ".join(f"{l[:8]:>8}" for l in labels)
    print(f"\n{title:<{label_width}}  {col_headers}")
    print("-" * (label_width + 2 + len(col_headers) + 2))
    for i, label in enumerate(labels):
        row = "  ".join(f"{cm[i][j]:>8}" for j in range(len(labels)))
        print(f"{label:<{label_width}}  {row}")
    print()


def print_error_samples(X_val, y_val, y_pred, probas, classes, n=15):
    """Prints misclassified samples with predicted confidence."""
    errors = [
        (X_val[i], y_val[i], y_pred[i], probas[i].max())
        for i in range(len(y_val))
        if y_val[i] != y_pred[i]
    ]
    errors.sort(key=lambda x: -x[3])  # sort by confidence descending (most "confidently wrong" first)
    print(f"\n--- Misclassified Samples (top {min(n, len(errors))} of {len(errors)}) ---")
    print(f"{'Product':<55} {'True Label':<25} {'Predicted':<25} {'Conf':>6}")
    print("-" * 115)
    for product, true_label, pred_label, conf in errors[:n]:
        print(f"{product[:54]:<55} {true_label:<25} {pred_label:<25} {conf:.2f}")
    print()


def train():
    print("Connecting to DB to fetch training data...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM dim_product")
    product_names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    print(f"Total products in dim_product: {len(product_names)}")

    labeled_data = bootstrap_labels(product_names)
    print(f"Bootstrapped training records: {len(labeled_data)}")

    if len(labeled_data) < 20:
        print("Warning: Too few records to train model. Adding dummy training data to avoid errors.")
        dummy_data = []
        for cat, keywords in CATEGORIES.items():
            for kw in keywords[:3]:
                dummy_data.append((f"{kw.title()} Marca Ficticia", cat))
        labeled_data.extend(dummy_data)
        print(f"Total training records (with dummy data): {len(labeled_data)}")

    X = np.array([item[0] for item in labeled_data])
    y = np.array([item[1] for item in labeled_data])

    # --- Group-based split to prevent data leakage ---
    # Products with the same base name (stripped of size/unit) always go to the same split.
    groups = np.array([make_group_key(name) for name in X])
    unique_groups = len(set(groups))
    print(f"Unique product groups (after stripping size/unit variants): {unique_groups}")

    # Split: 80% dev (train+val), 20% test
    gss_test = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    dev_idx, test_idx = next(gss_test.split(X, y, groups=groups))
    X_dev, y_dev, groups_dev = X[dev_idx], y[dev_idx], groups[dev_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    # Split dev: 75% train, 25% validation (of dev set)
    gss_val = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train_idx, val_idx = next(gss_val.split(X_dev, y_dev, groups=groups_dev))
    X_train, y_train = X_dev[train_idx], y_dev[train_idx]
    X_val, y_val = X_dev[val_idx], y_dev[val_idx]

    print(f"Split (group-safe): {len(X_train)} train / {len(X_val)} validation / {len(X_test)} test")

    # Verify no leakage: check that no group appears in more than one split
    train_groups = set(groups[dev_idx][train_idx])
    val_groups   = set(groups[dev_idx][val_idx])
    test_groups  = set(groups[test_idx])
    leaked_tv = train_groups & val_groups
    leaked_tt = train_groups & test_groups
    leaked_vt = val_groups   & test_groups
    if leaked_tv or leaked_tt or leaked_vt:
        print(f"  [WARN] Leakage detected! train∩val={len(leaked_tv)} train∩test={len(leaked_tt)} val∩test={len(leaked_vt)}")
    else:
        print("  [OK] No data leakage detected between splits.")

    # --- Train pipeline ---
    print("\nTraining TF-IDF + Logistic Regression model...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True, max_features=10000)),
        ('clf', LogisticRegression(max_iter=1000, C=1.0, class_weight='balanced'))
    ])
    pipeline.fit(X_train, y_train)

    # --- Validation evaluation ---
    y_val_pred = pipeline.predict(X_val)
    y_val_proba = pipeline.predict_proba(X_val)
    classes = pipeline.classes_

    print(f"\n--- Validation Set Results ---")
    print(f"Accuracy: {accuracy_score(y_val, y_val_pred):.4f}\n")
    print(classification_report(y_val, y_val_pred))

    print_confusion_matrix(y_val, y_val_pred, classes)
    print_error_samples(X_val, y_val, y_val_pred, y_val_proba, classes, n=15)

    # --- Confidence distribution on validation set ---
    max_conf = y_val_proba.max(axis=1)
    above_threshold = (max_conf >= 0.80).sum()
    print(f"--- Confidence Analysis (threshold=0.80) ---")
    print(f"  Predictions above threshold: {above_threshold}/{len(y_val)} ({above_threshold/len(y_val)*100:.1f}%)")
    print(f"  Mean confidence: {max_conf.mean():.4f}")
    print(f"  Min confidence:  {max_conf.min():.4f}")
    print(f"  Max confidence:  {max_conf.max():.4f}\n")

    # --- Retrain final model on dev (train + val) for production ---
    print("Retraining final model on train + validation data for production...")
    pipeline.fit(X_dev, y_dev)

    # --- Save model and held-out test set ---
    os.makedirs("model", exist_ok=True)
    model_path = os.path.join("model", "category_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)

    test_data_path = os.path.join("model", "test_data.pkl")
    with open(test_data_path, "wb") as f:
        pickle.dump((X_test.tolist(), y_test.tolist()), f)

    print(f"Model successfully saved to '{model_path}'")
    print(f"Test set ({len(X_test)} records) saved to '{test_data_path}' for separate evaluation.")


if __name__ == "__main__":
    train()
