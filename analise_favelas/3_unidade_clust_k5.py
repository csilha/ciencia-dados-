import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import folium
from folium.features import GeoJsonTooltip
import json
import requests
import seaborn as sns

# === Carregar dados ===
file_path = r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\escolaridade_br_22_total.xlsx"
df = pd.read_excel(file_path)

# Renomear coluna de estados
df = df.rename(columns={"Unnamed: 0": "UF"})

# Calcular total e normalizar por 10 mil habitantes
df["total"] = df["baixa"] + df["media"] + df["alta"]
df["baixa_10k"] = df["baixa"] / df["total"] * 10000
df["media_10k"] = df["media"] / df["total"] * 10000
df["alta_10k"] = df["alta"] / df["total"] * 10000

# Matriz para clustering
X = df[["baixa_10k", "media_10k", "alta_10k"]]
X_scaled = StandardScaler().fit_transform(X)

# KMeans com k=5
kmeans = KMeans(n_clusters=5, n_init=10, random_state=42)
df["cluster"] = kmeans.fit_predict(X_scaled)

#----- clustering --- 

# Siglas para os estados
siglas_estados = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA", "Ceará": "CE",
    "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA",
    "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG", "Pará": "PA",
    "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI", "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR",
    "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE", "Tocantins": "TO"
}
df["sigla"] = df["UF"].map(siglas_estados)

# Gráfico de dispersão
plt.figure(figsize=(10, 6))
# Paleta personalizada para o gráfico
palette_personalizada = {
    0: "#1f77b4",  # azul
    1: "#ff7f0e",  # laranja
    2: "#2ca02c",  # verde
    3: "#d62728",  # vermelho
    4: "#9467bd",  # roxo
}

sns.scatterplot(
    data=df,
    x="baixa_10k",
    y="alta_10k",
    hue="cluster",
    palette=palette_personalizada,
    s=100,
    legend="full"
)

# Adicionar siglas dos estados
for i in range(df.shape[0]):
    plt.text(
        df["baixa_10k"].iloc[i] + 15,
        df["alta_10k"].iloc[i],
        df["sigla"].iloc[i],
        fontsize=9
    )

plt.title("Clusters de Estados por Escolaridade (por 10 mil habitantes)")
plt.xlabel("População com Baixa Escolaridade (a cada 10 mil hab.)")
plt.ylabel("População com Alta Escolaridade (a cada 10 mil hab.)")
plt.grid(True)
plt.tight_layout()
plt.show()

# === Baixar GeoJSON diretamente da internet ===
geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
geojson_data = requests.get(geojson_url).json()

# Mapeamento de nomes entre 'UF' e GeoJSON
mapeamento_nomes = {
    "Acre": "Acre",
    "Alagoas": "Alagoas",
    "Amapá": "Amapá",
    "Amazonas": "Amazonas",
    "Bahia": "Bahia",
    "Ceará": "Ceará",
    "Distrito Federal": "Distrito Federal",
    "Espírito Santo": "Espírito Santo",
    "Goiás": "Goiás",
    "Maranhão": "Maranhão",
    "Mato Grosso": "Mato Grosso",
    "Mato Grosso do Sul": "Mato Grosso do Sul",
    "Minas Gerais": "Minas Gerais",
    "Pará": "Pará",
    "Paraíba": "Paraíba",
    "Paraná": "Paraná",
    "Pernambuco": "Pernambuco",
    "Piauí": "Piauí",
    "Rio de Janeiro": "Rio de Janeiro",
    "Rio Grande do Norte": "Rio Grande do Norte",
    "Rio Grande do Sul": "Rio Grande do Sul",
    "Rondônia": "Rondônia",
    "Roraima": "Roraima",
    "Santa Catarina": "Santa Catarina",
    "São Paulo": "São Paulo",
    "Sergipe": "Sergipe",
    "Tocantins": "Tocantins"
}

df["estado_geojson"] = df["UF"].map(mapeamento_nomes)

# Atualizar GeoJSON com clusters
for feature in geojson_data["features"]:
    nome = feature["properties"]["name"]
    row = df[df["estado_geojson"] == nome]
    if not row.empty:
        feature["properties"]["cluster"] = int(row["cluster"].values[0])
    else:
        feature["properties"]["cluster"] = "Desconhecido"

# Paleta de cores para 5 clusters
cores = {
    0: "#1f77b4",  # azul
    1: "#ff7f0e",  # laranja
    2: "#2ca02c",  # verde
    3: "#d62728",  # vermelho
    4: "#9467bd",  # roxo
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

# Salvar o mapa
map_file_path = "mapa_clusters_escolaridade.html"
m.save(map_file_path)
print(f"✅ Mapa salvo como {map_file_path}")
