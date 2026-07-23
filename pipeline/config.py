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

# --- Censo IBGE (Fase 2) ---
MUNICIPIO_RIO = "3304557"   # codigo IBGE do municipio do Rio de Janeiro
# Base do FTP do Censo 2022 (Agregados por Setores Censitarios)
IBGE_BASE = ("https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/"
             "Agregados_por_Setores_Censitarios")
IBGE_BAIRROS_ZIP = "Agregados_por_Bairro_csv/Agregados_por_bairros_basico_BR_20260520.zip"
IBGE_SETORES_ZIP = "Agregados_por_Setor_csv/Agregados_por_setores_basico_BR_20260520.zip"
ARQ_CENSO_BAIRROS = "data/processed/censo_rio_bairros.json"

# --- Modelo de demanda derivado do censo (premissas explicitas) ---
# Fracao dos domicilios ocupados considerados publico-alvo de marmita saudavel
TAXA_DOM_ALVO = 0.12
# Marmitas/semana por domicilio-alvo (a 100% de captura)
MARMITAS_SEM_POR_DOM = 3

# Pesos do score (Fase 4). Hoje so 'demanda' vem do censo; os demais sao
# ilustrativos ate rodarem s3 (POIs) e s4 (join espacial das isocronas).
PESOS = {"demanda": 0.40, "acesso": 0.25, "afinidade": 0.15, "baixa_concorrencia": 0.20}

ARQ_ISOCRONAS = "data/processed/isochrones.geojson"
