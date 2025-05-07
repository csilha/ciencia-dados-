import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração de estilo
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

# Carregar os dados
# Pulando as primeiras 5 linhas que contêm metadados e cabeçalhos
df = pd.read_csv(r'C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\favela_brasil.csv', sep=';', skiprows=5, encoding='utf-8', 
                 names=['Município', 'Quantidade'], header=None)

# Limpeza dos dados
# Remover linhas com valores nulos ou inválidos
df = df.dropna()
df = df[~df['Quantidade'].astype(str).str.contains('[a-zA-Z]')]  # Remove linhas com texto na coluna de quantidade

# Converter quantidade para numérico
df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
df = df.dropna(subset=['Quantidade'])

# Extrair estado do nome do município (está entre parênteses)
df['Estado'] = df['Município'].str.extract(r'\((.*?)\)')
df['Município'] = df['Município'].str.replace(r'\(.*?\)', '', regex=True).str.strip()

# Ordenar por quantidade de favelas
df_sorted = df.sort_values('Quantidade', ascending=False)

# Top 20 municípios com mais favelas
top_20 = df_sorted.head(20)

# Gráfico 1: Top 20 municípios com mais favelas
plt.figure(figsize=(14, 8))
barplot = sns.barplot(data=top_20, x='Quantidade', y='Município', hue='Estado', dodge=False, palette='viridis')
plt.title('Top 20 Municípios com Mais Favelas no Brasil (2022)')
plt.xlabel('Número de Favelas')
plt.ylabel('Município')
plt.grid(axis='x')

# Adicionar os valores nas barras
for p in barplot.patches:
    width = p.get_width()
    plt.text(width + 5, p.get_y() + p.get_height()/2, f'{int(width)}', ha='left', va='center')

plt.tight_layout()
plt.show()

# Gráfico 2: Distribuição por estado (top 10)
estados = df.groupby('Estado')['Quantidade'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(14, 6))
estados.plot(kind='bar', color='teal')
plt.title('Top 10 Estados com Mais Favelas (Soma por Estado)')
plt.xlabel('Estado')
plt.ylabel('Total de Favelas')
plt.xticks(rotation=45)
plt.grid(axis='y')

# Adicionar os valores nas barras
for i, v in enumerate(estados):
    plt.text(i, v + 50, str(int(v)), ha='center', va='bottom')

plt.tight_layout()
plt.show()


# Estatísticas descritivas
print("\nEstatísticas Descritivas:\n")
print(f"Total de favelas no Brasil: {df['Quantidade'].sum():,}")
print(f"Número total de municípios com favelas: {len(df)}")
print(f"Média de favelas por município: {df['Quantidade'].mean():.1f}")
print(f"Município com mais favelas: {df_sorted.iloc[0]['Município']} ({df_sorted.iloc[0]['Estado']}) com {df_sorted.iloc[0]['Quantidade']} favelas")
print(f"Mediana de favelas por município: {df['Quantidade'].median()}")

# Top 5 municípios por estado
print("\nTop 5 municípios por estado (com mais favelas):")
top_by_state = df.sort_values(['Estado', 'Quantidade'], ascending=[True, False]).groupby('Estado').head(5)
print(top_by_state.groupby('Estado').apply(lambda x: x[['Município', 'Quantidade']].to_string(index=False)))