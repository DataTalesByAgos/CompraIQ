import os
import re
import pickle

_MODEL = None
_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model", "category_model.pkl")

# Must be kept in sync with train_model.py
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


def _build_keyword_index() -> list[tuple[str, str, re.Pattern]]:
    """
    Builds a flat (keyword, category, pattern) list sorted by keyword length descending.
    Longest keywords are tried first so multi-word phrases beat lone words.
    Single-word keywords use word boundaries to avoid substring false matches.
    """
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


_KW_INDEX = _build_keyword_index()


def _fallback_predict(product_name: str) -> str:
    """Keyword matching fallback using longest-match-wins with word boundaries."""
    for _kw, category, pattern in _KW_INDEX:
        if pattern.search(product_name):
            return category
    return "Otros / Sin Categoria"


CONFIDENCE_THRESHOLD = 0.80


def predict_category(product_name: str) -> str:
    """
    Predicts product category using the trained Logistic Regression model.
    Applies a confidence threshold: if the model's top prediction probability
    is below CONFIDENCE_THRESHOLD, falls back to keyword matching.
    Falls back entirely to keyword matching if the model isn't trained yet.
    """
    global _MODEL

    if not product_name:
        return "Otros / Sin Categoria"

    # Lazy load the model from disk
    if _MODEL is None:
        if os.path.exists(_MODEL_PATH):
            try:
                with open(_MODEL_PATH, "rb") as f:
                    _MODEL = pickle.load(f)
            except Exception as e:
                print(f"    [WARN] Failed to load ML model from {_MODEL_PATH}: {e}")

    # If loaded successfully, make prediction with confidence check
    if _MODEL is not None:
        try:
            proba = _MODEL.predict_proba([product_name])[0]
            max_conf = proba.max()

            if max_conf >= CONFIDENCE_THRESHOLD:
                pred = _MODEL.classes_[proba.argmax()]
                return str(pred)
            else:
                # Low confidence — trust keyword rules instead
                fallback = _fallback_predict(product_name)
                if fallback != "Otros / Sin Categoria":
                    return fallback
                # Accept low-confidence ML prediction as last resort
                pred = _MODEL.classes_[proba.argmax()]
                return str(pred)
        except Exception as e:
            print(f"    [WARN] Prediction error: {e}")

    # Fallback to rules
    return _fallback_predict(product_name)
