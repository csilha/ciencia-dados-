import pandas as pd
import matplotlib.pyplot as plt

# Caminho do seu arquivo CSV
caminho_csv = '../meta_dados/favela.csv'

# Lê o arquivo pulando cabeçalhos e usando o separador correto
df = pd.read_csv(caminho_csv, sep=';', skiprows=5, engine='python', header=None, on_bad_lines='skip')

# Renomeia as colunas principais (ajuste conforme necessário)
df.columns = [
    'Local', 'Grupo_idade', 'Total_geral', 'Total_homens', 'Total_mulheres',
    'Branca_total', 'Branca_homens', 'Branca_mulheres',
    'Preta_total', 'Preta_homens', 'Preta_mulheres',
    'Amarela_total', 'Amarela_homens', 'Amarela_mulheres',
    'Parda_total', 'Parda_homens', 'Parda_mulheres',
    'Indigena_total', 'Indigena_homens', 'Indigena_mulheres',
    'Sem_declaracao_total', 'Sem_declaracao_homens', 'Sem_declaracao_mulheres'
]

# Remove linhas que não têm dados válidos
df = df[df['Grupo_idade'].notna()]
df = df[df['Grupo_idade'] != 'Grupo de idade']

# Converte colunas numéricas
colunas_numericas = df.columns[2:]
df[colunas_numericas] = df[colunas_numericas].apply(pd.to_numeric, errors='coerce')

# Filtra apenas a linha "Total" (população total)
df_total = df[df['Grupo_idade'] == 'Total'].iloc[0]

# Organiza os dados para gráfico
racas = ['Branca', 'Preta', 'Parda', 'Amarela', 'Indígena', 'Sem declaração']
valores = [
    df_total['Branca_total'],
    df_total['Preta_total'],
    df_total['Parda_total'],
    df_total['Amarela_total'],
    df_total['Indigena_total'],
    df_total['Sem_declaracao_total']
]

# Gráfico
plt.figure(figsize=(10, 6))
plt.bar(racas, valores, color='skyblue')
plt.title('População residente em favelas por cor ou raça (Total - Brasil)')
plt.ylabel('População')
plt.xlabel('Cor ou raça')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
