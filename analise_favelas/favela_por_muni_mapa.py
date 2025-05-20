import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.features import GeoJsonTooltip
import branca.colormap as cm
import requests
import json
import os

# ------------------ 1. LER E LIMPAR DADOS ------------------

# Caminho do seu CSV
csv_path = r'C:/Users/Cecília Barbosa/Documents/000000_dados/ciencia-dados-/meta_dados/favela_quantitativo_por_munici.csv'

# Carregar dados ignorando cabeçalhos extras
df = pd.read_csv(csv_path, sep=';', skiprows=5, encoding='utf-8', names=['Município', 'Quantidade'], header=None)

# Limpeza
df = df.dropna()
df = df[~df['Quantidade'].astype(str).str.contains('[a-zA-Z]')]
df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
df = df.dropna(subset=['Quantidade'])

# Extrair Estado do nome do município
df['Estado'] = df['Município'].str.extract(r'\((.*?)\)')
df['Município'] = df['Município'].str.replace(r'\(.*?\)', '', regex=True).str.strip()

# Agrupar por estado
df_estados = df.groupby("Estado")["Quantidade"].sum().reset_index()

# Mapeamento de siglas para nomes completos
sigla_para_nome = {
    'AC': 'Acre',
    'AL': 'Alagoas',
    'AM': 'Amazonas',
    'AP': 'Amapá',
    'BA': 'Bahia',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'ES': 'Espírito Santo',
    'GO': 'Goiás',
    'MA': 'Maranhão',
    'MG': 'Minas Gerais',
    'MS': 'Mato Grosso do Sul',
    'MT': 'Mato Grosso',
    'PA': 'Pará',
    'PB': 'Paraíba',
    'PE': 'Pernambuco',
    'PI': 'Piauí',
    'PR': 'Paraná',
    'RJ': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte',
    'RO': 'Rondônia',
    'RR': 'Roraima',
    'RS': 'Rio Grande do Sul',
    'SC': 'Santa Catarina',
    'SE': 'Sergipe',
    'SP': 'São Paulo',
    'TO': 'Tocantins'
}

# Substituir as siglas pelas formas completas
df_estados['Estado'] = df_estados['Estado'].map(sigla_para_nome)


# Corrigir possíveis nomes que venham sem acento (por segurança)
df_estados['Estado'] = df_estados['Estado'].replace({
    "Rondonia": "Rondônia",
    "Amapa": "Amapá",
    "Para": "Pará",
    "Maranhao": "Maranhão",
    "Piaui": "Piauí",
    "Goias": "Goiás",
    "Sao Paulo": "São Paulo",
    "Espirito Santo": "Espírito Santo"
})

# ------------------ 2. BAIXAR E CARREGAR GEOJSON ------------------

geo_path = "brazil-states.geojson"
if not os.path.exists(geo_path):
    print("🔽 Baixando GeoJSON...")
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    r = requests.get(url)
    with open(geo_path, "w", encoding="utf-8") as f:
        f.write(r.text)
    print("✔️ Arquivo GeoJSON salvo com sucesso!")

# Carregar o geojson
with open(geo_path, encoding='utf-8') as f:
    geojson_data = json.load(f)

# ------------------ 3. ASSOCIAR OS DADOS AO GEOJSON ------------------

# Adicionar valor de favelas por estado diretamente no geojson
for feature in geojson_data['features']:
    estado_nome = feature['properties']['name']
    valor = df_estados[df_estados['Estado'] == estado_nome]['Quantidade']
    feature['properties']['favelas'] = float(valor.values[0]) if not valor.empty else 0.0

# ------------------ 4. CRIAR MAPA COM GRADIENTE VERMELHO ------------------

# Criar mapa
mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

# Escala de cores (Reds)
max_favelas = df_estados['Quantidade'].max()
colormap = cm.linear.Reds_09.scale(0, max_favelas)
colormap.caption = "Total de Favelas por Estado"

# Adicionar camada com gradiente
folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
        'fillColor': colormap(feature['properties']['favelas']),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.8,
    },
    tooltip=GeoJsonTooltip(
        fields=["name", "favelas"],
        aliases=["Estado:", "Total de Favelas:"],
        localize=True
    )
).add_to(mapa)

# Adicionar legenda
colormap.add_to(mapa)

# ------------------ 5. SALVAR E FINALIZAR ------------------

mapa.save("mapa_qtd_favelas_gradiente_vermelho.html")
print("🗺️ Mapa com gradiente vermelho salvo como 'mapa_qtd_favelas_gradiente_vermelho.html'")
