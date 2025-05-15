import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import branca.colormap as cm
import json
import folium
from folium.features import GeoJsonTooltip

# ---------- CONFIGURAÇÕES DE ESTILO ----------
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

# ---------- CARREGAR DADOS ----------
df = pd.read_csv(
    r'C:/Users/Cecília Barbosa/Documents/000000_dados/ciencia-dados-/meta_dados/favela_quantitativo_por_munici.csv',
    sep=';', skiprows=5, encoding='utf-8', names=['Município', 'Quantidade'], header=None
)

# ---------- LIMPEZA ----------
df = df.dropna()
df = df[~df['Quantidade'].astype(str).str.contains('[a-zA-Z]')]
df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
df = df.dropna(subset=['Quantidade'])

# Extrair estado e nome limpo do município
df['Estado'] = df['Município'].str.extract(r'\((.*?)\)')
df['Município'] = df['Município'].str.replace(r'\(.*?\)', '', regex=True).str.strip()

# ---------- TOP 20 MUNICÍPIOS ----------
df_sorted = df.sort_values('Quantidade', ascending=False)
top_20 = df_sorted.head(20)

# ---------- GRÁFICO 1 ----------
plt.figure(figsize=(14, 8))
barplot = sns.barplot(data=top_20, x='Quantidade', y='Município', hue='Estado', dodge=False, palette='viridis')
plt.title('Top 20 Municípios com Mais Favelas no Brasil (2022)')
plt.xlabel('Número de Favelas')
plt.ylabel('Município')
plt.grid(axis='x')

for p in barplot.patches:
    width = p.get_width()
    if pd.notna(width):
        plt.text(width + 0.5, p.get_y() + p.get_height()/2, f'{int(width)}', ha='left', va='center')

plt.tight_layout()
plt.show()

# ---------- GRÁFICO 2 ----------
estados = df.groupby('Estado')['Quantidade'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(14, 6))
estados.plot(kind='bar', color='teal')
plt.title('Top 10 Estados com Mais Favelas (Soma por Estado)')
plt.xlabel('Estado')
plt.ylabel('Total de Favelas')
plt.xticks(rotation=45)
plt.grid(axis='y')

for i, v in enumerate(estados):
    plt.text(i, v + 1, str(int(v)), ha='center', va='bottom')

plt.tight_layout()
plt.show()

# ---------- ESTATÍSTICAS ----------
print("\n📊 Estatísticas Descritivas:\n")
print(f"Total de favelas no Brasil: {int(df['Quantidade'].sum()):,}")
print(f"Número total de municípios com favelas: {len(df)}")
print(f"Média de favelas por município: {df['Quantidade'].mean():.1f}")
print(f"Mediana de favelas por município: {df['Quantidade'].median():.1f}")
print(f"Município com mais favelas: {df_sorted.iloc[0]['Município']} ({df_sorted.iloc[0]['Estado']}) com {int(df_sorted.iloc[0]['Quantidade'])} favelas")

# ---------- TOP 5 MUNICÍPIOS POR ESTADO ----------
print("\n🏙️ Top 5 municípios por estado com mais favelas:")
top_by_state = df.sort_values(['Estado', 'Quantidade'], ascending=[True, False]).groupby('Estado').head(5)
print(top_by_state.groupby('Estado').apply(lambda x: x[['Município', 'Quantidade']].to_string(index=False)))

# ---------- MAPA INTERATIVO ----------
geolocator = Nominatim(user_agent="mapa_favelas")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

top_20['localizacao'] = top_20['Município'] + ', ' + top_20['Estado'] + ', Brasil'
top_20['coordenadas'] = top_20['localizacao'].apply(geocode)
top_20['latitude'] = top_20['coordenadas'].apply(lambda loc: loc.latitude if loc else None)
top_20['longitude'] = top_20['coordenadas'].apply(lambda loc: loc.longitude if loc else None)

# Criar mapa
mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

for _, row in top_20.iterrows():
    if pd.notna(row['latitude']) and pd.notna(row['longitude']):
        folium.CircleMarker(
            location=(row['latitude'], row['longitude']),
            radius=5 + row['Quantidade'] / 100,
            popup=f"{row['Município']} ({row['Estado']}) - {int(row['Quantidade'])} favelas",
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(mapa)

# Salvar mapa
mapa.save("mapa_top20_favelas.html")
print("\n🗺️ Mapa interativo salvo como 'mapa_top20_favelas.html'. Abra no navegador para visualizar.")
