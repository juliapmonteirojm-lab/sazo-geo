"""Fase 3 — POIs (concorrentes e ancoras de afinidade) via OpenStreetMap/Overpass.

Uso:
    python -m pipeline.s3_pois          # usa cache se ja existir
    python -m pipeline.s3_pois --force  # rebusca no Overpass

Conta, por zona (bairro), atribuindo cada POI a zona de centroide mais proximo:
  - concorrentes: restaurantes e fast-food (universo de almoco fora)
  - afinidade:    academias, estudios (yoga/pilates), lojas de produto
                  natural/organico e casas de suco — sinais de publico
                  atento a alimentacao saudavel.

Fallback (brief): se o Overpass falhar, aceita data/raw/pois_manual.csv com
colunas  nome;concorrentes;afinidade  (contagem manual por bairro).
Sem dependencias pesadas: so a biblioteca padrao.
"""
import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from shapely.geometry import Point
from shapely.prepared import prep

from pipeline import config, geo
from dashboard.zones import ZONAS

OVERPASS = "https://overpass-api.de/api/interpreter"
# bbox generosa cobrindo a Zona Sul (S, W, N, E)
BBOX = (-23.03, -43.29, -22.90, -43.15)
ARQ = "data/processed/pois_zonas.json"
MANUAL = "data/raw/pois_manual.csv"

# Filtros Overpass -> categoria interna
CONCORRENTE = '["amenity"~"^(restaurant|fast_food|food_court)$"]'
AFINIDADE = (
    '["leisure"="fitness_centre"]', '["sport"~"fitness|yoga|pilates"]',
    '["shop"~"health_food|organic|greengrocer"]', '["amenity"="juice_bar"]',
    '["shop"="farm"]',
)


def _query() -> str:
    s, w, n, e = BBOX
    b = f"({s},{w},{n},{e})"
    parts = [f'nwr{CONCORRENTE}{b};']
    for f in AFINIDADE:
        parts.append(f"nwr{f}{b};")
    body = "".join(parts)
    return f"[out:json][timeout:90];({body});out center tags;"


def _fetch() -> list:
    data = urllib.parse.urlencode({"data": _query()}).encode()
    req = urllib.request.Request(
        OVERPASS, data=data,
        headers={"User-Agent": "sazo-pipeline/1.0 (analise de mercado)"})
    with urllib.request.urlopen(req, timeout=100) as r:
        return json.loads(r.read())["elements"]


def _categoria(tags: dict) -> str:
    if tags.get("amenity") in ("restaurant", "fast_food", "food_court"):
        return "concorrentes"
    return "afinidade"


def _classificar_por_bairro(elems: list, contagem: dict) -> int:
    """Atribui cada POI ao bairro (poligono IBGE) que o contem. POIs fora dos
    16 bairros analisados sao descartados — sem a distorcao do vizinho-mais-
    proximo, que jogava o Centro inteiro no bairro de borda."""
    nomes = [z["nome"] for z in ZONAS]
    polis = geo.carregar_bairros(nomes=nomes)
    prep_polis = {nm: prep(g) for nm, g in polis.items()}
    atribuidos = 0
    for el in elems:
        tags = el.get("tags", {})
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lng = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lng is None:
            continue
        pt = Point(lng, lat)
        for nm, pg in prep_polis.items():
            if pg.contains(pt):
                contagem[nm][_categoria(tags)] += 1
                atribuidos += 1
                break
    return atribuidos


def _from_manual() -> dict:
    p = Path(MANUAL)
    if not p.exists():
        sys.exit(f"ERRO: Overpass falhou e {MANUAL} nao existe (fallback manual).")
    print(f"fallback: lendo {MANUAL}")
    out = {}
    with open(p, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            out[row["nome"]] = {"concorrentes": int(row["concorrentes"]),
                                "afinidade": int(row["afinidade"])}
    return out


def run(force: bool = False) -> dict:
    dest = Path(ARQ)
    if dest.exists() and not force:
        print(f"cache: {dest} ja existe — nenhuma chamada de rede.")
        return json.loads(dest.read_text(encoding="utf-8"))

    contagem = {z["nome"]: {"concorrentes": 0, "afinidade": 0} for z in ZONAS}
    try:
        elems = _fetch()
        n = _classificar_por_bairro(elems, contagem)
        print(f"Overpass OK: {len(elems)} POIs; {n} dentro dos 16 bairros.")
    except Exception as e:
        print(f"AVISO: Overpass falhou ({type(e).__name__}: {e}).")
        contagem = _from_manual()

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(contagem, ensure_ascii=False, indent=0),
                    encoding="utf-8")
    tc = sum(v["concorrentes"] for v in contagem.values())
    ta = sum(v["afinidade"] for v in contagem.values())
    print(f"salvo: {dest}  (concorrentes={tc}, afinidade={ta})")
    top = sorted(contagem.items(), key=lambda kv: kv[1]["concorrentes"], reverse=True)[:5]
    for nome, v in top:
        print(f"   {nome:<16} conc={v['concorrentes']:>3}  afin={v['afinidade']:>3}")
    return contagem


if __name__ == "__main__":
    run(force="--force" in sys.argv)
