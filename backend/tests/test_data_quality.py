import os
import pytest
import mysql.connector


def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "prices"),
        )
    except Exception:
        return None


@pytest.fixture
def conn():
    connection = get_db_connection()
    if connection is None:
        pytest.skip("Conexión a base de datos MySQL no disponible.")
    yield connection
    connection.close()


def test_no_non_grocery_categories(conn):
    """No deben existir productos de categorías no-góndola."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM dim_product dp
        JOIN fact_prices fp ON fp.product_id = dp.product_id
        WHERE dp.categoria REGEXP 'Electro Hogar|Tiempo Libre|Felices Fiestas|Jugueter'
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    assert count == 0, f"Hay {count} productos de categorías no-góndola"


def test_every_supermarket_has_products(conn):
    """Cada supermercado debe tener al menos 2000 productos."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ds.nombre, COUNT(*) as cnt
        FROM fact_prices fp
        JOIN dim_supermarket ds ON ds.supermarket_id = fp.supermarket_id
        GROUP BY ds.nombre
    """)
    rows = cursor.fetchall()
    cursor.close()
    for name, cnt in rows:
        assert cnt >= 2000, f"{name} solo tiene {cnt} productos (mínimo esperado: 2000)"


def test_prices_in_reasonable_range(conn):
    """Los precios deben estar entre 0.01 y 2.000.000 ARS."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_prices WHERE price < 0.01 OR price > 2000000")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count == 0, f"Hay {count} precios fuera del rango razonable (0.01 - 2.000.000)"


def test_no_zero_or_empty_name(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dim_product WHERE nombre IS NULL OR nombre = ''")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count == 0, f"Hay {count} productos con nombre vacío"


def test_no_negative_prices(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_prices WHERE price <= 0")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count == 0, f"Hay {count} precios <= 0"


def test_no_null_prices(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_prices WHERE price IS NULL")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count == 0, f"Hay {count} precios NULL"


def test_price_per_unit_calculated(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM fact_prices f
        JOIN dim_product p ON f.product_id = p.product_id
        WHERE p.unit_type IN ('g', 'ml', 'kg', 'l')
          AND (f.price_per_unit IS NULL OR f.price_per_unit <= 0)
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    assert count < 30, f"Hay {count} registros sin price_per_unit calculado (max permitido: 30)"


def test_products_span_grocery_categories(conn):
    """Deben existir productos en múltiples categorías de supermercado."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT SUBSTRING_INDEX(dp.categoria, ' ', 1)) FROM dim_product dp
        WHERE dp.categoria != ''
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    assert count >= 5, f"Solo {count} categorías principales encontradas (mínimo esperado: 5)"


def test_price_variation_across_supermarkets(conn):
    """Productos comunes deben tener precios en múltiples supermercados."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT dp.product_id, COUNT(DISTINCT fp.supermarket_id) as supers
            FROM dim_product dp
            JOIN fact_prices fp ON fp.product_id = dp.product_id
            GROUP BY dp.product_id
            HAVING supers >= 3
        ) t
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    assert count > 0, "Ningún producto está en 3+ supermercados"


def test_ean_format(conn):
    """Al menos el 80% de los EANs deben tener 8, 12 o 13 dígitos (formato estándar)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            SUM(CASE WHEN LENGTH(ean) IN (8, 12, 13) THEN 1 ELSE 0 END) as valid_eans,
            COUNT(*) as total_eans
        FROM dim_product
        WHERE ean IS NOT NULL AND ean != ''
    """)
    valid, total = cursor.fetchone()
    cursor.close()
    if total > 0:
        ratio = valid / total
        assert ratio >= 0.8, f"Solo {ratio:.0%} de EANs tienen formato estándar ({valid}/{total})"


def test_supermarket_names_normalized(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT nombre FROM dim_supermarket")
    names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    expected = {"Carrefour", "Dia", "Coto", "Jumbo", "Disco", "Vea", "Toledo", "Cordiez"}
    assert expected.issubset(set(names)), f"Faltan supermercados. Esperados: {expected} - Presentes: {names}"


def test_dedup_by_ean_within_supermarket(conn):
    """No debe haber mismo EAN asignado a distintos product_id en un mismo supermercado."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT dp.ean, fp.supermarket_id, COUNT(DISTINCT dp.product_id) as pids
            FROM dim_product dp
            JOIN fact_prices fp ON fp.product_id = dp.product_id
            WHERE dp.ean IS NOT NULL AND dp.ean != ''
            GROUP BY dp.ean, fp.supermarket_id
            HAVING pids > 1
        ) t
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    assert count == 0, f"Hay {count} EAN+supermercado con múltiples product_id"


def test_total_products_above_target(conn):
    """Total de productos únicos debe ser >= 10000."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dim_product")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count >= 10000, f"Solo {count} productos únicos (mínimo esperado: 10000)"


def test_total_price_records_above_target(conn):
    """Total de registros de precio debe ser >= 15000."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_prices")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count >= 15000, f"Solo {count} registros de precio (mínimo esperado: 15000)"
