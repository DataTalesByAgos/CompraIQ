import pytest
from transform.parse_units import parse_presentation, calc_price_per_unit

def test_parse_presentation_simple_g():
    res = parse_presentation("500 g")
    assert res["unit_quantity"] == 500.0
    assert res["unit_type"] == "g"
    assert res["unit_multiplier"] == 1
    assert res["base_quantity"] == 500.0
    assert res["unit_label"] == "por 100g"

def test_parse_presentation_kg_to_g():
    res = parse_presentation("1.5 kg")
    assert res["unit_quantity"] == 1.5
    assert res["unit_type"] == "kg"
    assert res["unit_multiplier"] == 1
    assert res["base_quantity"] == 1500.0
    assert res["unit_label"] == "por 100g"

def test_parse_presentation_ml():
    res = parse_presentation("250ml")
    assert res["unit_quantity"] == 250.0
    assert res["unit_type"] == "ml"
    assert res["unit_multiplier"] == 1
    assert res["base_quantity"] == 250.0
    assert res["unit_label"] == "por 100ml"

def test_parse_presentation_liter_to_ml():
    res = parse_presentation("2.25 L")
    assert res["unit_quantity"] == 2.25
    assert res["unit_type"] == "l"
    assert res["unit_multiplier"] == 1
    assert res["base_quantity"] == 2250.0
    assert res["unit_label"] == "por 100ml"

def test_parse_presentation_pack():
    res = parse_presentation("6 x 300 ml")
    assert res["unit_quantity"] == 300.0
    assert res["unit_type"] == "ml"
    assert res["unit_multiplier"] == 6
    assert res["base_quantity"] == 1800.0
    assert res["unit_label"] == "por 100ml"

def test_parse_presentation_units():
    res = parse_presentation("3 unidades")
    assert res["unit_quantity"] == 3.0
    assert res["unit_type"] == "un"
    assert res["unit_multiplier"] == 1
    assert res["base_quantity"] == 3.0
    assert res["unit_label"] == "por unidad"

def test_parse_presentation_empty_and_invalid():
    res = parse_presentation("")
    assert res["unit_quantity"] is None
    
    res_none = parse_presentation(None)
    assert res_none["unit_quantity"] is None

    res_invalid = parse_presentation("producto sin medida")
    assert res_invalid["unit_quantity"] is None

def test_calc_price_per_unit_weight_volume():
    # Price for 500g = $1000 -> Price per 100g = $200
    p1 = calc_price_per_unit(1000.0, 500.0, "g")
    assert p1 == 200.0

    # Price for 2L (2000ml) = $1500 -> Price per 100ml = $75
    p2 = calc_price_per_unit(1500.0, 2000.0, "ml")
    assert p2 == 75.0

def test_calc_price_per_unit_individual():
    # Price for 6 units = $1200 -> Price per unit = $200
    p = calc_price_per_unit(1200.0, 6.0, "un")
    assert p == 200.0

def test_calc_price_per_unit_edge_cases():
    assert calc_price_per_unit(1000.0, 0.0, "g") is None
    assert calc_price_per_unit(1000.0, -50.0, "g") is None
    assert calc_price_per_unit(1000.0, 500.0, None) is None
