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

# Remove linhas inválidas
df = df[df['Grupo_idade'].notna()]
df = df[df['Grupo_idade'] != 'Grupo de idade']

# Converte colunas numéricas
colunas_numericas = df.columns[2:]
df[colunas_numericas] = df[colunas_numericas].apply(pd.to_numeric, errors='coerce')

# ---------- Gráfico 1: Cor/Raça por Gênero ----------
df_total = df[df['Grupo_idade'] == 'Total'].iloc[0]

racas = ['Branca', 'Preta', 'Parda', 'Amarela', 'Indígena', 'Sem declaração']
homens = [
    df_total['Branca_homens'], df_total['Preta_homens'], df_total['Parda_homens'],
    df_total['Amarela_homens'], df_total['Indigena_homens'], df_total['Sem_declaracao_homens']
]
mulheres = [
    df_total['Branca_mulheres'], df_total['Preta_mulheres'], df_total['Parda_mulheres'],
    df_total['Amarela_mulheres'], df_total['Indigena_mulheres'], df_total['Sem_declaracao_mulheres']
]

x = range(len(racas))
plt.figure(figsize=(10, 6))
bar1 = plt.bar(x, homens, width=0.4, label='Homens', align='center')
bar2 = plt.bar([p + 0.4 for p in x], mulheres, width=0.4, label='Mulheres', align='center')

# Adiciona valores numéricos no topo das barras
for i, (h, m) in enumerate(zip(homens, mulheres)):
    plt.text(i, h + max(homens) * 0.01, f'{int(h):,}', ha='center', fontsize=8)
    plt.text(i + 0.4, m + max(mulheres) * 0.01, f'{int(m):,}', ha='center', fontsize=8)

plt.xticks([p + 0.2 for p in x], racas, rotation=45)
plt.title('População residente em favelas por cor/raça e gênero')
plt.ylabel('População')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()



#--- ------- Gráfico 2: Cor/Raça por Faixa Etária ----------
# Agrupa dados por faixa etária e soma por raça
faixas = df[df['Grupo_idade'] != 'Total']['Grupo_idade']
parda_por_idade = df[df['Grupo_idade'] != 'Total'][['Grupo_idade', 'Parda_total']]
preta_por_idade = df[df['Grupo_idade'] != 'Total'][['Grupo_idade', 'Preta_total']]
branca_por_idade = df[df['Grupo_idade'] != 'Total'][['Grupo_idade', 'Branca_total']]

plt.figure(figsize=(12, 6))
plt.plot(faixas, parda_por_idade['Parda_total'], marker='o', label='Parda')
plt.plot(faixas, preta_por_idade['Preta_total'], marker='o', label='Preta')
plt.plot(faixas, branca_por_idade['Branca_total'], marker='o', label='Branca')
plt.title('Distribuição por idade das principais cores/raças em favelas')
plt.xlabel('Grupo de Idade')
plt.ylabel('População')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

