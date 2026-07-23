# Sazô — Dashboard geográfico

Dashboard de análise de mercado para a cozinha Sazô (Botafogo, Rio). O mapa usa
**Leaflet (CDN) + tiles CartoDB** e **isócronas reais** do OpenRouteService.

## Arquitetura

- **Pipeline (Python)** — roda 1x na máquina do dev. Usa a chave ORS e internet
  para buscar as isócronas. Artefato: `data/processed/isochrones.geojson`.
- **Dashboard (HTML)** — `dist/sazo_dashboard.html`. Dados embutidos inline
  (sem `fetch`, sem chave). Leaflet + tiles vêm da CDN, então **precisa de
  internet ao abrir** (para a biblioteca e os blocos do mapa).

## Como rodar

```bash
# 1. dependências (só o pipeline precisa; requests)
pip install -r requirements.txt

# 2. chave ORS — copie o exemplo e cole sua chave
cp .env.example .env
#   edite .env:  ORS_KEY=sua_chave_aqui

# 3. buscar isócronas no ORS (usa a chave; cacheia — 2ª vez não chama a rede)
python -m pipeline.s1_isochrones          # use --force para re-buscar

# 4. gerar o entregável
python -m dashboard.build                 # -> dist/sazo_dashboard.html
```

Depois é só abrir `dist/sazo_dashboard.html` no navegador (duplo clique).
Como os dados estão embutidos, **não precisa de servidor local** — mas precisa
de internet para o Leaflet e os tiles carregarem.

## Notas

- A chave ORS fica **só** no `.env` (git-ignorado). Nunca entra no HTML.
- As **isócronas são reais** (ORS: `cycling-regular` e `driving-car`).
  Os **scores/domicílios das zonas são ilustrativos** até o pipeline de censo
  (IBGE) rodar — está sinalizado na seção de metodologia do dashboard.
- Créditos obrigatórios (OSM/CARTO/ORS) já estão no rodapé do dashboard.
