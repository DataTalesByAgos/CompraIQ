import os
import time
from datetime import date
import mysql.connector
from transform.parse_units import parse_presentation, calc_price_per_unit


# ---------------------------------------------------------------------------
# Conexión con retry
# ---------------------------------------------------------------------------
def get_connection(retries: int = 6, delay: float = 5.0):
    """Intenta conectar a MySQL con reintentos (cubre el gap post-healthcheck)."""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "prices"),
            )
        except mysql.connector.Error as e:
            last_err = e
            print(f"    [DB] Intento {attempt}/{retries} fallido, reintentando en {delay}s...")
            time.sleep(delay)
    raise last_err



# ---------------------------------------------------------------------------
# 1. LOAD BATCH & RAW
# ---------------------------------------------------------------------------
def insert_ingestion_batch(batch_id: str, source_user: str = 'system') -> int:
    """Inserta en dim_ingestion y retorna la ingestion_key."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dim_ingestion (batch_id, source_user) VALUES (%s, %s)",
        (batch_id, source_user)
    )
    ingestion_key = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return ingestion_key

def insert_raw(data: list[dict], ingestion_key: int) -> list[int]:
    """
    Inserta los registros tal como llegan en raw_prices.
    Retorna los IDs insertados para mantener trazabilidad.
    """
    conn = get_connection()
    cursor = conn.cursor()
    raw_ids = []

    for row in data:
        cursor.execute(
            """
            INSERT INTO raw_prices (ingestion_key, ean, producto, precio, presentacion, supermercado, fuente, promociones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                ingestion_key,
                row.get("ean"),
                row["producto"],
                row["precio"],
                row.get("presentacion", ""),
                row["supermercado"],
                row.get("fuente", "selenium"),
                row.get("promociones"),
            ),
        )
        raw_ids.append(cursor.lastrowid)

    conn.commit()
    cursor.close()
    conn.close()
    return raw_ids


# ---------------------------------------------------------------------------
# 2. HELPERS: upsert de dimensiones
# ---------------------------------------------------------------------------
def _upsert_product(cursor, nombre: str, categoria: str, parsed: dict, ean: str = None, marca: str = "") -> int:
    if ean:
        cursor.execute("SELECT product_id FROM dim_product WHERE ean = %s", (ean,))
        row = cursor.fetchone()
        if row:
            product_id = row[0]
            cursor.execute(
                """
                UPDATE dim_product SET
                    nombre           = %s,
                    marca            = %s,
                    categoria        = COALESCE(%s, categoria),
                    unit_quantity    = %s,
                    unit_type        = %s,
                    unit_multiplier  = %s,
                    base_quantity    = %s,
                    presentacion_raw = %s
                WHERE product_id = %s
                """,
                (
                    nombre,
                    marca,
                    categoria,
                    parsed["unit_quantity"],
                    parsed["unit_type"],
                    parsed["unit_multiplier"],
                    parsed["base_quantity"],
                    parsed["presentacion_raw"],
                    product_id,
                )
            )
            return product_id

        cursor.execute("SELECT product_id FROM dim_product WHERE nombre = %s AND ean IS NULL LIMIT 1", (nombre,))
        row = cursor.fetchone()
        if row:
            product_id = row[0]
            cursor.execute(
                """
                UPDATE dim_product SET
                    ean              = %s,
                    marca            = %s,
                    categoria        = COALESCE(%s, categoria),
                    unit_quantity    = %s,
                    unit_type        = %s,
                    unit_multiplier  = %s,
                    base_quantity    = %s,
                    presentacion_raw = %s
                WHERE product_id = %s
                """,
                (
                    ean,
                    marca,
                    categoria,
                    parsed["unit_quantity"],
                    parsed["unit_type"],
                    parsed["unit_multiplier"],
                    parsed["base_quantity"],
                    parsed["presentacion_raw"],
                    product_id,
                )
            )
            return product_id

        cursor.execute(
            """
            INSERT INTO dim_product
                (ean, nombre, marca, categoria, unit_quantity, unit_type, unit_multiplier,
                 base_quantity, presentacion_raw)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                ean,
                nombre,
                marca,
                categoria,
                parsed["unit_quantity"],
                parsed["unit_type"],
                parsed["unit_multiplier"],
                parsed["base_quantity"],
                parsed["presentacion_raw"],
            )
        )
        return cursor.lastrowid
    else:
        cursor.execute("SELECT product_id FROM dim_product WHERE nombre = %s LIMIT 1", (nombre,))
        row = cursor.fetchone()
        if row:
            product_id = row[0]
            cursor.execute(
                """
                UPDATE dim_product SET
                    marca            = %s,
                    categoria        = COALESCE(%s, categoria),
                    unit_quantity    = %s,
                    unit_type        = %s,
                    unit_multiplier  = %s,
                    base_quantity    = %s,
                    presentacion_raw = %s
                WHERE product_id = %s
                """,
                (
                    marca,
                    categoria,
                    parsed["unit_quantity"],
                    parsed["unit_type"],
                    parsed["unit_multiplier"],
                    parsed["base_quantity"],
                    parsed["presentacion_raw"],
                    product_id,
                )
            )
            return product_id
        else:
            cursor.execute(
                """
                INSERT INTO dim_product
                    (ean, nombre, marca, categoria, unit_quantity, unit_type, unit_multiplier,
                     base_quantity, presentacion_raw)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    nombre,
                    marca,
                    categoria,
                    parsed["unit_quantity"],
                    parsed["unit_type"],
                    parsed["unit_multiplier"],
                    parsed["base_quantity"],
                    parsed["presentacion_raw"],
                )
            )
            return cursor.lastrowid


def _upsert_supermarket(cursor, nombre: str) -> int:
    """Inserta o recupera dim_supermarket. Retorna supermarket_id."""
    cursor.execute(
        "INSERT IGNORE INTO dim_supermarket (nombre) VALUES (%s)", (nombre,)
    )
    cursor.execute(
        "SELECT supermarket_id FROM dim_supermarket WHERE nombre = %s", (nombre,)
    )
    return cursor.fetchone()[0]


def _upsert_date(cursor, d: date) -> int:
    """Inserta o recupera dim_date. Retorna date_id (YYYYMMDD)."""
    date_id = int(d.strftime("%Y%m%d"))
    dia_semana = d.strftime("%A")  # Monday, Tuesday...
    es_finde = d.weekday() >= 5    # Sábado=5, Domingo=6

    cursor.execute(
        """
        INSERT IGNORE INTO dim_date (date_id, fecha, anio, mes, dia, dia_semana, es_finde)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (date_id, d, d.year, d.month, d.day, dia_semana, es_finde),
    )
    return date_id


def _get_source_id(cursor, fuente: str) -> int:
    """Recupera source_id de dim_source."""
    fuente_norm = fuente.lower() if fuente.lower() in ("api", "selenium") else "selenium"
    cursor.execute(
        "SELECT source_id FROM dim_source WHERE nombre = %s", (fuente_norm,)
    )
    row = cursor.fetchone()
    return row[0] if row else 2  # default: selenium


# ---------------------------------------------------------------------------
# 3. LOAD DIMENSIONAL
# ---------------------------------------------------------------------------
def insert_dimensional(data: list[dict], raw_ids: list[int], ingestion_key: int) -> None:
    """
    Transforma y carga en dim_* + fact_prices delegando cálculo a MySQL.

    Args:
        data:          lista de dicts del extractor
        raw_ids:       IDs de raw_prices correspondientes
        ingestion_key: Clave del lote
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today()

    date_id = _upsert_date(cursor, today)

    def _parse_price(raw: str) -> float | None:
        """Parsea un precio desde string manejando múltiples formatos.

        Formatos soportados:
          - "2420.0"      (float string – VTEX API)
          - "$2.599,00"   (argentino con símbolo)
          - "2599"        (entero simple)
        """
        s = str(raw).replace("$", "").replace("ARS", "").strip()
        if not s:
            return None
        # 1. Intentar parseo directo (cubre "2420.0", "2599", "1234.56")
        try:
            return float(s)
        except ValueError:
            pass
        # 2. Formato argentino: "2.599,00" → "2599.00"
        try:
            s = s.replace(".", "").replace(",", ".")
            return float(s)
        except ValueError:
            return None

    for row, raw_id in zip(data, raw_ids):
        # --- Limpiar precio ---
        precio_float = _parse_price(row["precio"])
        if precio_float is None:
            print(f"    [WARN] Precio inválido ignorado: {row['precio']!r}")
            continue

        if precio_float <= 0:
            print(f"    [WARN] Precio <= 0 ignorado: {precio_float}")
            continue

        # --- Parsear presentación ---
        parsed = parse_presentation(row.get("presentacion") or "")

        # Si la presentación no vino, intentar inferirla del nombre
        # pero sin guardar el nombre del producto como presentacion_raw
        if parsed["unit_type"] is None:
            product_name = row["producto"]
            parsed = parse_presentation(product_name)
            parsed["presentacion_raw"] = None

        # --- Upsert dimensiones ---
        product_id     = _upsert_product(cursor, row["producto"], row.get("categoria"), parsed, row.get("ean"), row.get("marca", ""))
        supermarket_id = _upsert_supermarket(cursor, row["supermercado"])
        source_id      = _get_source_id(cursor, row.get("fuente", "selenium"))

        base_qty = parsed["base_quantity"]
        unit_type = parsed["unit_type"]
        unit_label = parsed["unit_label"]

        # Determinamos el multiplicador para el precio_por_unidad
        # Como base_quantity siempre está en gramos o mililitros,
        # multiplicamos por 100 para peso y volumen.
        multiplier_for_price = 100 if unit_type in ('g', 'ml', 'kg', 'l') else 1

        # --- Insertar hecho (Cálculo delegado a DB) ---
        cursor.execute(
            """
            INSERT INTO fact_prices
                (ingestion_key, product_id, supermarket_id, date_id, source_id,
                 price, price_per_unit, unit_label, raw_id)
            VALUES (%s, %s, %s, %s, %s, %s, (%s / NULLIF(%s, 0)) * %s, %s, %s)
            """,
            (
                ingestion_key,
                product_id,
                supermarket_id,
                date_id,
                source_id,
                precio_float,
                precio_float,          # param 1 for division
                base_qty,              # param 2 for NULLIF
                multiplier_for_price,  # param 3 multiplier
                unit_label,
                raw_id,
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()