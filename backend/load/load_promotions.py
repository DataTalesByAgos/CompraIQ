import os
import mysql.connector
from datetime import datetime

# Import scrapers
from extract.dia_promo_scraper import scrape_dia_promotions
from extract.coto_promo_scraper import scrape_coto_promotions
from extract.modo_promo_scraper import scrape_modo_promotions
from extract.cencosud_carrefour_promo_scraper import scrape_cencosud_carrefour_promotions

def get_db_connection():
    # Leer variables de entorno (al igual que la parte de carga de precios)
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "prices")
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def run_promotions_pipeline():
    print("=" * 50)
    print("▶  INICIANDO PIPELINE DE PROMOCIONES Y DESCUENTOS")
    print("=" * 50)
    
    # 1. Obtener todas las promos reales
    all_promos = []
    
    all_promos.extend(scrape_dia_promotions())
    all_promos.extend(scrape_coto_promotions())
    all_promos.extend(scrape_modo_promotions())
    all_promos.extend(scrape_cencosud_carrefour_promotions())
    
    print(f"\n[Consolidación] Total de promociones extraídas: {len(all_promos)}")
    
    if not all_promos:
        print("⚠ No se extrajeron promociones. Abortando carga en base de datos.")
        return
        
    # 2. Guardar en Base de Datos MySQL
    print("\n[DB Load] Insertando promociones en la base de datos...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Asegurar que la tabla existe por si no se corrió schema.sql completo
    create_table_query = """
    CREATE TABLE IF NOT EXISTS promotions (
        id                    VARCHAR(64) PRIMARY KEY,
        supermercado          VARCHAR(100) NOT NULL,
        beneficio             VARCHAR(150) NOT NULL,
        tipo_beneficio        VARCHAR(50) NOT NULL,
        tipo_descuento        VARCHAR(50) NOT NULL DEFAULT 'porcentaje',
        valor                 DECIMAL(10,2) NOT NULL,
        dia_semana            VARCHAR(15) NOT NULL,
        tope_descuento_pesos  DECIMAL(15,2) NULL,
        categorias_aplicables VARCHAR(255) DEFAULT 'all',
        fecha_inicio          DATE NULL,
        fecha_fin             DATE NULL,
        url_fuente            VARCHAR(255) NULL,
        actualizado_el        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_supermercado_dia (supermercado, dia_semana)
    );
    """
    cursor.execute(create_table_query)
    
    # Eliminar únicamente las promociones que ya expiraron en lugar de vaciar la tabla por completo
    cursor.execute("DELETE FROM promotions WHERE fecha_fin < CURRENT_DATE()")
    
    insert_query = """
    INSERT INTO promotions (
        id, supermercado, beneficio, tipo_beneficio, tipo_descuento,
        valor, dia_semana, tope_descuento_pesos, categorias_aplicables,
        fecha_inicio, fecha_fin, url_fuente
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        valor = VALUES(valor),
        tope_descuento_pesos = VALUES(tope_descuento_pesos),
        fecha_fin = VALUES(fecha_fin),
        actualizado_el = CURRENT_TIMESTAMP;
    """
    
    success_count = 0
    for p in all_promos:
        try:
            cursor.execute(insert_query, (
                p["id"],
                p["supermercado"],
                p["beneficio"],
                p["tipo_beneficio"],
                p["tipo_descuento"],
                p["valor"],
                p["dia_semana"],
                p["tope_descuento_pesos"],
                p["categorias_aplicables"],
                p["fecha_inicio"],
                p["fecha_fin"],
                p["url_fuente"]
            ))
            success_count += 1
        except Exception as ex:
            print(f"  ⚠ Error al insertar promo {p.get('beneficio')} en {p.get('supermercado')}: {ex}")
            
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Pipeline de Promociones completo. {success_count} registros guardados en la tabla `promotions`.")

if __name__ == "__main__":
    # Configurar path por si se corre de forma directa
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_promotions_pipeline()
