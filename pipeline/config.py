"""Premissas centrais do projeto Sazô. Nenhum número mágico fora daqui."""

# Coordenada da cozinha (Botafogo, Rio de Janeiro) — SEMPRE [lng, lat] para o ORS
COZINHA_LNGLAT = [-43.184, -22.951]
COZINHA_LATLNG = [-22.951, -43.184]  # ordem do Leaflet

# Isócronas: (perfil ORS, [segundos...], rótulos em minutos)
ISOCRONAS = [
    {"profile": "cycling-regular", "range": [900, 1500], "mins": [15, 25], "mode": "bike"},
    {"profile": "driving-car",     "range": [1200, 2100], "mins": [20, 35], "mode": "carro"},
]

# Premissas do modelo de receita
CAPACIDADE_SEMANAL = 800
PRODUCAO_ATUAL = 550
GASTO_FORA = 32.0        # R$ por refeicao/marmita
SEMANAS_MES = 4.33
CAPTURA_BASE = 0.01      # 1,0%

ARQ_ISOCRONAS = "data/processed/isochrones.geojson"
