import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "prices"),
    )

def backfill():
    conn = get_connection()
    cursor = conn.cursor()

    print("--- Starting EAN Backfill ---")
    
    # Select products that have an EAN and find others with the same name that don't have an EAN
    query = """
        SELECT p1.nombre, p1.ean, p2.product_id
        FROM dim_product p1
        JOIN dim_product p2 ON p1.nombre = p2.nombre
        WHERE p1.ean IS NOT NULL AND p2.ean IS NULL
    """
    
    cursor.execute(query)
    matches = cursor.fetchall()
    
    if not matches:
        print("No name matches found between products with EAN and products without EAN.")
        cursor.close()
        conn.close()
        return

    print(f"Found {len(matches)} historical records to backfill EAN for.")
    
    updated_count = 0
    for name, ean, product_id in matches:
        cursor.execute(
            "UPDATE dim_product SET ean = %s WHERE product_id = %s",
            (ean, product_id)
        )
        updated_count += 1

    conn.commit()
    print(f"Successfully backfilled {updated_count} records.")
    
    # Also attempt to update historical raw_prices records where product name matches
    print("\n--- Backfilling raw_prices EAN values ---")
    raw_query = """
        UPDATE raw_prices r
        JOIN dim_product p ON r.producto = p.nombre
        SET r.ean = p.ean
        WHERE r.ean IS NULL AND p.ean IS NOT NULL
    """
    cursor.execute(raw_query)
    conn.commit()
    print(f"Updated raw_prices records: {cursor.rowcount}")

    cursor.close()
    conn.close()
    print("--- Backfill Complete ---")

if __name__ == "__main__":
    backfill()
