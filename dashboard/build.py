"""Fase 6 — injeta os dados (isocronas reais + zonas) no template e gera o
entregavel dist/sazo_dashboard.html.

Contrato: template.html contem o token literal  /*__DATA__*/  em um <script>.
Ele e trocado por  window.SAZO_DATA = {...};  com todos os dados inline.
Nenhuma chave de API entra no HTML.

Uso:
    python -m dashboard.build
"""
import json
from pathlib import Path

from pipeline import config
from dashboard.zones import ZONAS

TEMPLATE = Path("dashboard/template.html")
OUT = Path("dist/sazo_dashboard.html")
TOKEN = "/*__DATA__*/"


def build() -> None:
    iso = json.loads(Path(config.ARQ_ISOCRONAS).read_text(encoding="utf-8"))

    premissas = {
        "cozinha": config.COZINHA_LATLNG,
        "capacidade_semanal": config.CAPACIDADE_SEMANAL,
        "producao_atual": config.PRODUCAO_ATUAL,
        "ociosa": config.CAPACIDADE_SEMANAL - config.PRODUCAO_ATUAL,
        "gasto_fora": config.GASTO_FORA,
        "semanas_mes": config.SEMANAS_MES,
        "captura_base": config.CAPTURA_BASE,
        "atendido_hoje": ["Botafogo", "Flamengo", "Laranjeiras"],
        "alcance_bike_km2": 14,
        "area_nao_atendida_pct": 68,
    }

    data = {"premissas": premissas, "zonas": ZONAS, "isocronas": iso}
    blob = "window.SAZO_DATA = " + json.dumps(data, ensure_ascii=False) + ";"

    html = TEMPLATE.read_text(encoding="utf-8")
    if TOKEN not in html:
        raise SystemExit(f"ERRO: token {TOKEN} nao encontrado em {TEMPLATE}.")
    html = html.replace(TOKEN, blob)

    assert "ORS_KEY" not in html and "Authorization" not in html, "chave vazou no HTML!"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"OK: {OUT} gerado ({kb:.0f} KB) — {len(ZONAS)} zonas, "
          f"{len(iso['features'])} isocronas.")


if __name__ == "__main__":
    build()
