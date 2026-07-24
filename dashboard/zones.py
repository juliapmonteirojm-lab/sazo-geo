"""Zonas do dashboard = bairros REAIS da Zona Sul (nomes batem com o IBGE).

Depois das Fases 2-4, quase tudo vem de dados reais:
  - domicilios / populacao ....... Censo 2022 (IBGE)          [Fase 2]
  - concorrentes / afinidade ..... OpenStreetMap / Overpass   [Fase 3]
  - acesso (alcance de bike) ..... rateio das isocronas ORS   [Fase 4]
  - demanda ...................... derivada dos domicilios     [Fase 2]

Aqui fica so o minimo que nao vem de arquivo:
  - latlng: centroide do bairro, apenas para posicionar o marcador no mapa.
'nome' precisa ser identico ao NM_BAIRRO do IBGE para os joins funcionarem.
"""
ZONAS = [
    {"nome": "Botafogo",        "latlng": [-22.951, -43.184]},
    {"nome": "Humaitá",         "latlng": [-22.955, -43.198]},
    {"nome": "Laranjeiras",     "latlng": [-22.933, -43.183]},
    {"nome": "Flamengo",        "latlng": [-22.932, -43.174]},
    {"nome": "Catete",          "latlng": [-22.925, -43.176]},
    {"nome": "Glória",          "latlng": [-22.919, -43.175]},
    {"nome": "Urca",            "latlng": [-22.949, -43.163]},
    {"nome": "Cosme Velho",     "latlng": [-22.945, -43.198]},
    {"nome": "Copacabana",      "latlng": [-22.971, -43.184]},
    {"nome": "Leme",            "latlng": [-22.963, -43.170]},
    {"nome": "Jardim Botânico", "latlng": [-22.967, -43.223]},
    {"nome": "Lagoa",           "latlng": [-22.972, -43.205]},
    {"nome": "Gávea",           "latlng": [-22.978, -43.232]},
    {"nome": "Ipanema",         "latlng": [-22.984, -43.202]},
    {"nome": "Leblon",          "latlng": [-22.986, -43.223]},
    {"nome": "São Conrado",     "latlng": [-23.007, -43.263]},
]
