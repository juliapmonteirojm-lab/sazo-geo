"""Fase 1 — busca as isocronas no OpenRouteService e salva um GeoJSON combinado.

Uso:
    python -m pipeline.s1_isochrones          # usa cache se ja existir
    python -m pipeline.s1_isochrones --force  # ignora o cache e rebusca

A chave vem de .env (ORS_KEY=...). A chave NUNCA entra no GeoJSON nem no HTML.
Rodar duas vezes seguidas faz ZERO chamadas de rede na segunda vez (cache).
"""
import json
import os
import sys
import time
from pathlib import Path
from urllib import request as urlrequest, error as urlerror

from pipeline import config

ORS_URL = "https://api.openrouteservice.org/v2/isochrones/{profile}"


def _load_key() -> str:
    # Carrega ORS_KEY do ambiente ou do arquivo .env (sem dependencia externa).
    key = os.environ.get("ORS_KEY", "").strip()
    if not key:
        envfile = Path(".env")
        if envfile.exists():
            for line in envfile.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("ORS_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    if not key:
        sys.exit("ERRO: defina ORS_KEY no arquivo .env (veja .env.example).")
    return key


def _fetch(profile: str, ranges: list, key: str, range_type: str = "time") -> dict:
    body = json.dumps({
        "locations": [config.COZINHA_LNGLAT],
        "range": ranges,
        "range_type": range_type,
    }).encode("utf-8")
    req = urlrequest.Request(
        ORS_URL.format(profile=profile),
        data=body,
        headers={"Authorization": key, "Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run(force: bool = False) -> dict:
    out = Path(config.ARQ_ISOCRONAS)
    if out.exists() and not force:
        print(f"cache: {out} ja existe — nenhuma chamada de rede.")
        return json.loads(out.read_text(encoding="utf-8"))

    key = _load_key()
    features = []
    for spec in config.ISOCRONAS:
        kmh = spec["kmh"]
        # tempo (min) -> distancia de rede (metros) usando a velocidade assumida
        metros = [round(kmh * (m / 60) * 1000) for m in spec["mins"]]
        print(f"ORS -> {spec['profile']} {spec['mins']}min @ {kmh}km/h = {metros}m (distance)")
        fc = _fetch(spec["profile"], metros, key, range_type="distance")
        for feat, mins, dist_m in zip(fc["features"], spec["mins"], metros):
            feat["properties"] = {
                "mode": spec["mode"],
                "minutes": mins,
                "kmh": kmh,
                "metros": dist_m,
                "label": f"{spec['mode']} {mins} min",
            }
            features.append(feat)
        time.sleep(1)  # gentil com o rate limit do plano gratuito

    combined = {"type": "FeatureCollection", "features": features}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(combined), encoding="utf-8")
    print(f"OK: {len(features)} isocronas salvas em {out}")
    return combined


if __name__ == "__main__":
    try:
        run(force="--force" in sys.argv)
    except urlerror.HTTPError as e:
        sys.exit(f"ERRO HTTP {e.code} do ORS: {e.read().decode('utf-8', 'ignore')[:300]}")
    except urlerror.URLError as e:
        sys.exit(f"ERRO de rede (sem internet?): {e}")
