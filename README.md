# Sazô — Dashboard geográfico

Dashboard de análise de mercado para a cozinha Sazô (Botafogo, Rio). O mapa usa
**Leaflet (CDN) + tiles CartoDB** e dados **reais**: isócronas do
OpenRouteService, censo do IBGE (2022) e POIs do OpenStreetMap.

## Arquitetura

- **Pipeline (Python)** — roda 1x na máquina do dev. Precisa de internet e da
  chave ORS. Gera os artefatos em `data/processed/`.
- **Dashboard (HTML)** — `dist/sazo_dashboard.html`. Dados embutidos inline
  (sem `fetch`, sem chave). Leaflet + tiles vêm da CDN, então **precisa de
  internet ao abrir** (biblioteca + blocos do mapa).

```
s1_isochrones ─┐
s2_census ─────┤→ build.py → dist/sazo_dashboard.html
s3_pois ───────┤
s4_score ──────┘
```

## Como rodar

```bash
pip install -r requirements.txt

cp .env.example .env          # e cole a chave:  ORS_KEY=...

python -m pipeline.s1_isochrones   # isócronas ORS (bike/carro)   [Fase 1]
python -m pipeline.s2_census       # censo IBGE, recorte do Rio   [Fase 2]
python -m pipeline.s3_pois         # POIs OSM (concorrentes/afin) [Fase 3]
python -m pipeline.s4_score        # rateio espacial + acesso     [Fase 4]
python -m dashboard.build          # -> dist/sazo_dashboard.html  [Fase 6]

pytest                             # testes do rateio espacial
```

Depois é só abrir `dist/sazo_dashboard.html` no navegador. Todas as etapas
cacheiam os downloads — rodar de novo não refaz chamadas de rede
(use `--force` em s1/s2/s3 para refazer).

## O que é real

| Dado | Fonte | Fase |
|---|---|---|
| Isócronas (bike 15/25, carro 20/35) | OpenRouteService | 1 |
| Domicílios e população por bairro | IBGE — Censo 2022 | 2 |
| Concorrentes e âncoras de afinidade | OpenStreetMap (Overpass) | 3 |
| Acesso, km² alcançáveis, % não atendida | Rateio espacial das isócronas (EPSG:31983) | 4 |

Componentes do score (`config.PESOS`): **demanda** (domicílios), **acesso**
(fração do bairro dentro da isócrona de bike 25 min), **afinidade** (densidade
de POIs saudáveis) e **baixa concorrência** (inverso da densidade de
restaurantes). As únicas premissas assumidas são de negócio: capacidade da
cozinha, gasto médio e taxa de captura (ajustável no dashboard).

## Notas

- A chave ORS fica **só** no `.env` (git-ignorado). Nunca entra no HTML.
- Rateio **por área** (não por centroide): cada setor entra na conta pela
  fração da sua área dentro da isócrona — o centroide distorceria as bordas.
- Créditos obrigatórios (OSM/CARTO/ORS/IBGE) já estão no rodapé do dashboard.
