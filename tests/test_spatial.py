"""Fase 4 — testes do rateio espacial (criterio de aceite do brief).

Casos sinteticos para frac_inside: 100% dentro -> 1.0; 100% fora -> 0.0;
metade -> 0.5 +/- 0.01. Alem disso: soma de domicilios rateados <= total, e
o score ponderado nunca sai de [0,100].
"""
from shapely.geometry import box

from pipeline import config, geo
from pipeline.s4_score import frac_inside


def test_totalmente_dentro():
    area = box(0, 0, 10, 10)
    unidade = box(2, 2, 4, 4)
    assert frac_inside(unidade, area) == 1.0


def test_totalmente_fora():
    area = box(0, 0, 10, 10)
    unidade = box(20, 20, 22, 22)
    assert frac_inside(unidade, area) == 0.0


def test_metade_dentro():
    area = box(0, 0, 10, 10)
    unidade = box(5, 0, 15, 10)  # metade da unidade dentro da area
    assert abs(frac_inside(unidade, area) - 0.5) < 0.01


def test_soma_rateada_nao_excede_total():
    # grade de 10 setores 1x10; isocrona cobre 2,5 colunas
    iso = box(0, 0, 2.5, 10)
    total = rateado = 0.0
    for i in range(10):
        setor = box(i, 0, i + 1, 10)
        dom = 100
        total += dom
        rateado += dom * frac_inside(setor, iso)
    assert rateado <= total + 1e-9
    assert abs(rateado - 250) < 1e-6  # exatamente 2,5 colunas * 100


def test_frac_sempre_entre_0_e_1():
    area = box(0, 0, 10, 10)
    for unidade in (box(-5, -5, 5, 5), box(3, 3, 7, 7), box(9, 9, 20, 20)):
        f = frac_inside(unidade, area)
        assert 0.0 <= f <= 1.0


def test_pesos_somam_um():
    assert abs(sum(config.PESOS.values()) - 1.0) < 1e-9


def test_score_sempre_em_0_100():
    w = config.PESOS
    chaves = ["demanda", "acesso", "afinidade", "baixa_concorrencia"]
    for comp in ([0, 0, 0, 0], [100, 100, 100, 100], [50, 20, 80, 10], [100, 0, 100, 0]):
        s = sum(w[k] * v for k, v in zip(chaves, comp))
        assert 0 <= s <= 100


def test_reprojecao_para_metrico_preserva_ordem_de_grandeza():
    # 1 km2 aproximado perto da cozinha deve dar ~1e6 m2 apos reprojetar
    lng, lat = config.COZINHA_LNGLAT
    d = 0.0045  # ~0.5 km em graus nesta latitude
    quad = box(lng - d, lat - d, lng + d, lat + d)
    area_m2 = geo.para_metrico(quad).area
    assert 5e5 < area_m2 < 2e6
