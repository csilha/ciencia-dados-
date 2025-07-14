
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import seaborn as sns
from sklearn.metrics import silhouette_score
import folium
from folium.features import GeoJsonTooltip
import json
import requests
import os

# ---------- PARTE 1: Análise e Clusterização ----------

# 1. Carregar Excel e tratar colunas
df = pd.read_excel(r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\escolaridade_br_22_total.xlsx")

if df.columns[0] != 'Estado':
    df.rename(columns={df.columns[0]: 'Estado'}, inplace=True)

# Remover linha do Brasil
df = df[df['Estado'].str.lower() != 'brasil']

# Converter colunas para numérico
for col in ['baixa', 'media', 'alta']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Calcular total e proporções
df['total'] = df['baixa'] + df['media'] + df['alta']
df['baixa_10k'] = df['baixa'] / df['total'] * 10000
df['media_10k'] = df['media'] / df['total'] * 10000
df['alta_10k'] = df['alta'] / df['total'] * 10000

# Normalizar e aplicar KMeans
X = df[['baixa_10k', 'media_10k', 'alta_10k']]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)

# Plotar dispersão
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='baixa_10k', y='alta_10k', hue='cluster', palette='Set2', s=100)
for i in range(df.shape[0]):
    plt.text(df['baixa_10k'].iloc[i], df['alta_10k'].iloc[i], df['Estado'].iloc[i][:2], fontsize=8)
plt.title('Clusters de Estados por Escolaridade (por 10 mil habitantes)')
plt.xlabel('População com Baixa Escolaridade (a cada 10 mil hab.)')
plt.ylabel('População com Alta Escolaridade (a cada 10 mil hab.)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Avaliação de clusters
inertias = []
silhouette_scores = []
ks = range(2, 8)

for k in ks:
    kmeans_k = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans_k.fit(X_scaled)
    inertias.append(kmeans_k.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans_k.labels_))

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(ks, inertias, marker='o')
plt.title('Método do Cotovelo')
plt.xlabel('Número de Clusters (k)')
plt.ylabel('Inércia')

plt.subplot(1, 2, 2)
plt.plot(ks, silhouette_scores, marker='o', color='green')
plt.title('Coeficiente de Silhueta')
plt.xlabel('Número de Clusters (k)')
plt.ylabel('Silhouette Score')
plt.tight_layout()
plt.show()

# ---------- PARTE 2: Mapa com Folium ----------

# Baixar GeoJSON diretamente se não existir
geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
geojson_path = "brazil-states.geojson"

if not os.path.exists(geojson_path):
    with open(geojson_path, "w", encoding="utf-8") as f:
        f.write(requests.get(geojson_url).text)

# Carregar GeoJSON
with open(geojson_path, encoding="utf-8") as f:
    geojson_data = json.load(f)

# Mapear cluster para cada estado no GeoJSON
for feature in geojson_data["features"]:
    nome = feature["properties"]["name"]
    row = df[df["Estado"] == nome]
    if not row.empty:
        feature["properties"]["cluster"] = int(row["cluster"].values[0])
    else:
        feature["properties"]["cluster"] = "Desconhecido"

# Definir cores
cores = {
    0: "#2ca02c",
    1: "#ff7f0e",
    2: "#1f77b4"
}

# Criar o mapa
m = folium.Map(location=[-14.2, -51.9], zoom_start=4)

folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
        "fillColor": cores.get(feature["properties"]["cluster"], "gray"),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    },
    tooltip=GeoJsonTooltip(
        fields=["name", "cluster"],
        aliases=["Estado:", "Cluster Escolaridade:"],
        localize=True
    )
).add_to(m)

map_file_path = "mapa_clusters_escolaridade.html"
m.save(map_file_path)
print(f"✅ Mapa salvo como {map_file_path}")
