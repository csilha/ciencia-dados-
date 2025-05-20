import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import json
import requests

# ----------------------------
# Caminhos dos arquivos
# ----------------------------
xlsx_path = "C:/Users/Cecília Barbosa/Documents/000000_dados/ciencia-dados-/meta_dados/pop_br_estado_anos.xlsx"
csv_path = "C:/Users/Cecília Barbosa/Documents/000000_dados/ciencia-dados-/meta_dados/pop_favela_uf_2010.csv"

# ----------------------------
# Lista de estados
# ----------------------------
estados = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba", "Pernambuco",
    "Alagoas", "Sergipe", "Bahia", "Minas Gerais", "Espírito Santo", "Rio de Janeiro",
    "São Paulo", "Paraná", "Santa Catarina", "Rio Grande do Sul", "Mato Grosso do Sul",
    "Mato Grosso", "Goiás", "Distrito Federal"
]

# ----------------------------
# Função para limpar números brasileiros
# ----------------------------
def limpar_numero_brasileiro(valores):
    resultados = []
    for val in valores:
        try:
            val_str = str(val).strip().replace(".", "").replace(",", ".")
            val_float = float(val_str)
            resultados.append(int(val_float))
        except Exception:
            resultados.append(0)
    return resultados

# ----------------------------
# Leitura dos dados
# ----------------------------
df_excel = pd.read_excel(xlsx_path, engine="openpyxl")
pop_total_raw = df_excel.iloc[2:30, 12]  # População total por estado (coluna M)
pop_total = limpar_numero_brasileiro(pop_total_raw)

df_csv = pd.read_csv(csv_path, sep=";", skiprows=5, names=["Estado", "Populacao_Favela"])
df_csv = df_csv[df_csv["Estado"].isin(estados)]
df_csv["Populacao_Favela"] = df_csv["Populacao_Favela"].astype(str).str.replace(".", "", regex=False)
df_csv["Populacao_Favela"] = df_csv["Populacao_Favela"].astype(int)

# ----------------------------
# Construção do DataFrame final
# ----------------------------
df = pd.DataFrame({
    "Estado": estados,
    "Populacao_Total": pop_total,
    "Populacao_Favela": df_csv["Populacao_Favela"].values
})
df["Populacao_Formal"] = df["Populacao_Total"] - df["Populacao_Favela"]
df["Proporcao_por_10mil"] = (df["Populacao_Favela"] / df["Populacao_Total"]) * 10000
df["Percentual_Favela"] = (df["Populacao_Favela"] / df["Populacao_Total"]) * 100
df = df.sort_values(by="Proporcao_por_10mil", ascending=False)

# ----------------------------
# Gráfico: proporção por 10 mil habitantes
# ----------------------------
plt.figure(figsize=(12, 8))
sns.barplot(data=df, x="Proporcao_por_10mil", y="Estado")
plt.xlabel("Moradores de favela por 10 mil habitantes")
plt.ylabel("Estado")
plt.title("Proporção de moradores de favelas por 10 mil habitantes (Censo 2010)")
plt.grid(True, axis="x")
plt.xlim(0, 4000)  # Limite no eixo X até 4 mil
plt.tight_layout()
plt.show()

# ----------------------------
# Gráfico: Top 10 em números absolutos (com limite no eixo X)
# ----------------------------
top10_absoluto = df.sort_values(by="Populacao_Favela", ascending=False).head(10)
plt.figure(figsize=(12, 6))
sns.barplot(data=top10_absoluto, x='Populacao_Favela', y='Estado')
plt.xlabel('Número absoluto de pessoas em favelas')
plt.ylabel('Estado')
plt.title('Top 10 estados com mais pessoas vivendo em favelas')
plt.grid(True, axis='x')
plt.xlim(0, 4000000)  # Limite no eixo X até 4 milhões
plt.tight_layout()
plt.show()


# ----------------------------
# Gráfico: Barras empilhadas com porcentagem
# ----------------------------
df_empilhado = df.sort_values(by="Populacao_Total")
plt.figure(figsize=(14, 8))
plt.bar(df_empilhado["Estado"], df_empilhado["Populacao_Formal"], label="Área urbanizada formal", color="lightgray")
bars_favela = plt.bar(
    df_empilhado["Estado"],
    df_empilhado["Populacao_Favela"],
    bottom=df_empilhado["Populacao_Formal"],
    label="Favelas",
    color="red"
)

for i, bar in enumerate(bars_favela):
    total = bar.get_height() + bar.get_y()
    percentual = df_empilhado.iloc[i]["Percentual_Favela"]
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        total + df["Populacao_Total"].max() * 0.005,
        f"{percentual:.1f}%",
        ha='center',
        va='bottom',
        fontsize=8,
        color="black"
    )

plt.ylabel("População")
plt.xlabel("Estado")
plt.title("População por estado com destaque para favelas (Censo 2010)")
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.show()

# ----------------------------
# NOVO GRÁFICO DE DISPERSÃO
# ----------------------------

# (re)calcular a coluna Percentual_Favela se ainda não existir
if "Percentual_Favela" not in df.columns:
    df["Percentual_Favela"] = (df["Populacao_Favela"] / df["Populacao_Total"]) * 100

# Remover os dois estados com menor e maior percentual
df_dispersao = df.sort_values(by="Percentual_Favela").iloc[2:-2]

# Calcular a média dos percentuais (com dados filtrados)
media_percentual = df_dispersao["Percentual_Favela"].mean()

# Calcular desvio da média
df_dispersao["Desvio_da_Media"] = df_dispersao["Percentual_Favela"] - media_percentual

# Criar gráfico de dispersão
plt.figure(figsize=(12, 6))
sns.scatterplot(
    data=df_dispersao,
    x="Estado",
    y="Percentual_Favela",
    hue="Desvio_da_Media",
    palette="coolwarm",
    s=100
)
plt.axhline(media_percentual, color='gray', linestyle='--', label=f'Média: {media_percentual:.2f}%')
plt.xticks(rotation=45)
plt.ylabel("Percentual de população em favelas 2010(%)")
plt.title("Dispersão dos percentuais de moradores em favelas por estado\n(desconsiderando os 2 maiores e 2 menores)")
plt.legend()
plt.grid(True, axis='y')
plt.tight_layout()
plt.show()


# ----------------------------
# Mapa interativo com gradiente
# ----------------------------
url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
response = requests.get(url)
with open("brazil-states.geojson", "w", encoding='utf-8') as f:
    f.write(response.text)

with open("brazil-states.geojson", encoding='utf-8') as f:
    geojson_data = json.load(f)

# Corrigir nomes (caso necessário)
df['Estado'] = df['Estado'].replace({
    "Rondonia": "Rondônia", "Amapa": "Amapá", "Para": "Pará", "Maranhao": "Maranhão",
    "Piaui": "Piauí", "Ceara": "Ceará", "Paraiba": "Paraíba", "Espirito Santo": "Espírito Santo",
    "Sao Paulo": "São Paulo", "Parana": "Paraná", "Goias": "Goiás"
})

# Criar e salvar o mapa
mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)
folium.Choropleth(
    geo_data=geojson_data,
    data=df,
    columns=['Estado', 'Proporcao_por_10mil'],
    key_on='feature.properties.name',
    fill_color='Reds',
    fill_opacity=0.7,
    line_opacity=0.3,
    nan_fill_color='gray',
    legend_name='Moradores de favelas por 10 mil habitantes (Censo 2010)'
).add_to(mapa)

mapa.save("mapa_gradiente_favelas_2010.html")
print("🗺️ Mapa interativo salvo como 'mapa_gradiente_favelas_2010.html'")
