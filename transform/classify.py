import os
import pickle

_MODEL = None
_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model", "category_model.pkl")

# Static keyword mapping fallback dictionary
CATEGORIES = {
    "Lácteos": [
        "leche", "yogur", "queso", "manteca", "crema", "tregar", "milk", "sancor", "serenisima", 
        "ricota", "dulce de leche", "ddl", "cremoso", "port salut", "musarela", "muzzarella", "activia"
    ],
    "Básicos de Almacén": [
        "arroz", "fideos", "aceite", "sal", "azucar", "harina", "puré", "salsa", "legumbres", 
        "fideo", "polenta", "lentejas", "garbanzos", "arvejas", "mayonesa", "ketchup", "mostaza", 
        "vinagre", "caldo", "orégano", "pimienta", "pimentón", "aderezo", "gallo", "matarazzo", "lucchetti"
    ],
    "Bebidas con Alcohol": [
        "cerveza", "vino", "fernet", "gin", "whisky", "champagne", "licor", "sidra", "malbec", 
        "cabernet", "brut", "vodka", "aperitivo", "campari", "heineken", "quilmes", "stella", "brahma", "corona"
    ],
    "Bebidas sin Alcohol": [
        "gaseosa", "agua", "jugo", "coca", "pepsi", "tonica", "aquarius", "levite", "sprite", 
        "fanta", "soda", "pomelo", "terma", "cepita", "villavicencio", "villa del sur"
    ],
    "Frutas y Verduras": [
        "papa", "cebolla", "tomate", "manzana", "banana", "lechuga", "naranja", "zanahoria", 
        "limon", "palta", "frutilla", "pera", "verdura", "fruta", "zapallo", "espinaca", "acelga", "morrón"
    ],
    "Carnicería y Pescadería": [
        "carne", "pollo", "hamburguesa", "paty", "pescado", "asado", "lomo", "peceto", "milanesa", 
        "bife", "vacio", "matambre", "cerdo", "chorizo", "merluza", "salmon", "atun", "swift"
    ],
    "Panadería y Galletitas": [
        "pan", "galletitas", "alfajor", "lactal", "budin", "magdalenas", "galletitas oreo", 
        "chocolinas", "criollitas", "tostadas", "bizcochitos", "pan rallado", "artesano", "fargo", "bimbo"
    ],
    "Cuidado Personal": [
        "shampoo", "desodorante", "jabon tocador", "dentifrico", "pasta dental", "pañales", 
        "papel higienico", "colgate", "dove", "rexona", "toallitas", "protector solar", "acondicionador"
    ],
    "Limpieza del Hogar": [
        "detergente", "lavandina", "desinfectante", "jabon liquido", "suavizante", "rollo cocina", 
        "ala", "skip", "vivere", "cif", "poett", "procacen", "trapo", "magistral", "ayudín"
    ],
    "Congelados y Otros": [
        "helado", "congelados", "nuggets", "papas fritas congeladas", "patitas", "super congelados", "franchesco"
    ]
}

def _fallback_predict(product_name: str) -> str:
    """Basic keyword matching fallback if scikit-learn model is missing."""
    name_lower = product_name.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in name_lower:
                return category
    return "Otros / Sin Categoria"

def predict_category(product_name: str) -> str:
    """
    Predicts product category using the trained Logistic Regression model.
    Falls back to keyword matching if the model isn't trained yet.
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
                
    # If loaded successfully, make prediction
    if _MODEL is not None:
        try:
            pred = _MODEL.predict([product_name])
            return str(pred[0])
        except Exception as e:
            print(f"    [WARN] Prediction error: {e}")
            
    # Fallback to rules
    return _fallback_predict(product_name)
