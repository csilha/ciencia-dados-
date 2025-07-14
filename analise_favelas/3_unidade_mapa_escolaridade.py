import pandas as pd
import folium
from folium.features import GeoJsonTooltip
import requests
import json
import os


# 1. Carregar os dados da escolaridade
df = pd.read_csv(r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\escolaridade_normalizada.csv")


# Carregar o CSV com separador de vírgula e corrigir nome das colunas
df = pd.read_csv(r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\escolaridade_normalizada.csv", sep=",", encoding="utf-8")
df.columns = ["Estado", "Baixa", "Media", "Alta"]


# Corrigir nomes de estados com caracteres incorretos
df["Estado"] = df["Estado"].str.upper().replace({
    "RONDÃ”NIA": "RONDÔNIA",
    "MARANHÃƒO": "MARANHÃO",
    "PARÃ": "PARÁ",
    "AMAPÃ": "AMAPÁ",
    "PIAUÃ": "PIAUÍ",
    "CEARÃ": "CEARÁ",
    "GOIÃS": "GOIÁS"
})


# Corrigir nomes para bater com GeoJSON
df["Estado"] = df["Estado"].replace({
    "RONDÔNIA": "Rondônia",
    "ACRE": "Acre",
    "AMAZONAS": "Amazonas",
    "RORAIMA": "Roraima",
    "PARÁ": "Pará",
    "AMAPÁ": "Amapá",
    "TOCANTINS": "Tocantins",
    "MARANHÃO": "Maranhão",
    "PIAUÍ": "Piauí",
    "CEARÁ": "Ceará",
    "RIO GRANDE DO NORTE": "Rio Grande do Norte",
    "PARAÍBA": "Paraíba",
    "PERNAMBUCO": "Pernambuco",
    "ALAGOAS": "Alagoas",
    "SERGIPE": "Sergipe",
    "BAHIA": "Bahia",
    "MINAS GERAIS": "Minas Gerais",
    "ESPÍRITO SANTO": "Espírito Santo",
    "RIO DE JANEIRO": "Rio de Janeiro",
    "SÃO PAULO": "São Paulo",
    "PARANÁ": "Paraná",
    "SANTA CATARINA": "Santa Catarina",
    "RIO GRANDE DO SUL": "Rio Grande do Sul",
    "MATO GROSSO DO SUL": "Mato Grosso do Sul",
    "MATO GROSSO": "Mato Grosso",
    "GOIÁS": "Goiás",
    "DISTRITO FEDERAL": "Distrito Federal"
})


# Classificar o estado conforme a maior categoria
def classificar_escolaridade(row):
    categorias = {"Baixa": row["Baixa"], "Media": row["Media"], "Alta": row["Alta"]}
    return max(categorias, key=categorias.get)


df["Categoria"] = df.apply(classificar_escolaridade, axis=1)


# Baixar GeoJSON se não estiver salvo
geo_path = "brazil-states.geojson"
if not os.path.exists(geo_path):
    geo_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    with open(geo_path, "w", encoding="utf-8") as f:
        f.write(requests.get(geo_url).text)


# Abrir o arquivo GeoJSON
with open(geo_path, encoding="utf-8") as f:
    geojson_data = json.load(f)


# Mapa de cores
cores = {
    "Baixa": "#7f0000",  # vermelho escuro
    "Media": "#cc0000",  # vermelho médio
    "Alta": "#ff9999",   # vermelho claro
}


# Adicionar a categoria escolaridade ao GeoJSON
for feature in geojson_data["features"]:
    nome = feature["properties"]["name"]
    row = df[df["Estado"] == nome]
    if not row.empty:
        categoria = row["Categoria"].values[0]
        feature["properties"]["Categoria"] = categoria
    else:
        feature["properties"]["Categoria"] = "Desconhecido"


# Criar mapa com folium
m = folium.Map(location=[-14.2, -51.9], zoom_start=4)


folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
        "fillColor": cores.get(feature["properties"]["Categoria"], "gray"),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    },
    tooltip=GeoJsonTooltip(
        fields=["name", "Categoria"],
        aliases=["Estado:", "Categoria Escolaridade:"],
        localize=True
    )
).add_to(m)


# Salvar o mapa
m.save("mapa_categoria_escolaridade.html")
print("✅ Mapa gerado: mapa_categoria_escolaridade.html")



