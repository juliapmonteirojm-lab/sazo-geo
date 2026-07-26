"""Fase 4 — rateio espacial das isocronas + acesso real por bairro.

Reprojeta tudo para EPSG:31983 (metros) ANTES de calcular area. Para cada
setor censitario, calcula a fracao de sua area dentro de cada isocrona e rateia
os domicilios ocupados por essa fracao (rateio por area — nao por centroide,
que distorce justamente as bordas, que e onde mora a decisao).

Produz data/processed/score_breakdown.json com:
  - kpis: area real das isocronas (km2), domicilios ao alcance, % nao atendida
  - acesso: por bairro, fracao (0-100) da area do bairro dentro do bike 25 min
  - rateio: domicilios ocupados dentro de cada isocrona

Uso: python -m pipeline.s4_score
"""
import json
from pathlib import Path

from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.prepared import prep

from pipeline import config, geo
from dashboard.zones import ZONAS

ATENDIDO_HOJE = ["Botafogo", "Flamengo", "Laranjeiras"]


def frac_inside(g_unidade, g_area) -> float:
    """Fracao da area de g_unidade que cai dentro de g_area (0..1)."""
    a = g_unidade.area
    if a <= 0 or not g_unidade.intersects(g_area):
        return 0.0
    return min(1.0, g_unidade.intersection(g_area).area / a)


def run() -> dict:
    iso = json.loads(Path(config.ARQ_ISOCRONAS).read_text(encoding="utf-8"))

    # isocronas em metros, por chave "mode-min"
    iso_m, iso_wgs = {}, []
    for f in iso["features"]:
        p = f["properties"]
        g = shape(f["geometry"])
        iso_wgs.append(g)
        iso_m[f"{p['mode']}-{p['minutes']}"] = geo.para_metrico(g).buffer(0)
    bike25 = iso_m["bike-25"]
    prep_iso = {k: prep(g) for k, g in iso_m.items()}

    # bbox de recorte = uniao das isocronas (a de carro 35 e a maior)
    minx, miny, maxx, maxy = unary_union(iso_wgs).bounds
    bbox = (minx, miny, maxx, maxy)

    # bairros (16) em metros; regiao atendida hoje = uniao de 3 bairros
    nomes = [z["nome"] for z in ZONAS]
    bairros_wgs = geo.carregar_bairros(nomes=nomes)
    bairros = {n: geo.para_metrico(g).buffer(0) for n, g in bairros_wgs.items()}
    atendido = unary_union([bairros[n] for n in ATENDIDO_HOJE]).buffer(0)
    nao_atendida_geom = bike25.difference(atendido)

    # acesso real por bairro = fracao da area do bairro dentro do bike 25 min
    acesso = {n: round(100 * frac_inside(g, bike25)) for n, g in bairros.items()}

    # rateio por area dos domicilios dos setores em cada isocrona
    rateio = {k: 0.0 for k in iso_m}
    dom_nao_atendida = 0.0
    n_setores = 0
    prep_bike25 = prep_iso["bike-25"]
    for _cd, dom, g_wgs in geo.carregar_setores(bbox=bbox):
        if dom <= 0:
            continue
        g = geo.para_metrico(g_wgs).buffer(0)
        if g.area <= 0:
            continue
        n_setores += 1
        for k, gi in iso_m.items():
            if prep_iso[k].intersects(g):
                rateio[k] += dom * frac_inside(g, gi)
        if prep_bike25.intersects(g):
            dom_nao_atendida += dom * frac_inside(g, nao_atendida_geom)

    dom_bike25 = rateio["bike-25"]
    kpis = {
        "alcance_bike_km2": round(bike25.area / 1e6, 1),
        "area_km2_por_isocrona": {k: round(g.area / 1e6, 1) for k, g in iso_m.items()},
        "dom_bike25": round(dom_bike25),
        "dom_nao_atendida": round(dom_nao_atendida),
        "area_nao_atendida_pct": round(100 * nao_atendida_geom.area / bike25.area),
        "dom_nao_atendida_pct": round(100 * dom_nao_atendida / dom_bike25) if dom_bike25 else 0,
        "n_setores_considerados": n_setores,
        "atendido_hoje": ATENDIDO_HOJE,
    }
    out = {"kpis": kpis, "acesso": acesso,
           "rateio_domicilios": {k: round(v) for k, v in rateio.items()}}

    dest = Path(config.ARQ_SCORE)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    # poligonos simplificados dos bairros (WGS84) para o simulador do dashboard
    def _round_geo(g):
        def rnd(coords):
            if isinstance(coords[0], (int, float)):
                return [round(coords[0], 5), round(coords[1], 5)]
            return [rnd(c) for c in coords]
        m = mapping(g)
        m["coordinates"] = rnd(m["coordinates"])
        return m
    bairros_geo = {n: _round_geo(g.simplify(config.SIMPLIFY_TOL, preserve_topology=True))
                   for n, g in bairros_wgs.items()}
    gdest = Path(config.ARQ_BAIRROS_GEO)
    gdest.write_text(json.dumps(bairros_geo, ensure_ascii=False), encoding="utf-8")

    print("=== Fase 4 — rateio espacial ===")
    print(f"  setores considerados:        {n_setores}")
    print(f"  area bike 25 min:            {kpis['alcance_bike_km2']} km2")
    print(f"  domicilios ao alcance bike:  {kpis['dom_bike25']:,}".replace(",", "."))
    print(f"  area nao atendida:           {kpis['area_nao_atendida_pct']}%")
    print(f"  domicilios nao atendidos:    {kpis['dom_nao_atendida']:,} "
          f"({kpis['dom_nao_atendida_pct']}%)".replace(",", "."))
    print(f"  acesso min/max:              {min(acesso.values())}..{max(acesso.values())}")
    print(f"salvo: {dest}")
    return out


if __name__ == "__main__":
    run()
