"""Zonas do dashboard = bairros REAIS da Zona Sul (nomes batem com o IBGE).

O build.py junta estes bairros ao censo (data/processed/censo_rio_bairros.json)
para preencher domicilios e populacao REAIS (IBGE Censo 2022) e derivar a
componente 'demanda' do score.

Aqui ficam apenas:
  - latlng: centroide aproximado do bairro (para o marcador no mapa)
  - conc:   nº de concorrentes (ILUSTRATIVO ate a Fase 3 / POIs)
  - comp_extra: [acesso, afinidade, baixa_concorrencia] em 0-100 (ILUSTRATIVOS
    ate a Fase 4 / join espacial das isocronas e a contagem real de POIs).
A componente 'demanda' NAO fica aqui: vem do censo, calculada no build.
'nome' precisa ser identico ao NM_BAIRRO do IBGE para o join funcionar.
"""
ZONAS = [
    {"nome": "Botafogo",        "latlng": [-22.951, -43.184], "conc": 6,  "comp_extra": [98, 84, 62]},
    {"nome": "Humaitá",         "latlng": [-22.955, -43.198], "conc": 3,  "comp_extra": [95, 90, 86]},
    {"nome": "Laranjeiras",     "latlng": [-22.933, -43.183], "conc": 4,  "comp_extra": [90, 88, 80]},
    {"nome": "Flamengo",        "latlng": [-22.932, -43.174], "conc": 7,  "comp_extra": [88, 80, 66]},
    {"nome": "Catete",          "latlng": [-22.925, -43.176], "conc": 5,  "comp_extra": [82, 74, 72]},
    {"nome": "Glória",          "latlng": [-22.919, -43.175], "conc": 3,  "comp_extra": [80, 72, 70]},
    {"nome": "Urca",            "latlng": [-22.949, -43.163], "conc": 1,  "comp_extra": [70, 92, 96]},
    {"nome": "Cosme Velho",     "latlng": [-22.945, -43.198], "conc": 2,  "comp_extra": [74, 82, 80]},
    {"nome": "Copacabana",      "latlng": [-22.971, -43.184], "conc": 22, "comp_extra": [72, 70, 46]},
    {"nome": "Leme",            "latlng": [-22.963, -43.170], "conc": 4,  "comp_extra": [74, 74, 60]},
    {"nome": "Jardim Botânico", "latlng": [-22.967, -43.223], "conc": 3,  "comp_extra": [68, 86, 78]},
    {"nome": "Lagoa",           "latlng": [-22.972, -43.205], "conc": 2,  "comp_extra": [66, 84, 80]},
    {"nome": "Gávea",           "latlng": [-22.978, -43.232], "conc": 3,  "comp_extra": [60, 82, 74]},
    {"nome": "Ipanema",         "latlng": [-22.984, -43.202], "conc": 12, "comp_extra": [58, 72, 42]},
    {"nome": "Leblon",          "latlng": [-22.986, -43.223], "conc": 10, "comp_extra": [54, 70, 44]},
    {"nome": "São Conrado",     "latlng": [-23.007, -43.263], "conc": 2,  "comp_extra": [44, 68, 72]},
]
