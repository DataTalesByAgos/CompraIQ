import pytest
from transform.validate import validate

def test_validate_clean_and_valid():
    data = [
        {"producto": " leche entera tregar ", "precio": " $1.200,50 ", "supermercado": " jumbo ", "categoria": "Lácteos"},
        {"producto": "Arroz Gallo", "precio": "850.00", "supermercado": "disco"}
    ]
    valid, rejected = validate(data)
    
    assert len(valid) == 2
    assert len(rejected) == 0
    
    # Title casing & stripping checks
    assert valid[0]["producto"] == "Leche Entera Tregar"
    assert valid[0]["supermercado"] == "Jumbo"
    assert valid[1]["producto"] == "Arroz Gallo"
    assert valid[1]["supermercado"] == "Disco"

def test_validate_missing_fields():
    data = [
        {"producto": "Leche", "precio": "1200"},  # Missing supermercado
        {"precio": "1200", "supermercado": "Jumbo"},  # Missing producto
        {"producto": "Leche", "supermercado": "Jumbo"}  # Missing precio
    ]
    valid, rejected = validate(data)
    assert len(valid) == 0
    assert len(rejected) == 3
    assert "Campos faltantes" in rejected[0]["__reason"]

def test_validate_invalid_prices():
    data = [
        {"producto": "Leche", "precio": "cero pesos", "supermercado": "Jumbo"},
        {"producto": "Yogur", "precio": "-500", "supermercado": "Jumbo"},
        {"producto": "Queso", "precio": "0", "supermercado": "Jumbo"},
        {"producto": "Crema", "precio": "  ", "supermercado": "Jumbo"}
    ]
    valid, rejected = validate(data)
    assert len(valid) == 0
    assert len(rejected) == 4
    assert "precio no parseable" in rejected[0]["__reason"]
    assert "precio no parseable" in rejected[1]["__reason"]
    assert "precio no parseable" in rejected[2]["__reason"]
    assert "precio vacío" in rejected[3]["__reason"]

def test_validate_deduplication():
    data = [
        {"producto": "Leche Entera", "precio": "1200", "supermercado": "Jumbo", "ean": "7791234567890"},
        # Duplicate by EAN in same supermarket
        {"producto": "Leche Entera Modificada", "precio": "1250", "supermercado": "Jumbo", "ean": "7791234567890"},
        # Duplicate by Name in same supermarket (no EAN)
        {"producto": "Yogur Frutilla", "precio": "400", "supermercado": "Jumbo"},
        {"producto": "Yogur Frutilla", "precio": "450", "supermercado": "Jumbo"},
        # Same EAN but different supermarket is NOT a duplicate
        {"producto": "Leche Entera", "precio": "1200", "supermercado": "Disco", "ean": "7791234567890"}
    ]
    valid, rejected = validate(data)
    assert len(valid) == 3
    assert len(rejected) == 2
    
    # Check that second EAN and second name duplicates were rejected
    assert rejected[0]["producto"] == "Leche Entera Modificada"
    assert rejected[0]["__reason"] == "duplicado en este lote"
    assert rejected[1]["producto"] == "Yogur Frutilla"
    assert rejected[1]["__reason"] == "duplicado en este lote"
