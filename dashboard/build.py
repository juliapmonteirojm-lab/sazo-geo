"""Fase 6 — gera dist/sazo_dashboard.html.

Junta:
  - isocronas REAIS (ORS, data/processed/isochrones.geojson)
  - censo REAL (IBGE, data/processed/censo_rio_bairros.json) -> domicilios/pop
  - zonas (dashboard/zones.py) -> centroides + componentes ilustrativas

Deriva, de forma transparente (premissas em config.py):
  - demanda   = domicilios ocupados normalizados (0-100)
  - score     = media ponderada das 4 componentes (PESOS)
  - mercado   = dom_ocupados * TAXA_DOM_ALVO * MARMITAS_SEM_POR_DOM
E marca quais zonas caem dentro da isocrona de bike 25 min (teste de
centroide — aproximacao; o rateio por area fica para a Fase 4).

Contrato: template.html tem o token  /*__DATA__*/  -> window.SAZO_DATA = {...};
Nenhuma chave de API entra no HTML.

Uso: python -m dashboard.build
"""
import json
import math
import unicodedata
from pathlib import Path

from pipeline import config
from dashboard.zones import ZONAS

TEMPLATE = Path("dashboard/template.html")
OUT = Path("dist/sazo_dashboard.html")
TOKEN = "/*__DATA__*/"


def _norm(s: str) -> str:
    # normaliza nome de bairro p/ join robusto (sem acento, minusculo)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.strip().lower()


def _point_in_ring(lng: float, lat: float, ring: list) -> bool:
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and \
           (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _in_polygon(lng: float, lat: float, geometry: dict) -> bool:
    # suporta Polygon e MultiPolygon; considera so o anel externo
    if geometry["type"] == "Polygon":
        polys = [geometry["coordinates"]]
    else:  # MultiPolygon
        polys = geometry["coordinates"]
    return any(_point_in_ring(lng, lat, poly[0]) for poly in polys)


def _haversine_km(a, b) -> float:
    (la1, lo1), (la2, lo2) = a, b
    r = 6371.0
    dla, dlo = math.radians(la2 - la1), math.radians(lo2 - lo1)
    h = (math.sin(dla / 2) ** 2
         + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(dlo / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(h))


def _minmax(valores, inverso=False):
    """Normaliza uma lista de valores para 0-100 (min-max). inverso: menor->100."""
    lo, hi = min(valores), max(valores)
    if hi == lo:
        return [50.0 for _ in valores]
    out = [100 * (v - lo) / (hi - lo) for v in valores]
    return [100 - x for x in out] if inverso else out


def build() -> None:
    iso = json.loads(Path(config.ARQ_ISOCRONAS).read_text(encoding="utf-8"))
    censo = json.loads(Path(config.ARQ_CENSO_BAIRROS).read_text(encoding="utf-8"))
    pois = json.loads(Path(config.ARQ_POIS).read_text(encoding="utf-8"))
    por_nome = {_norm(b["nome"]): b for b in censo["bairros"]}
    # Fase 4 (opcional): rateio espacial real. Se ausente, acesso e KPIs de area
    # caem para valores interinos.
    score_bd = None
    if Path(config.ARQ_SCORE).exists():
        score_bd = json.loads(Path(config.ARQ_SCORE).read_text(encoding="utf-8"))
    bairros_geo = None
    if Path(config.ARQ_BAIRROS_GEO).exists():
        bairros_geo = json.loads(Path(config.ARQ_BAIRROS_GEO).read_text(encoding="utf-8"))

    bike25 = next((f["geometry"] for f in iso["features"]
                   if f["properties"]["mode"] == "bike"
                   and f["properties"]["minutes"] == 25), None)

    # 1a passada: anexa censo (Fase 2) + POIs (Fase 3) e calcula mercado.
    enriquecidas = []
    faltando = []
    for z in ZONAS:
        b = por_nome.get(_norm(z["nome"]))
        p = pois.get(z["nome"], {"concorrentes": 0, "afinidade": 0})
        if not b:
            faltando.append(z["nome"])
            continue
        dom = b["domicilios_ocupados"]
        merc = round(dom * config.TAXA_DOM_ALVO * config.MARMITAS_SEM_POR_DOM)
        lat, lng = z["latlng"]
        enriquecidas.append({**z, "dom": dom, "pessoas": b["pessoas"],
                             "area_km2": b["area_km2"], "mercado": merc,
                             "conc": p["concorrentes"], "afin_raw": p["afinidade"],
                             "no_alcance_bike25": bool(bike25 and _in_polygon(lng, lat, bike25))})
    if faltando:
        raise SystemExit(f"ERRO: bairros sem match no censo: {faltando}")

    # Componentes normalizadas (0-100) sobre as 16 zonas:
    max_dom = max(z["dom"] for z in enriquecidas)
    # densidades por 1.000 domicilios (Fase 3, dados OSM reais)
    dens_conc = [z["conc"] * 1000 / z["dom"] for z in enriquecidas]
    dens_afin = [z["afin_raw"] * 1000 / z["dom"] for z in enriquecidas]
    baixa_conc_s = _minmax(dens_conc, inverso=True)   # menos concorrencia -> maior
    afinidade_s = _minmax(dens_afin)                  # mais ancoras -> maior
    if score_bd:
        # acesso REAL (Fase 4): fracao da area do bairro dentro do bike 25 min
        acesso_s = [score_bd["acesso"].get(z["nome"], 0) for z in enriquecidas]
    else:
        # acesso INTERIM: proxy por distancia a cozinha
        dist = [_haversine_km(config.COZINHA_LATLNG, z["latlng"]) for z in enriquecidas]
        acesso_s = _minmax(dist, inverso=True)        # mais perto -> maior

    pesos = config.PESOS
    zonas_out = []
    for i, z in enumerate(enriquecidas):
        demanda = round(100 * z["dom"] / max_dom)
        acesso = round(acesso_s[i])
        afinidade = round(afinidade_s[i])
        baixa_conc = round(baixa_conc_s[i])
        score = round(pesos["demanda"] * demanda + pesos["acesso"] * acesso
                      + pesos["afinidade"] * afinidade
                      + pesos["baixa_concorrencia"] * baixa_conc)
        score = max(0, min(100, score))
        dist_km = round(_haversine_km(config.COZINHA_LATLNG, z["latlng"]) * config.DIST_ROAD_FACTOR, 2)
        zonas_out.append({
            "nome": z["nome"], "latlng": z["latlng"],
            "score": score, "dom": z["dom"], "pessoas": z["pessoas"],
            "conc": z["conc"], "afin": z["afin_raw"], "mercado": z["mercado"],
            "no_alcance_bike25": z["no_alcance_bike25"], "dist_km": dist_km,
            "comp": [demanda, acesso, afinidade, baixa_conc],
        })
    zonas_out.sort(key=lambda z: z["score"], reverse=True)

    dom_zonas = sum(z["dom"] for z in zonas_out)
    dom_bike25 = sum(z["dom"] for z in zonas_out if z["no_alcance_bike25"])

    # KPIs de area: reais (Fase 4) se disponiveis, senao interinos.
    if score_bd:
        k = score_bd["kpis"]
        alcance_km2 = k["alcance_bike_km2"]
        area_nao_atendida = k["area_nao_atendida_pct"]
        dom_alcance_bike = k["dom_bike25"]
        dom_nao_atendida = k["dom_nao_atendida"]
        kpis_reais = True
    else:
        alcance_km2, area_nao_atendida = 14, 68
        dom_alcance_bike, dom_nao_atendida = dom_bike25, None
        kpis_reais = False

    premissas = {
        "cozinha": config.COZINHA_LATLNG,
        "capacidade_semanal": config.CAPACIDADE_SEMANAL,
        "producao_atual": config.PRODUCAO_ATUAL,
        "ociosa": config.CAPACIDADE_SEMANAL - config.PRODUCAO_ATUAL,
        "gasto_fora": config.GASTO_FORA,
        "semanas_mes": config.SEMANAS_MES,
        "captura_base": config.CAPTURA_BASE,
        "atendido_hoje": ["Botafogo", "Flamengo", "Laranjeiras"],
        "alcance_bike_km2": alcance_km2,
        "area_nao_atendida_pct": area_nao_atendida,
        "kpis_reais": kpis_reais,
        "dom_alcance_bike25": dom_alcance_bike,
        "dom_nao_atendida_bike25": dom_nao_atendida,
        "pesos": pesos,
        "taxa_dom_alvo": config.TAXA_DOM_ALVO,
        "marmitas_sem_por_dom": config.MARMITAS_SEM_POR_DOM,
        "censo": {
            "fonte": "IBGE — Censo 2022 (Agregados por Setores Censitários)",
            "municipio": censo["validacao"]["municipio"],
            "pessoas_municipio": censo["validacao"]["pessoas_via_setores"],
            "domicilios_municipio": censo["validacao"]["domicilios_via_setores"],
            "n_setores": censo["validacao"]["n_setores"],
            "n_bairros": censo["validacao"]["n_bairros"],
            "dom_ocupados_zonas": dom_zonas,
            "dom_ocupados_no_alcance_bike25": dom_bike25,
        },
        "pois": {
            "fonte": "OpenStreetMap (Overpass)",
            "concorrentes": sum(z["conc"] for z in zonas_out),
            "afinidade": sum(z["afin"] for z in zonas_out),
        },
        "negocio": {
            "preco": config.PRECO_MARMITA,
            "custo_marmita": config.CUSTO_MARMITA,
            "marmitas_por_pedido": config.MARMITAS_POR_PEDIDO,
            "custo_entrega_pedido": config.CUSTO_ENTREGA_PEDIDO,
            "custos_fixos_mes": config.CUSTOS_FIXOS_MES,
            "custo_entrega_km": config.CUSTO_ENTREGA_KM,
            "ifood_taxa": config.IFOOD_TAXA,
            "ifood_taxa_basico": config.IFOOD_TAXA_BASICO,
            "entregador_salario_mes": config.ENTREGADOR_SALARIO_MES,
        },
    }

    data = {"premissas": premissas, "zonas": zonas_out, "isocronas": iso}
    if bairros_geo:
        data["bairros_geo"] = bairros_geo
    blob = "window.SAZO_DATA = " + json.dumps(data, ensure_ascii=False) + ";"

    html = TEMPLATE.read_text(encoding="utf-8")
    if TOKEN not in html:
        raise SystemExit(f"ERRO: token {TOKEN} nao encontrado em {TEMPLATE}.")
    html = html.replace(TOKEN, blob)
    assert "ORS_KEY" not in html and "Authorization" not in html, "chave vazou no HTML!"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    # index.html (mesmo conteúdo) para o site servir no "/" em qualquer host estático
    (OUT.parent / "index.html").write_text(html, encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"OK: {OUT} ({kb:.0f} KB) — {len(zonas_out)} zonas, "
          f"{len(iso['features'])} isocronas.")
    print(f"   domicilios ocupados (16 zonas): {dom_zonas:,}".replace(",", "."))
    print(f"   no alcance de bike 25 min:      {dom_bike25:,}".replace(",", "."))
    print(f"   top 3: " + ", ".join(f"{z['nome']}({z['score']})" for z in zonas_out[:3]))


if __name__ == "__main__":
    build()
