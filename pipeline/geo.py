"""Utilitarios geoespaciais compartilhados (Fases 3 e 4).

Baixa as malhas do IBGE (bairros/setores) sob demanda, le shapefiles com pyshp,
converte para geometrias shapely e reprojeta para EPSG metrico (area em metros).
"""
import glob
import unicodedata
import zipfile
from pathlib import Path
from urllib import request as urlrequest

import shapefile  # pyshp
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as shp_transform

from pipeline import config

RAW = Path("data/raw")
_TF = Transformer.from_crs(4326, config.EPSG_METRICO, always_xy=True)


def para_metrico(geom):
    """Reprojeta uma geometria WGS84 (lng,lat) para EPSG_METRICO (metros)."""
    return shp_transform(lambda x, y, z=None: _TF.transform(x, y), geom)


def _baixar_unzip(rel_url: str, nome: str) -> Path:
    destdir = RAW / nome
    if list(destdir.glob("*.shp")):
        return next(destdir.glob("*.shp"))
    zippath = RAW / f"{nome}.zip"
    if not zippath.exists():
        url = f"{config.IBGE_BASE}/{rel_url}"
        print(f"baixando malha {url} ...")
        req = urlrequest.Request(url, headers={"User-Agent": "sazo-pipeline/1.0"})
        zippath.parent.mkdir(parents=True, exist_ok=True)
        with urlrequest.urlopen(req, timeout=300) as r, open(zippath, "wb") as fh:
            fh.write(r.read())
        print(f"  -> {zippath} ({zippath.stat().st_size/1_048_576:.1f} MB)")
    destdir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zippath) as zf:
        zf.extractall(destdir)
    return next(destdir.glob("*.shp"))


def malha_bairros_shp() -> Path:
    return _baixar_unzip(config.IBGE_MALHA_BAIRROS, "RJ_bairros_malha")


def malha_setores_shp() -> Path:
    return _baixar_unzip(config.IBGE_MALHA_SETORES, "RJ_setores_malha")


def _norm(s: str) -> str:
    # comparacao de nome de bairro robusta a acento/encoding
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return s.strip().lower()


def _ler_shp(shp):
    # usa a codificacao declarada no .cpg (as malhas do Censo 2022 sao UTF-8);
    # cai para latin-1 se nao houver .cpg.
    cpg = Path(shp).with_suffix(".cpg")
    enc = "utf-8"
    if cpg.exists():
        txt = cpg.read_text(encoding="ascii", errors="ignore").strip().lower()
        if "8859" in txt or "latin" in txt or txt in ("cp1252", "windows-1252"):
            enc = "latin-1"
    return shapefile.Reader(str(shp), encoding=enc)


def carregar_bairros(nomes=None, mun=None):
    """Retorna {nome_pedido: shapely geometry WGS84} do municipio. O match e
    feito por nome normalizado (sem acento), e a chave devolvida e o nome
    exatamente como foi pedido em `nomes` (para casar com ZONAS)."""
    mun = mun or config.MUNICIPIO_RIO
    quer = {_norm(n): n for n in nomes} if nomes else None
    shp = malha_bairros_shp()
    r = _ler_shp(shp)
    out = {}
    for sr in r.iterShapeRecords():
        rec = sr.record.as_dict()
        if str(rec.get("CD_MUN")) != mun:
            continue
        chave = _norm(rec.get("NM_BAIRRO"))
        if quer is not None and chave not in quer:
            continue
        nome = quer[chave] if quer else rec.get("NM_BAIRRO")
        g = shape(sr.shape.__geo_interface__).buffer(0)  # buffer(0) conserta aneis
        out[nome] = out[nome].union(g) if nome in out else g
    return out


def _int(v) -> int:
    try:
        return int(round(float(str(v).replace(",", ".")))) if v not in (None, "", ".") else 0
    except ValueError:
        return 0


def carregar_setores(mun=None, bbox=None):
    """Gera (CD_SETOR, dom_ocupados, geometry WGS84) por setor do municipio.
    dom_ocupados = v0007 (domicilios particulares permanentes ocupados), a
    mesma metrica de mercado usada nas zonas. bbox opcional (minlng, minlat,
    maxlng, maxlat) recorta por bounding box do setor."""
    mun = mun or config.MUNICIPIO_RIO
    shp = malha_setores_shp()
    r = _ler_shp(shp)
    for sr in r.iterShapeRecords():
        rec = sr.record.as_dict()
        if str(rec.get("CD_MUN")) != mun:
            continue
        if bbox is not None:
            bb = sr.shape.bbox  # (minx,miny,maxx,maxy) em WGS84
            if bb[2] < bbox[0] or bb[0] > bbox[2] or bb[3] < bbox[1] or bb[1] > bbox[3]:
                continue
        g = shape(sr.shape.__geo_interface__).buffer(0)
        yield rec.get("CD_SETOR"), _int(rec.get("v0007")), g
