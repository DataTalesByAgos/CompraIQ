import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text, or_

app = Flask(__name__)
CORS(app)

# ── SQLAlchemy config ────────────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "supersecret")
DB_NAME     = os.getenv("DB_NAME", "prices")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    "?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
}

db = SQLAlchemy(app)

# ── ORM Models ───────────────────────────────────────────────────────────────

class DimProduct(db.Model):
    __tablename__ = "dim_product"

    product_id      = db.Column(db.Integer, primary_key=True)
    ean             = db.Column(db.String(50))
    nombre          = db.Column(db.String(255), nullable=False)
    marca           = db.Column(db.String(100))
    search_tags     = db.Column(db.Text)
    categoria       = db.Column(db.String(100))
    unit_quantity   = db.Column(db.Numeric(10, 3))
    unit_type       = db.Column(db.String(10))
    unit_multiplier = db.Column(db.SmallInteger, default=1)
    base_quantity   = db.Column(db.Numeric(10, 3))
    presentacion_raw = db.Column(db.String(100))

    prices = db.relationship("FactPrice", back_populates="product", lazy="dynamic")


class DimSupermarket(db.Model):
    __tablename__ = "dim_supermarket"

    supermarket_id = db.Column(db.Integer, primary_key=True)
    nombre         = db.Column(db.String(100), nullable=False, unique=True)

    prices = db.relationship("FactPrice", back_populates="supermarket", lazy="dynamic")


class FactPrice(db.Model):
    __tablename__ = "fact_prices"

    fact_id        = db.Column(db.Integer, primary_key=True)
    ingestion_key  = db.Column(db.Integer, nullable=False)
    product_id     = db.Column(db.Integer, db.ForeignKey("dim_product.product_id"), nullable=False)
    supermarket_id = db.Column(db.Integer, db.ForeignKey("dim_supermarket.supermarket_id"), nullable=False)
    date_id        = db.Column(db.Integer, nullable=False)
    source_id      = db.Column(db.Integer, nullable=False)
    price          = db.Column(db.Numeric(15, 2), nullable=False)
    price_per_unit = db.Column(db.Numeric(15, 4))
    unit_label     = db.Column(db.String(20))
    raw_id         = db.Column(db.Integer)

    product      = db.relationship("DimProduct", back_populates="prices")
    supermarket  = db.relationship("DimSupermarket", back_populates="prices")


class Promotion(db.Model):
    __tablename__ = "promotions"

    id                    = db.Column(db.String(64), primary_key=True)
    supermercado          = db.Column(db.String(100), nullable=False)
    beneficio             = db.Column(db.String(150), nullable=False)
    tipo_beneficio        = db.Column(db.String(50), nullable=False)
    tipo_descuento        = db.Column(db.String(50), nullable=False, default='porcentaje')
    valor                 = db.Column(db.Numeric(10, 2), nullable=False)
    dia_semana            = db.Column(db.String(15), nullable=False)
    tope_descuento_pesos  = db.Column(db.Numeric(15, 2))
    categorias_aplicables = db.Column(db.String(255), default='all')
    fecha_inicio          = db.Column(db.Date)
    fecha_fin             = db.Column(db.Date)
    url_fuente            = db.Column(db.String(255))
    actualizado_el        = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


# ── Helpers ────────────────────────────────────────────────────────────────────

def _top_category(cat_raw: str) -> str:
    """Extract the top-level category (first whitespace-separated word)."""
    if not cat_raw:
        return ""
    return cat_raw.split()[0]


# ── Helper: latest price per product per supermarket (subquery) ──────────────

def latest_price_subquery():
    """Returns a subquery with max fact_id per (product_id, supermarket_id)."""
    return (
        db.session.query(
            func.max(FactPrice.fact_id).label("max_fact_id")
        )
        .group_by(FactPrice.product_id, FactPrice.supermarket_id)
        .subquery()
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.route("/api/promotions", methods=["GET"])
def get_promotions():
    try:
        today = func.current_date()
        promos = (
            db.session.query(Promotion)
            .filter(
                or_(Promotion.fecha_inicio == None, Promotion.fecha_inicio <= today),
                or_(Promotion.fecha_fin == None, Promotion.fecha_fin >= today)
            )
            .all()
        )
        
        serialized = []
        for p in promos:
            serialized.append({
                "id": p.id,
                "supermercado": p.supermercado,
                "beneficio": p.beneficio,
                "tipo_beneficio": p.tipo_beneficio,
                "tipo_descuento": p.tipo_descuento,
                "valor": float(p.valor),
                "dia_semana": p.dia_semana,
                "tope_descuento_pesos": float(p.tope_descuento_pesos) if p.tope_descuento_pesos is not None else None,
                "categorias_aplicables": p.categorias_aplicables,
                "fecha_inicio": p.fecha_inicio.isoformat() if p.fecha_inicio else None,
                "fecha_fin": p.fecha_fin.isoformat() if p.fecha_fin else None,
                "url_fuente": p.url_fuente,
                "actualizado_el": p.actualizado_el.isoformat() if p.actualizado_el else None
            })
        return jsonify(serialized)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/search", methods=["GET"])
def search_products():
    """
    Search products by name and return latest prices across all supermarkets.

    Query params:
        q     (str) : search term (partial match, case-insensitive)
        store (str) : preferred supermarket name (optional, for sorting)
        limit (int) : max products to return (default 8, max 30)
    """
    q         = request.args.get("q", "").strip()
    store     = request.args.get("store", "").strip()
    categoria = request.args.get("categoria", "").strip()
    limit     = min(int(request.args.get("limit", 20)), 50)

    if len(q) < 2:
        return jsonify([])

    try:
        # Subquery: max fact_id per (product_id, supermarket_id) → latest prices only
        latest_sq = latest_price_subquery()

        # Base query
        query = (
            db.session.query(
                DimProduct.product_id,
                DimProduct.nombre,
                DimProduct.marca,
                DimProduct.categoria,
                DimProduct.presentacion_raw,
                DimSupermarket.nombre.label("supermercado"),
                FactPrice.price,
            )
            .join(FactPrice, DimProduct.product_id == FactPrice.product_id)
            .join(latest_sq, FactPrice.fact_id == latest_sq.c.max_fact_id)
            .join(DimSupermarket, FactPrice.supermarket_id == DimSupermarket.supermarket_id)
            .filter(text("MATCH(dim_product.nombre, dim_product.marca, dim_product.search_tags) AGAINST (:q IN BOOLEAN MODE)").params(q=q))
        )

        # Filter strictly to products sold at the preferred store
        if store:
            store_pids_sq = (
                db.session.query(FactPrice.product_id)
                .join(DimSupermarket, FactPrice.supermarket_id == DimSupermarket.supermarket_id)
                .filter(DimSupermarket.nombre.ilike(store))
                .subquery()
            )
            query = query.filter(DimProduct.product_id.in_(store_pids_sq))

        # Filter by top-level category
        if categoria:
            query = query.filter(DimProduct.categoria.startswith(categoria))

        query = query.order_by(DimProduct.nombre)
        rows = query.all()

        # Group by product_id → collect prices per supermarket
        products: dict[int, dict] = {}
        for row in rows:
            pid = row.product_id
            if pid not in products:
                # Clean up category: take last segment after space-separated hierarchy
                cat_raw = row.categoria or ""
                # Categories look like "Lácteos Y Productos Frescos Leches Leches Enteras"
                # We keep the full string but trim it for display
                cat_clean = cat_raw.split(" Y ")[0].strip() if " Y " in cat_raw else cat_raw.strip()

                products[pid] = {
                    "product_id":   pid,
                    "nombre":       row.nombre,
                    "marca":        row.marca or "",
                    "categoria":    cat_clean,
                    "presentacion": row.presentacion_raw or "",
                    "prices":       {},
                }
            products[pid]["prices"][row.supermercado] = int(row.price)

        result_list = list(products.values())
        # Sort: prefix match first, then store availability, then alphabetical
        q_lower = q.lower()
        store_pref = store if store else ""
        result_list.sort(key=lambda p: (
            0 if p["nombre"].lower().startswith(q_lower) else 1,
            0 if store_pref in p["prices"] else 1,
            p["nombre"].lower()
        ))

        return jsonify(result_list[:limit])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/popular", methods=["GET"])
def popular_products():
    """
    Returns a small set of popular/common products for a given store.
    Used to pre-populate the quick-add pills.

    Query params:
        store (str) : supermarket name (required)
        limit (int) : default 6
    """
    store = request.args.get("store", "Carrefour").strip()
    limit = min(int(request.args.get("limit", 6)), 20)

    # Curated popular categories to show as quick-add suggestions
    popular_keywords = [
        "leche", "pan", "aceite", "arroz", "fideos", "azucar",
        "yogur", "manteca", "harina", "tomate"
    ]

    try:
        latest_sq = latest_price_subquery()

        results = []
        for keyword in popular_keywords:
            row = (
                db.session.query(
                    DimProduct.product_id,
                    DimProduct.nombre,
                    DimProduct.marca,
                    DimProduct.categoria,
                    DimProduct.presentacion_raw,
                    FactPrice.price,
                )
                .join(FactPrice, DimProduct.product_id == FactPrice.product_id)
                .join(latest_sq, FactPrice.fact_id == latest_sq.c.max_fact_id)
                .join(DimSupermarket, FactPrice.supermarket_id == DimSupermarket.supermarket_id)
                .filter(
                    DimSupermarket.nombre == store,
                    text("MATCH(dim_product.nombre, dim_product.marca, dim_product.search_tags) AGAINST (:kw IN BOOLEAN MODE)").params(kw=keyword)
                )
                .order_by(FactPrice.price)
                .first()
            )
            if row:
                results.append({
                    "product_id":   row.product_id,
                    "nombre":       row.nombre,
                    "marca":        row.marca or "",
                    "categoria":    row.categoria or "",
                    "presentacion": row.presentacion_raw or "",
                    "prices":       {store: int(row.price)},
                })
            if len(results) >= limit:
                break

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Return top-level grocery categories with at least 10 products."""
    BLOCK = {
        "1", "6", "A", "Abrillantadores", "Aceto", "Anchoas", "Aros",
        "Arrollado", "Arrollados", "Aseo", "Azul",
        "Baldes", "Banana", "Barbacoa", "Barras", "Bocaditos",
        "Bollos", "Bolsas", "Bombones", "Bovinos", "Brocoli",
        "Budines", "Caballa", "Cebada", "Cebollas", "Chauchas",
        "Chicles", "Chip", "Choritos", "Ciabatta",
        "Con", "Condimento", "Cosméticos", "Crema", "Cucarachas",
        "Cápsulas", "Danbo", "Detergente", "Donas", "Donuts",
        "Dulce", "Duros", "Elaboración", "En", "Encurtidos",
        "Energizantes", "Ensalada", "Entero", "Especiales",
        "Espinacas", "Extracto", "Facturas", "Fajitas", "Farmacia",
        "Fiambrería", "Filete", "Flanes", "Flautitas", "Fontina",
        "Frutillas", "Fynbo", "Galletas,", "Garbanzos",
        "Gin", "Gouda", "Guantes", "Hidratante", "Hierbas",
        "Hormigas", "Huevo", "Instantáneo", "Jamón",
        "Jugo", "Jurel", "Lasagna", "Lavado",
        "Lechuga", "Limpia", "Limpiadores", "Listos", "Lomo",
        "Madalenas", "Mani", "Mantecas", "Margarinas",
        "Mate", "Membrillo", "Menudencias", "Mermeladas",
        "Mezcla", "Mignon", "Mix", "Molde", "Molido",
        "Moras", "Moscas", "Navidad", "Nuggets", "Nuggets,",
        "Obleas", "Palitos", "Panaderia",
        "Panificados", "Papa", "Papel", "Papeles",
        "Para", "Pasta", "Pategras", "Patitas",
        "Paté", "Pechuga", "Perfumeria", "Pescaderia",
        "Pesto", "Piononos", "Pizzas,", "Platos",
        "Polillas", "Polvo", "Por", "Porcinos",
        "Porotos", "Premezcla", "Prepizza", "Productos",
        "Pulpa", "Puré", "Queso", "Rebozador",
        "Rebozados", "Relleno", "Rotiseria",
        "Salmón", "Sandwiches", "Sardinas", "Semiconserva",
        "Sémola", "Shampoo", "Sin", "Sopas,", "Suavizante",
        "Supremas", "Tabletas", "Tostadas", "Tradicional",
        "Tybo", "Varitas", "Vegetales", "Verdulería",
        "X", "Yogur", "Zanahoria", "Ñoquis", "Carniceria",
    }
    try:
        sql = text("""
            SELECT SUBSTRING_INDEX(categoria, ' ', 1) AS top_cat, COUNT(*) AS cnt
            FROM dim_product
            WHERE categoria != '' AND categoria IS NOT NULL
            GROUP BY top_cat
            HAVING cnt >= 15
            ORDER BY top_cat
        """)
        rows = db.session.execute(sql).fetchall()
        result = [row[0] for row in rows if row[0] not in BLOCK]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/supermarkets", methods=["GET"])
def get_supermarkets():
    """Return list of all supermarket names."""
    try:
        rows = DimSupermarket.query.order_by(DimSupermarket.nombre).all()
        return jsonify([s.nombre for s in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
