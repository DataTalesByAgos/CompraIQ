# Cazador de Precios 🛒

Pipeline ETL automatizado de precios de supermercados en Argentina.

Extrae precios de Carrefour, Dia, Coto, Jumbo, Disco y Vea — los normaliza, clasifica y almacena en un data warehouse relacional para análisis comparativo.

---

## El Problema

Comparar precios entre supermercados en Argentina es difícil. Los sitios no tienen APIs públicas documentadas, los formatos de presentación son inconsistentes ("500 g", "6 x 300 ml", "1.5 L") y las categorías que publica cada supermercado no son homogéneas entre sí.

El costo no es solo tiempo — es invisibilidad sobre dónde conviene comprar qué producto.

**Cazador de Precios** resuelve eso con un pipeline automatizado que:
- Extrae datos de 6 supermercados vía API
- Normaliza precios a una unidad base comparable (por 100g / 100ml / por unidad)
- Clasifica productos automáticamente con ML cuando la tienda no envía categoría
- Persiste todo en un modelo dimensional (star schema) listo para BI

---

## Cómo Funciona

El pipeline sigue cuatro etapas secuenciales:

```mermaid
flowchart LR
    subgraph Extract
        C[Carrefour\nVTEX API]
        D[Dia\nVTEX API]
        CO[Coto\nAPI]
        J[Jumbo\nVTEX API]
        DS[Disco\nVTEX API]
        V[Vea\nVTEX API]
    end

    subgraph Transform
        VL[Validate\nvalidate.py]
        PU[Parse Units\nparse_units.py]
        CL[Classify\nclassify.py]
    end

    subgraph Load
        RAW[raw_prices]
        DIM[dim_product\ndim_supermarket\ndim_date]
        FACT[fact_prices]
    end

    C & D & CO & J & DS & V --> VL
    VL --> PU --> CL
    CL --> RAW
    RAW --> DIM --> FACT
```

### Estrategia de extracción

Cada supermercado tiene su propio extractor. La lógica es: **API primero, Selenium como fallback**.

| Supermercado | Fuente primaria | Fallback |
|---|---|---|
| Carrefour | VTEX API (`/catalog_system/pub/products/search`) | Selenium headless |
| Dia | VTEX API | — |
| Jumbo | VTEX API (`vtex_base`) | — |
| Disco | VTEX API (`vtex_base`) | — |
| Vea | VTEX API (`vtex_base`) | — |
| Coto | API propia | — |

Los cinco supermercados VTEX usan una base común (`vtex_base.py`) que maneja paginación y parseo de ítems. Carrefour tiene su propio extractor con mayor control sobre el scraping de Selenium.

---

## Arquitectura

### Modelo de datos (Star Schema)

```mermaid
erDiagram
    dim_ingestion {
        int ingestion_key PK
        varchar batch_id
        timestamp load_timestamp
        varchar source_user
    }
    raw_prices {
        int id PK
        int ingestion_key FK
        varchar ean
        text producto
        text precio
        text presentacion
        text supermercado
        varchar fuente
        text promociones
        timestamp fecha
    }
    dim_product {
        int product_id PK
        varchar ean
        varchar nombre
        varchar categoria
        decimal unit_quantity
        varchar unit_type
        smallint unit_multiplier
        decimal base_quantity
        varchar presentacion_raw
    }
    dim_supermarket {
        int supermarket_id PK
        varchar nombre
        varchar pais
    }
    dim_date {
        int date_id PK
        date fecha
        smallint anio
        tinyint mes
        tinyint dia
        varchar dia_semana
        boolean es_finde
    }
    dim_source {
        int source_id PK
        varchar nombre
    }
    fact_prices {
        int fact_id PK
        int ingestion_key FK
        int product_id FK
        int supermarket_id FK
        int date_id FK
        int source_id FK
        decimal price
        decimal price_per_unit
        varchar unit_label
        int raw_id FK
    }

    dim_ingestion ||--o{ raw_prices : "tiene"
    dim_ingestion ||--o{ fact_prices : "agrupa"
    dim_product ||--o{ fact_prices : "describe"
    dim_supermarket ||--o{ fact_prices : "proviene de"
    dim_date ||--o{ fact_prices : "fecha"
    dim_source ||--o{ fact_prices : "fuente"
    raw_prices ||--o{ fact_prices : "trazabilidad"
```

### Flujo de ejecución del pipeline

```mermaid
sequenceDiagram
    participant N8N as Scheduler / N8N
    participant Main as main.py
    participant Extract as Extractores
    participant Validate as validate.py
    participant DB as MySQL

    N8N->>Main: Ejecutar pipeline
    Main->>DB: INSERT dim_ingestion (batch_id)
    DB-->>Main: ingestion_key

    Main->>Extract: extract_carrefour() ... extract_vea()
    Extract-->>Main: raw_data[]

    Main->>Validate: validate(raw_data)
    Validate-->>Main: valid[], rejected[]

    Main->>DB: INSERT raw_prices (valid_data, ingestion_key)
    DB-->>Main: raw_ids[]

    Main->>DB: insert_dimensional()
    Note over DB: _upsert_product → predict_category si categoria vacía
    Note over DB: parse_presentation → normaliza unidad
    DB-->>Main: ✅ dim_product / fact_prices actualizados

    Main->>N8N: JSON PIPELINE_RESULT
```

---

## Clasificación de Categorías (ML)

Los supermercados envían categorías inconsistentes o vacías. El clasificador resuelve eso automáticamente durante la carga.

### Cómo funciona

- **`transform/classify.py`**: expone `predict_category(nombre) → str`. Carga el modelo entrenado una sola vez (lazy load). Si no existe el `.pkl`, cae al fallback de reglas por keywords.
- **`load/load_db.py`**: en `_upsert_product`, si `categoria` está vacía o es `None`, llama a `predict_category(nombre)` antes de insertar.

### Arquitectura del clasificador

```mermaid
flowchart TD
    A[nombre del producto] --> B{¿model.pkl existe?}
    B -- Sí --> C[TF-IDF Vectorizer\nngram_range 1-2]
    C --> D[Logistic Regression]
    D --> E[categoría predicha]
    B -- No --> F[Fallback: keyword matching\nreglas estáticas por categoría]
    F --> E
```

### Categorías objetivo

| Categoría | Ejemplos de keywords |
|---|---|
| Lácteos | leche, yogur, queso, manteca, serenísima |
| Básicos de Almacén | arroz, fideos, aceite, sal, harina, polenta |
| Bebidas con Alcohol | cerveza, vino, fernet, gin, whisky, sidra |
| Bebidas sin Alcohol | gaseosa, agua, jugo, coca, pepsi, sprite |
| Frutas y Verduras | papa, cebolla, tomate, manzana, banana |
| Carnicería y Pescadería | carne, pollo, hamburguesa, milanesa, merluza |
| Panadería y Galletitas | pan, galletitas, alfajor, lactal, chocolinas |
| Cuidado Personal | shampoo, desodorante, pañales, colgate, dove |
| Limpieza del Hogar | detergente, lavandina, desinfectante, skip |
| Congelados y Otros | helado, nuggets, papas congeladas |

### Entrenar el modelo manualmente

```bash
# Requiere que el contenedor de MySQL esté corriendo
python train_model.py
```

Esto conecta a la base, hace bootstrap de labels con las reglas de keywords, entrena el pipeline `TF-IDF + LogisticRegression` y guarda el modelo en `model/category_model.pkl`. Se recomienda re-entrenar cuando haya un volumen significativo de nuevos productos.

---

## Normalización de Unidades

El módulo `transform/parse_units.py` parsea el texto crudo de presentación y lo convierte a una unidad base para comparación justa entre productos de distinto tamaño.

**Formatos soportados:**

| Texto original | `unit_quantity` | `unit_type` | `base_quantity` | `unit_label` |
|---|---|---|---|---|
| `500 g` | 500 | g | 500 | por 100g |
| `1.5 L` | 1.5 | l | 1500 | por 100ml |
| `6 x 300 ml` | 300 | ml | 1800 | por 100ml |
| `1 kg` | 1 | kg | 1000 | por 100g |
| `Un` | 1 | un | 1 | por unidad |

El campo `price_per_unit` en `fact_prices` permite comparar el precio real por 100g o 100ml independientemente del tamaño del envase.

---

## Inicio Rápido

### 1. Configurar variables de entorno

```bash
cp .env.example .env
# Completar con credenciales de la base de datos
```

Variables requeridas en `.env`:
```
MYSQL_ROOT_PASSWORD=...
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=...
DB_NAME=prices
```

### 2. Levantar la base de datos

```bash
docker compose up mysql phpmyadmin -d
```

El schema se inicializa automáticamente desde `db/schema.sql` en el primer arranque. phpMyAdmin queda disponible en `http://localhost:8080`.

### 3. Ejecutar el pipeline

**Modo manual (local):**
```bash
python main.py
```

**Modo automatizado (Docker + scheduler):**
```bash
docker compose --profile cron up
```

### 4. Entrenar el clasificador ML (primera vez o cuando corresponda)

```bash
python train_model.py
```

### 5. Backfill de EAN (datos históricos)

Si hay productos en la base sin EAN que ya tienen un gemelo con EAN cargado después:
```bash
python backfill_ean.py
```

---

## Scripts de Utilidad

| Script | Descripción |
|---|---|
| `train_model.py` | Entrena el clasificador ML desde los registros actuales de `dim_product` |
| `backfill_ean.py` | Propaga EAN a registros históricos que comparten nombre con un producto ya identificado |

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Extracción | `requests` (API), `selenium` + Chromium headless (fallback) |
| Transformación | Python puro + `re` para parseo de unidades |
| Clasificación | `scikit-learn` (TF-IDF + Logistic Regression) |
| Base de datos | MySQL 8 (Docker) |
| Orquestación | Docker Compose + N8N (scheduler externo) |
| UI de base | phpMyAdmin |

---

## Estructura del Proyecto

```
supermercado/
├── extract/
│   ├── vtex_base.py        # Extractor genérico para supermercados VTEX
│   ├── carrefour.py        # Extractor Carrefour (API + Selenium fallback)
│   ├── dia.py              # Extractor Dia
│   ├── coto.py             # Extractor Coto
│   ├── jumbo.py            # Extractor Jumbo
│   ├── disco.py            # Extractor Disco
│   └── vea.py              # Extractor Vea
├── transform/
│   ├── classify.py         # Clasificador ML de categorías
│   ├── parse_units.py      # Parser y normalizador de unidades
│   ├── validate.py         # Validación y deduplicación del lote
│   └── clean_data.py       # Limpieza auxiliar
├── load/
│   └── load_db.py          # Upsert dimensional + inserción en fact_prices
├── db/
│   └── schema.sql          # DDL del star schema
├── model/
│   └── category_model.pkl  # Modelo ML entrenado (generado por train_model.py)
├── main.py                 # Punto de entrada del pipeline
├── train_model.py          # Script de entrenamiento del clasificador
├── backfill_ean.py         # Utilidad de backfill de EAN
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Proveniencia de los Datos

Los datos se obtienen directamente desde las APIs públicas y sitios web de cada supermercado. No se utilizan bases de datos de terceros ni scrapers pagos.

| Fuente | Método | URL base |
|---|---|---|
| Carrefour | VTEX API + Selenium | `carrefour.com.ar` |
| Dia | VTEX API | `diaonline.supermercadosdia.com.ar` |
| Jumbo | VTEX API | `jumbo.com.ar` |
| Disco | VTEX API | `disco.com.ar` |
| Vea | VTEX API | `vea.com.ar` |
| Coto | API propia | `cotodigital3.com.ar` |

Los datos extraídos son de carácter público (precios y nombres de productos visibles a cualquier visitante del sitio). No se almacena información personal de ningún tipo. El pipeline solo registra nombre del producto, precio, presentación, supermercado y fecha de extracción.
