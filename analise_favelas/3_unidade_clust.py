import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import seaborn as sns
from sklearn.metrics import silhouette_score
import geopandas as gpd
from geobr import read_state


# Carregar dados
file_path = r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\escolaridade_br_22_total.xlsx"
df = pd.read_excel(file_path)

# Remover linha do Brasil (total)
df = df[df['baixa'] != 'Brasil']

# Converter colunas para numérico
for col in ['baixa', 'media', 'alta']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Calcular total populacional e normalizar por 10 mil habitantes
df['total'] = df['baixa'] + df['media'] + df['alta']
df['baixa_10k'] = df['baixa'] / df['total'] * 10000
df['media_10k'] = df['media'] / df['total'] * 10000
df['alta_10k'] = df['alta'] / df['total'] * 10000

# Selecionar colunas normalizadas para clustering
X = df[['baixa_10k', 'media_10k', 'alta_10k']]

# Padronizar os dados
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Aplicar KMeans com 3 clusters
kmeans = KMeans(n_clusters=3, random_state=42)
df['cluster'] = kmeans.fit_predict(X_scaled)

# Plotar gráfico de dispersão
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='baixa_10k', y='alta_10k', hue='cluster', palette='Set2', s=100)
for i in range(df.shape[0]):
    plt.text(df['baixa_10k'].iloc[i], df['alta_10k'].iloc[i], df.index[i], fontsize=8)
plt.title('Clusters de Estados por Escolaridade (por 10 mil habitantes)')
plt.xlabel('População com Baixa Escolaridade (a cada 10 mil hab.)')
plt.ylabel('População com Alta Escolaridade (a cada 10 mil hab.)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Exibir resultado final
print(df[['baixa_10k', 'media_10k', 'alta_10k', 'cluster']])

# -----  teste do cluster = 3 -----
# Dados fornecidos anteriormente
data = {
    "Estado": [
        "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins", "Maranhão", "Piauí", "Ceará",
        "Rio Grande do Norte", "Paraíba", "Pernambuco", "Alagoas", "Sergipe", "Bahia", "Minas Gerais", "Espírito Santo",
        "Rio de Janeiro", "São Paulo", "Paraná", "Santa Catarina", "Rio Grande do Sul", "Mato Grosso do Sul", "Mato Grosso",
        "Goiás", "Distrito Federal", "Brasil"
    ],
    "baixa": [
        646097, 296474, 1224993, 179876, 3207626, 217908, 513562, 2678343, 1421076, 3549426, 1357806, 1680839, 3529336,
        1323710, 896104, 5879900, 7922097, 1396653, 5306787, 13551980, 4027128, 2607840, 4225103, 1132756, 1134497,
        2810822, 1057414, 73149578
    ],
    "media": [
        348066, 179961, 1073286, 168642, 1874741, 187665, 394849, 1608640, 706287, 2290925, 800681, 897675, 2372798,
        669520, 520086, 3616133, 5483064, 1051848, 4875302, 13692410, 3075397, 2134682, 2862843, 875082, 936630,
        2233689, 1343481, 55305618
    ],
    "alta": [
        164632, 84300, 342586, 67045, 601096, 89111, 176386, 466881, 304955, 759303, 339974, 390742, 852481, 267996,
        218255, 1146608, 2615434, 491101, 2371507, 7478587, 1687930, 1260173, 1488416, 419307, 382321, 1012348, 794406,
        25854291
    ]
}

df = pd.DataFrame(data)

# Calculando o total populacional estimado por estado
df["total"] = df["baixa"] + df["media"] + df["alta"]

# Normalizando por 10 mil habitantes
df["baixa_10mil"] = df["baixa"] / df["total"] * 10000
df["alta_10mil"] = df["alta"] / df["total"] * 10000

X = df[["baixa_10mil", "alta_10mil"]]

# Elbow method
inertias = []
silhouette_scores = []
ks = range(2, 8)

for k in ks:
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X, kmeans.labels_))

# Plot Elbow
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(ks, inertias, marker='o')
plt.title('Método do Cotovelo')
plt.xlabel('Número de Clusters (k)')
plt.ylabel('Inércia')

# Plot Silhouette
plt.subplot(1, 2, 2)
plt.plot(ks, silhouette_scores, marker='o', color='green')
plt.title('Coeficiente de Silhueta')
plt.xlabel('Número de Clusters (k)')
plt.ylabel('Silhouette Score')

plt.tight_layout()
plt.show()

# ----- mapa ------- 
import pandas as pd
import folium
from folium.features import GeoJsonTooltip
import json

# Dados de cluster (substitua pelos seus reais, se necessário)
dados = {
    "Estado": [
        "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal", "Espírito Santo", "Goiás",
        "Maranhão", "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará", "Paraíba", "Paraná",
        "Pernambuco", "Piauí", "Rio de Janeiro", "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", "Roraima",
        "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"
    ],
    "cluster": [
        2, 2, 2, 2, 2, 2, 1, 0, 1,
        2, 1, 0, 0, 2, 2, 0,
        2, 2, 0, 2, 0, 2, 2,
        0, 0, 2, 2
    ]
}
df = pd.DataFrame(dados)

# Carregar GeoJSON local
with open("brazil-states.geojson", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Associar cluster a cada estado no GeoJSON
for feature in geojson_data["features"]:
    nome = feature["properties"]["name"]
    row = df[df["Estado"] == nome]
    if not row.empty:
        cluster = row["cluster"].values[0]
        feature["properties"]["cluster"] = int(cluster)
    else:
        feature["properties"]["cluster"] = "Desconhecido"

# Definir cores para os clusters
cores = {
    0: "#2ca02c",  # verde
    1: "#ff7f0e",  # laranja
    2: "#1f77b4"   # azul
}

# Criar o mapa
m = folium.Map(location=[-14.2, -51.9], zoom_start=4)

# Adicionar os estados ao mapa
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

# Salvar o mapa
m.save("mapa_clusters_escolaridade.html")
print("✅ Mapa salvo como mapa_clusters_escolaridade.html")
