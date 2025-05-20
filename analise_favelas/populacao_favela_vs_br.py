import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import locale
import platform

# Configurar locale para interpretar número no formato brasileiro
if platform.system() == "Windows":
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
else:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Caminhos dos arquivos
xlsx_path = "C:/Users/Cecília Barbosa/Documents/000000_dados/ciencia-dados-/meta_dados/brasil_populacao_por_uf.xlsx"
csv_path = "C:/Users/Cecília Barbosa/Documents/000000_dados/ciencia-dados-/meta_dados/favela_popu_por_uf.csv"

# Lista de estados na ordem correta
estados = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba", "Pernambuco",
    "Alagoas", "Sergipe", "Bahia", "Minas Gerais", "Espírito Santo", "Rio de Janeiro",
    "São Paulo", "Paraná", "Santa Catarina", "Rio Grande do Sul", "Mato Grosso do Sul",
    "Mato Grosso", "Goiás", "Distrito Federal"
]

# Função para limpar e converter valores numéricos formatados (com pontos, espaços, etc.)
def limpar_com_locale(valores):
    resultados = []
    for val in valores:
        try:
            val_str = str(val).strip().replace(" ", "")  # remove espaços entre os milhares
            val_float = locale.atof(val_str)
            resultados.append(int(val_float))
        except Exception:
            resultados.append(0)
    return resultados

# ----------------------------
# Ler dados do Excel
# ----------------------------
df_excel = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
pop_total_raw = df_excel.iloc[10:37, 2]  # População total (coluna C, linhas 11 a 37)
pop_total = limpar_com_locale(pop_total_raw)

# ----------------------------
# Ler dados do CSV
# ----------------------------
df_csv = pd.read_csv(csv_path, sep=";", header=None, encoding="utf-8")
pop_favela_raw = df_csv.iloc[7:34, 2]  # População favela (coluna C, linhas 8 a 34)
pop_favela = limpar_com_locale(pop_favela_raw)

# ----------------------------
# Montar DataFrame final
# ----------------------------
df = pd.DataFrame({
    "Estado": estados,
    "Populacao_Total": pop_total,
    "Populacao_Favela": pop_favela
})

# Verificação de erro
erros = df[df["Populacao_Favela"] > df["Populacao_Total"]]
if not erros.empty:
    print("⚠️ ERRO: População em favelas maior que a total em alguns estados:")
    print(erros)
    exit()

# Calcular proporção por 10 mil habitantes
df["Proporcao_por_10mil"] = (df["Populacao_Favela"] / df["Populacao_Total"]) * 10000
df = df.sort_values(by="Proporcao_por_10mil", ascending=False)

# ----------------------------
# Exibir gráfico
# ----------------------------
plt.figure(figsize=(12, 8))
sns.barplot(data=df, x="Proporcao_por_10mil", y="Estado")
plt.xlabel("Moradores de favela por 10 mil habitantes")
plt.ylabel("Estado")
plt.title("Proporção de moradores de favelas a cada 10 mil habitantes por estado")
plt.grid(True, axis="x")
plt.xlim(0, 4000)  # Limite no eixo X até 4 mil
plt.tight_layout()
plt.show()

# -------------------------------
# Top 10 estados com maior número absoluto de moradores em favelas
# -------------------------------
top10_absoluto = df.sort_values(by="Populacao_Favela", ascending=False).head(10)

print("\n🧭 Top 10 estados com mais pessoas vivendo em favelas (número absoluto):")
print(top10_absoluto[["Estado", "Populacao_Favela"]].to_string(index=False))

# -------------------------------
# Gráfico dos 10 estados com mais pessoas em favelas (absoluto)
# -------------------------------
plt.figure(figsize=(12, 6))
sns.barplot(data=top10_absoluto, x='Populacao_Favela', y='Estado')
plt.xlabel('Número de pessoas vivendo em favelas')
plt.ylabel('Estado')
plt.title('Top 10 estados com maior número absoluto de pessoas vivendo em favelas')
plt.grid(True, axis='x')
plt.xlim(0, 4000000)  # Limite no eixo X até 4 milhões
plt.tight_layout()
plt.show()

# -------------------------------
# Gráfico de barras empilhadas com porcentagem sobre favelas
# -------------------------------

# Ordenar os dados por população total
df_empilhado = df.sort_values(by="Populacao_Total")

# Calcular população fora de favelas
df_empilhado["Populacao_Formal"] = df_empilhado["Populacao_Total"] - df_empilhado["Populacao_Favela"]

# Calcular a porcentagem de favelas
df_empilhado["Percentual_Favela"] = (df_empilhado["Populacao_Favela"] / df_empilhado["Populacao_Total"]) * 100

# Criar gráfico
plt.figure(figsize=(14, 8))
plt.bar(df_empilhado["Estado"], df_empilhado["Populacao_Formal"], label="Área urbanizada formal", color="lightgray")
bars_favela = plt.bar(
    df_empilhado["Estado"],
    df_empilhado["Populacao_Favela"],
    bottom=df_empilhado["Populacao_Formal"],
    label="Favelas",
    color="red"
)

# Adicionar porcentagem no topo da parte vermelha (favelas)
for i, bar in enumerate(bars_favela):
    height = bar.get_height()
    bottom = bar.get_y()
    total = height + bottom
    percentual = df_empilhado.iloc[i]["Percentual_Favela"]
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        total + df_empilhado["Populacao_Total"].max() * 0.005,  # deslocamento vertical
        f"{percentual:.1f}%",
        ha='center',
        va='bottom',
        fontsize=8,
        color="black"
    )

plt.ylabel("População")
plt.xlabel("Estado")
plt.title("População total por estado com destaque e porcentagem de moradores em favelas")
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
plt.ylabel("Percentual de população em favelas 2022 (%)")
plt.title("Dispersão dos percentuais de moradores em favelas por estado\n(desconsiderando os 2 maiores e 2 menores)")
plt.legend()
plt.grid(True, axis='y')
plt.tight_layout()
plt.show()


# ---- mapa ------------
import folium
import json
import requests

url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
response = requests.get(url)

with open("brazil-states.geojson", "w", encoding='utf-8') as f:
    f.write(response.text)

print("✔️ Arquivo GeoJSON salvo como 'brazil-states.geojson'")


with open("brazil-states.geojson", encoding='utf-8') as f:
    geojson_data = json.load(f)


# Abrir o GeoJSON salvo anteriormente
with open("brazil-states.geojson", encoding='utf-8') as f:
    geojson_data = json.load(f)

# Corrigir possíveis divergências de acentuação
df['Estado'] = df['Estado'].replace({
    "Rondonia": "Rondônia",
    "Amapa": "Amapá",
    "Para": "Pará",
    "Maranhao": "Maranhão",
    "Piaui": "Piauí",
    "Ceara": "Ceará",
    "Paraiba": "Paraíba",
    "Pernambuco": "Pernambuco",
    "Alagoas": "Alagoas",
    "Sergipe": "Sergipe",
    "Bahia": "Bahia",
    "Minas Gerais": "Minas Gerais",
    "Espirito Santo": "Espírito Santo",
    "Rio de Janeiro": "Rio de Janeiro",
    "Sao Paulo": "São Paulo",
    "Parana": "Paraná",
    "Santa Catarina": "Santa Catarina",
    "Rio Grande do Sul": "Rio Grande do Sul",
    "Mato Grosso do Sul": "Mato Grosso do Sul",
    "Mato Grosso": "Mato Grosso",
    "Goias": "Goiás",
    "Distrito Federal": "Distrito Federal"
})

# Criar o mapa
mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

# Adicionar o gradiente de cor com os nomes dos estados
folium.Choropleth(
    geo_data=geojson_data,
    data=df,
    columns=['Estado', 'Proporcao_por_10mil'],
    key_on='feature.properties.name',
    fill_color='Reds',
    fill_opacity=0.7,
    line_opacity=0.3,
    nan_fill_color='gray',
    legend_name='Moradores de favelas por 10 mil habitantes'
).add_to(mapa)

# Salvar o mapa
mapa.save("mapa_gradiente_favelas.html")
print("🗺️ Mapa com gradiente de vermelho salvo como 'mapa_gradiente_favelas.html'")
