"""Fase 2 — Censo IBGE (2022). Baixa os agregados por setor e por bairro,
recorta para o municipio do Rio de Janeiro, valida e salva os dados reais.

Uso:
    python -m pipeline.s2_census          # usa cache dos downloads
    python -m pipeline.s2_census --force  # rebaixa os zips

Sem dependencias pesadas: so a biblioteca padrao (urllib, zipfile, csv).
Os CSVs do IBGE sao ';'-separados, codificados em latin-1, com virgula decimal.

Aceite (Fase 2): a contagem de setores e a soma de domicilios do municipio
batem entre a fonte por setor e a fonte por bairro (consistencia interna),
e os totais sao reportados para conferencia com o publicado pelo IBGE.
"""
import csv
import io
import json
import sys
import zipfile
from pathlib import Path
from urllib import request as urlrequest, error as urlerror

from pipeline import config

RAW = Path("data/raw")


def _download(url: str, dest: Path, force: bool) -> Path:
    if dest.exists() and not force:
        print(f"cache: {dest.name} ja baixado.")
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"baixando {url} ...")
    req = urlrequest.Request(url, headers={"User-Agent": "sazo-pipeline/1.0"})
    with urlrequest.urlopen(req, timeout=180) as resp, open(dest, "wb") as fh:
        fh.write(resp.read())
    print(f"  -> {dest} ({dest.stat().st_size/1_048_576:.1f} MB)")
    return dest


def _open_single_csv(zip_path: Path):
    """Abre o unico .csv de dentro do zip como stream de texto latin-1."""
    zf = zipfile.ZipFile(zip_path)
    name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
    return io.TextIOWrapper(zf.open(name), encoding="latin-1")


def _num(v: str) -> float:
    v = (v or "").strip()
    if v in ("", "."):
        return 0.0
    return float(v.replace(".", "").replace(",", "."))


def _int(v: str) -> int:
    return int(round(_num(v)))


def run(force: bool = False) -> dict:
    bairros_zip = _download(f"{config.IBGE_BASE}/{config.IBGE_BAIRROS_ZIP}",
                            RAW / "bairros_basico_BR.zip", force)
    setores_zip = _download(f"{config.IBGE_BASE}/{config.IBGE_SETORES_ZIP}",
                            RAW / "setores_basico_BR.zip", force)

    mun = config.MUNICIPIO_RIO

    # --- Bairros do municipio (para alimentar o dashboard) ---
    # v0001 = pessoas | v0002 = domicilios (total) | v0007 = domicilios
    # particulares permanentes ocupados (a metrica de mercado que usamos).
    bairros = []
    with _open_single_csv(bairros_zip) as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            if row["CD_MUN"] != mun:
                continue
            bairros.append({
                "cd_bairro": row["CD_BAIRRO"],
                "nome": row["NM_BAIRRO"],
                "pessoas": _int(row["v0001"]),
                "domicilios": _int(row["v0002"]),
                "domicilios_ocupados": _int(row["v0007"]),
                "area_km2": round(_num(row["AREA_KM2"]), 4),
            })
    dom_bairros = sum(b["domicilios"] for b in bairros)

    # --- Setores do municipio (recorte + validacao) ---
    # CD_SETOR tem 15 digitos; os 7 primeiros sao o codigo do municipio.
    n_setores = 0
    dom_setores = 0
    pessoas_setores = 0
    with _open_single_csv(setores_zip) as fh:
        reader = csv.DictReader(fh, delimiter=";")
        key = "CD_MUN" if "CD_MUN" in reader.fieldnames else None
        setor_key = "CD_SETOR" if "CD_SETOR" in reader.fieldnames else reader.fieldnames[0]
        for row in reader:
            in_mun = (row.get(key) == mun) if key else row[setor_key].startswith(mun)
            if not in_mun:
                continue
            n_setores += 1
            dom_setores += _int(row["v0002"])
            pessoas_setores += _int(row["v0001"])

    validacao = {
        "municipio": mun,
        "n_bairros": len(bairros),
        "n_setores": n_setores,
        "domicilios_via_bairros": dom_bairros,
        "domicilios_via_setores": dom_setores,
        "pessoas_via_setores": pessoas_setores,
        "diferenca_domicilios": dom_bairros - dom_setores,
    }

    out = {"validacao": validacao, "bairros": bairros}
    dest = Path(config.ARQ_CENSO_BAIRROS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    print("\n=== VALIDACAO (Fase 2) ===")
    for k, v in validacao.items():
        print(f"  {k:>24}: {v}")
    if validacao["diferenca_domicilios"] != 0:
        print("  AVISO: domicilios por bairro != por setor. Investigar o merge.")
    else:
        print("  OK: domicilios batem entre setor e bairro.")
    print(f"\nsalvo: {dest} ({len(bairros)} bairros do Rio)")
    return out


if __name__ == "__main__":
    try:
        run(force="--force" in sys.argv)
    except urlerror.URLError as e:
        sys.exit(f"ERRO de rede (sem internet?): {e}")
