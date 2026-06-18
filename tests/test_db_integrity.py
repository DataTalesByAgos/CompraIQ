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

def test_db_connection(conn):
    assert conn.is_connected()

def test_db_tables_exist(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()

    required_tables = ["dim_product", "dim_supermarket", "dim_date", "fact_prices", "raw_prices", "dim_ingestion"]
    for table in required_tables:
        assert table in tables, f"La tabla {table} no existe en la base de datos."

def test_db_no_null_names(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dim_product WHERE nombre IS NULL OR nombre = ''")
    null_names_count = cursor.fetchone()[0]
    cursor.close()
    assert null_names_count == 0, "Hay productos en dim_product con nombre nulo o vacío."

def test_db_valid_prices(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_prices WHERE price <= 0")
    invalid_prices_count = cursor.fetchone()[0]
    cursor.close()
    assert invalid_prices_count == 0, "Hay precios menores o iguales a cero en fact_prices."

def test_db_price_per_unit_calculation(conn):
    cursor = conn.cursor()
    # Check if price_per_unit is calculated for products with units
    cursor.execute("""
        SELECT COUNT(*) FROM fact_prices f
        JOIN dim_product p ON f.product_id = p.product_id
        WHERE p.unit_type IN ('g', 'ml', 'kg', 'l') 
          AND (f.price_per_unit IS NULL OR f.price_per_unit <= 0)
    """)
    uncalculated_count = cursor.fetchone()[0]
    cursor.close()
    assert uncalculated_count == 0, "Hay registros en fact_prices con precio por unidad nulo o inválido."
