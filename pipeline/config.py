"""Premissas centrais do projeto Sazô. Nenhum número mágico fora daqui."""

# Coordenada da cozinha (Botafogo, Rio de Janeiro) — SEMPRE [lng, lat] para o ORS
COZINHA_LNGLAT = [-43.184, -22.951]
COZINHA_LATLNG = [-22.951, -43.184]  # ordem do Leaflet

# Velocidades REAIS de entrega (editaveis) — o "dial" do alcance.
# Usamos isocrona por TEMPO do ORS (que ja penaliza morros e tipo de via),
# mas com orcamento conservador: o perfil padrao anda a ~17 km/h (bike) e
# ~50 km/h (carro, fluxo livre), rapido demais pro Rio com carga/transito.
# Pedimos ao ORS o tempo que corresponde a nossa velocidade-alvo:
#   tempo_ORS = tempo_rotulo * (velocidade_alvo / velocidade_base_ORS)
# Assim a FORMA respeita relevo e a ESCALA reflete a entrega real.
VELOCIDADE_BIKE_KMH = 12.0    # bike de entrega carregada, com ladeira/transito
VELOCIDADE_CARRO_KMH = 24.0   # media no transito da Zona Sul do Rio
ORS_BASE_BIKE_KMH = 17.0      # velocidade efetiva do perfil ORS (calibrada)
ORS_BASE_CARRO_KMH = 50.0

# Isocronas: perfil ORS, rotulos em minutos, modo, velocidade-alvo e base ORS.
ISOCRONAS = [
    {"profile": "cycling-regular", "mins": [15, 25], "mode": "bike",  "kmh": VELOCIDADE_BIKE_KMH,  "base_kmh": ORS_BASE_BIKE_KMH},
    {"profile": "driving-car",     "mins": [20, 35], "mode": "carro", "kmh": VELOCIDADE_CARRO_KMH, "base_kmh": ORS_BASE_CARRO_KMH},
]

# Premissas do modelo de receita
CAPACIDADE_SEMANAL = 800
PRODUCAO_ATUAL = 550
GASTO_FORA = 32.0        # R$ por refeicao/marmita (= preco de venda medio)
SEMANAS_MES = 4.33
CAPTURA_BASE = 0.01      # 1,0%

# --- Economia unitaria (informado pela Sazo) ---
PRECO_MARMITA = 32.0             # preco de venda medio
CUSTO_MARMITA = 13.0             # custo direto: insumos + embalagem
MARMITAS_POR_PEDIDO = 4          # media de marmitas por pedido/entrega
CUSTO_ENTREGA_PEDIDO = 7.0       # custo medio atual por pedido (entrega propria)
CUSTOS_FIXOS_MES = 12000.0       # cozinha, utilidades, pro-labore
# Modelo de entrega propria por distancia (editavel no dashboard).
# ~R$2/km rodado; na area atual (bairros proximos) da perto dos R$7/pedido reais.
CUSTO_ENTREGA_KM = 2.0
DIST_ROAD_FACTOR = 1.3           # fator viario sobre a distancia em linha reta
# iFood plano Entrega: comissao+taxa ~26,5% (pesquisa iFood Parceiros 2026)
IFOOD_TAXA = 0.265
# iFood plano Basico (entrega propria via plataforma): ~15,2%
IFOOD_TAXA_BASICO = 0.152
# Entregador contratado: salario mensal (entra como custo fixo adicional)
ENTREGADOR_SALARIO_MES = 2200.0

# --- Censo IBGE (Fase 2) ---
MUNICIPIO_RIO = "3304557"   # codigo IBGE do municipio do Rio de Janeiro
# Base do FTP do Censo 2022 (Agregados por Setores Censitarios)
IBGE_BASE = ("https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/"
             "Agregados_por_Setores_Censitarios")
IBGE_BAIRROS_ZIP = "Agregados_por_Bairro_csv/Agregados_por_bairros_basico_BR_20260520.zip"
IBGE_SETORES_ZIP = "Agregados_por_Setor_csv/Agregados_por_setores_basico_BR_20260520.zip"
ARQ_CENSO_BAIRROS = "data/processed/censo_rio_bairros.json"

# Malhas com atributos (geometria + domicilios) — Censo 2022, UF RJ
IBGE_MALHA_BAIRROS = "malha_com_atributos/bairros/shp/UF/RJ/RJ_bairros_CD2022.zip"
IBGE_MALHA_SETORES = "malha_com_atributos/setores/shp/UF/RJ/RJ_setores_CD2022.zip"
EPSG_METRICO = 31983   # SIRGAS 2000 / UTM 23S — para calcular area em metros

ARQ_POIS = "data/processed/pois_zonas.json"
ARQ_SCORE = "data/processed/score_breakdown.json"
ARQ_BAIRROS_GEO = "data/processed/bairros_geo.json"
# Tolerancia de simplificacao das geometrias de bairro para o cliente (~30m)
SIMPLIFY_TOL = 0.0003

# --- Modelo de demanda derivado do censo (premissas explicitas) ---
# Fracao dos domicilios ocupados considerados publico-alvo de marmita saudavel
TAXA_DOM_ALVO = 0.12
# Marmitas/semana por domicilio-alvo (a 100% de captura)
MARMITAS_SEM_POR_DOM = 3

# Pesos do score (Fase 4). Hoje so 'demanda' vem do censo; os demais sao
# ilustrativos ate rodarem s3 (POIs) e s4 (join espacial das isocronas).
PESOS = {"demanda": 0.40, "acesso": 0.25, "afinidade": 0.15, "baixa_concorrencia": 0.20}

ARQ_ISOCRONAS = "data/processed/isochrones.geojson"
