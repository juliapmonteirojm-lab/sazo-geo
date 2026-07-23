"""Dados de zonas para o choropleth/marcadores.

Isocronas = REAIS (via ORS). Estas zonas sao ILUSTRATIVAS ate o pipeline de
censo (IBGE) rodar — coordenadas sao centroides reais de bairros da Zona Sul,
scores/domicilios/mercado sao demonstrativos. Cada componente vai de 0 a 100:
[demanda, acesso, afinidade, baixa_concorrencia].
"""
ZONAS = [
    {"nome": "Humaitá",         "latlng": [-22.955, -43.198], "score": 92, "dom": 4200,  "conc": 3,  "mercado": 1850, "comp": [88, 95, 90, 86]},
    {"nome": "Botafogo",        "latlng": [-22.951, -43.184], "score": 88, "dom": 9800,  "conc": 6,  "mercado": 3200, "comp": [95, 98, 84, 62]},
    {"nome": "Laranjeiras",     "latlng": [-22.933, -43.183], "score": 86, "dom": 5100,  "conc": 4,  "mercado": 2100, "comp": [82, 90, 88, 80]},
    {"nome": "Flamengo",        "latlng": [-22.932, -43.174], "score": 83, "dom": 8700,  "conc": 7,  "mercado": 2900, "comp": [90, 88, 80, 66]},
    {"nome": "Catete/Glória",   "latlng": [-22.925, -43.176], "score": 79, "dom": 6200,  "conc": 5,  "mercado": 2050, "comp": [84, 82, 74, 72]},
    {"nome": "Urca",            "latlng": [-22.949, -43.163], "score": 78, "dom": 1400,  "conc": 1,  "mercado": 720,  "comp": [58, 70, 92, 96]},
    {"nome": "Copacabana–Leme", "latlng": [-22.965, -43.177], "score": 75, "dom": 12500, "conc": 11, "mercado": 3600, "comp": [96, 72, 70, 50]},
    {"nome": "Jardim Botânico", "latlng": [-22.967, -43.223], "score": 74, "dom": 3800,  "conc": 3,  "mercado": 1650, "comp": [72, 68, 86, 78]},
    {"nome": "Cosme Velho",     "latlng": [-22.945, -43.198], "score": 72, "dom": 2100,  "conc": 2,  "mercado": 980,  "comp": [64, 74, 82, 80]},
    {"nome": "Lagoa",           "latlng": [-22.972, -43.205], "score": 70, "dom": 2600,  "conc": 2,  "mercado": 1180, "comp": [68, 66, 84, 80]},
    {"nome": "Gávea",           "latlng": [-22.978, -43.232], "score": 68, "dom": 3300,  "conc": 3,  "mercado": 1420, "comp": [70, 60, 82, 74]},
    {"nome": "Ipanema",         "latlng": [-22.984, -43.202], "score": 66, "dom": 9400,  "conc": 12, "mercado": 2600, "comp": [92, 58, 72, 42]},
    {"nome": "Copacabana–Sul",  "latlng": [-22.984, -43.188], "score": 63, "dom": 10800, "conc": 13, "mercado": 2900, "comp": [90, 56, 66, 40]},
    {"nome": "Leblon",          "latlng": [-22.986, -43.223], "score": 61, "dom": 7200,  "conc": 10, "mercado": 2050, "comp": [80, 54, 70, 44]},
    {"nome": "São Conrado",     "latlng": [-23.007, -43.263], "score": 54, "dom": 2400,  "conc": 2,  "mercado": 900,  "comp": [56, 44, 68, 72]},
]
