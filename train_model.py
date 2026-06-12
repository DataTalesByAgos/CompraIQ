import os
import pickle
import mysql.connector
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

load_dotenv()

# Define keyword patterns for bootstrap labeling
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
        "papel higienico", "colgate", "dove", "rexona", "toallitas", "protector solar", "shampoo", "acondicionador"
    ],
    "Limpieza del Hogar": [
        "detergente", "lavandina", "desinfectante", "jabon liquido", "suavizante", "rollo cocina", 
        "ala", "skip", "vivere", "cif", "poett", "procacen", "trapo", "magistral", "ayudín"
    ],
    "Congelados y Otros": [
        "helado", "congelados", "nuggets", "papas fritas congeladas", "patitas", "super congelados", "franchesco"
    ]
}

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "prices"),
    )

def bootstrap_labels(product_names: list[str]) -> list[tuple[str, str]]:
    """Assign target categories based on rule keywords."""
    labeled_data = []
    for name in product_names:
        name_lower = name.lower()
        matched_category = None
        
        # Check rule keywords
        for category, keywords in CATEGORIES.items():
            for kw in keywords:
                if kw in name_lower:
                    matched_category = category
                    break
            if matched_category:
                break
                
        if matched_category:
            labeled_data.append((name, matched_category))
            
    return labeled_data

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
        # Dummy fallback data so that it can train even if database is mostly empty
        dummy_data = []
        for cat, keywords in CATEGORIES.items():
            for kw in keywords[:3]:
                dummy_data.append((f"{kw.title()} Marca Ficticia", cat))
        labeled_data.extend(dummy_data)
        print(f"Total training records (with dummy data): {len(labeled_data)}")

    X = [item[0] for item in labeled_data]
    y = [item[1] for item in labeled_data]

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train pipeline
    print("Training TF-IDF + Logistic Regression model...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True, max_features=10000)),
        ('clf', LogisticRegression(max_iter=1000, C=1.0, class_weight='balanced'))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    print(f"Model Accuracy on Test Split: {accuracy_score(y_test, y_pred):.4f}\n")
    print(classification_report(y_test, y_pred))

    # Save serialized model
    os.makedirs("model", exist_ok=True)
    model_path = os.path.join("model", "category_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)
        
    print(f"Model successfully saved to '{model_path}'")

if __name__ == "__main__":
    train()
