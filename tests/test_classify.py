import pytest
from transform.classify import predict_category, _fallback_predict

def test_fallback_predict_lacteos():
    assert _fallback_predict("leche descremada la serenisima") == "Lácteos"
    assert _fallback_predict("yogur de frutilla activia") == "Lácteos"
    assert _fallback_predict("queso cremoso tregar") == "Lácteos"

def test_fallback_predict_bebidas():
    assert _fallback_predict("cerveza quilmes 1l") == "Bebidas con Alcohol"
    assert _fallback_predict("vino malbec tinto") == "Bebidas con Alcohol"
    assert _fallback_predict("gaseosa coca cola light") == "Bebidas sin Alcohol"
    assert _fallback_predict("agua mineral villavicencio") == "Bebidas sin Alcohol"

def test_fallback_predict_limpieza():
    assert _fallback_predict("detergente magistral regular") == "Limpieza del Hogar"
    assert _fallback_predict("lavandina ayudin original") == "Limpieza del Hogar"


def test_fallback_predict_unknown():
    assert _fallback_predict("producto misterioso especial") == "Otros / Sin Categoria"
    assert _fallback_predict("") == "Otros / Sin Categoria"

def test_predict_category_integration():
    # Calling predict_category should run either the fallback or the ML model if trained.
    # It should not raise errors and should handle empty or None input gracefully.
    res_empty = predict_category("")
    assert res_empty == "Otros / Sin Categoria"
    
    res_none = predict_category(None)
    assert res_none == "Otros / Sin Categoria"

    res_real = predict_category("Leche Entera Larga Vida")
    assert res_real in ["Lácteos", "Otros / Sin Categoria"]
