import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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



# --- GRÁFICO 2 MELHORADO COM SEUS DADOS ---

import matplotlib.pyplot as plt

# 1. Filtrar e preparar os dados
faixas = df[df['Grupo_idade'] != 'Total']['Grupo_idade']
total_populacao = df[df['Grupo_idade'] != 'Total']['Total_geral'].fillna(0)

# 2. Configurar o gráfico
plt.figure(figsize=(10, 6))
bars = plt.bar(faixas, total_populacao, color='#1f77b4', width=0.7, alpha=0.8)

# 3. Adicionar rótulos de valor
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height):,}'.replace(',', '.'),  # Formato 1.000.000
             ha='center', va='bottom')

# 4. Customização limpa
plt.title('População em Favelas por Faixa Etária', pad=20, fontweight='bold')
plt.xlabel('Faixa Etária')
plt.ylabel('População Total')
plt.xticks(rotation=45 if len(faixas) > 3 else 0)
plt.grid(axis='y', linestyle=':', alpha=0.4)

# 5. Remover elementos desnecessários
ax = plt.gca()
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.show()


#grafico 03 é de municipios com mais favelas 
#grafico 04 é de estados com mais favelas 
