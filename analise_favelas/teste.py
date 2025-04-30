import pandas as pd
import matplotlib.pyplot as plt

# Configuração do estilo dos gráficos
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

# Carregar os dados
caminho_completo = r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\analise_favelas\favela_brasil.csv"
df = pd.read_csv(caminho_completo, sep=';', encoding='utf-8', skiprows=2)

# Limpar e processar os dados
# Remover a linha do total Brasil
df = df[~df['Brasil e Município'].str.contains('Brasil', na=False)]

# Extrair estado da coluna de município
df[['Município', 'Estado']] = df['Brasil e Município'].str.extract(r'(.+)\s\(([A-Z]{2})\)')

# Converter a coluna de valores para numérico
df['2022'] = pd.to_numeric(df['2022'], errors='coerce')

# Agrupar por estado e somar o número de favelas
estados_df = df.groupby('Estado')['2022'].sum().reset_index()
estados_df = estados_df.sort_values('2022', ascending=False).head(10)

# Pegar os 10 municípios com mais favelas
municipios_df = df.sort_values('2022', ascending=False).head(10)

# Criar os gráficos
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Gráfico dos estados
ax1.barh(estados_df['Estado'], estados_df['2022'], color='skyblue')
ax1.set_title('Top 10 Estados com Mais Favelas (2022)')
ax1.set_xlabel('Número de Favelas')
ax1.set_ylabel('Estado')
for i, v in enumerate(estados_df['2022']):
    ax1.text(v + 3, i, str(v), color='black', va='center')

# Gráfico dos municípios
ax2.barh(municipios_df['Município'], municipios_df['2022'], color='salmon')
ax2.set_title('Top 10 Municípios com Mais Favelas (2022)')
ax2.set_xlabel('Número de Favelas')
ax2.set_ylabel('Município')
for i, v in enumerate(municipios_df['2022']):
    ax2.text(v + 3, i, str(v), color='black', va='center')

plt.tight_layout()
plt.show()

# Mostrar os dados em forma de tabela também
print("\nTop 10 Estados com mais favelas:")
print(estados_df.to_string(index=False))

print("\nTop 10 Municípios com mais favelas:")
print(municipios_df[['Município', 'Estado', '2022']].to_string(index=False))