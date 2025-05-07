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

# 1. Filtrar dados válidos (remover faixas com valor zero)
dados_filtrados = df[(df['Grupo_idade'] != 'Total') & (df['Total_geral'] > 0)]
faixas = dados_filtrados['Grupo_idade']
valores = dados_filtrados['Total_geral']

# 2. Configuração do gráfico ultra-limp
fig, ax = plt.subplots(figsize=(10, 5))  # Mais compacto

# 3. Barras com estilo minimalista
bars = ax.bar(faixas, valores, 
             color='#2c7bb6', 
             width=0.6,
             edgecolor='white',
             linewidth=0.5)

# 4. Adicionar valores formatados
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height * 1.02,
           f'{int(height):,}'.replace(',', '.'),
           ha='center', va='bottom',
           fontsize=9)

# 5. Customização profissional
ax.set_title('Distribuição por Faixa Etária - População em Favelas', 
            pad=15, fontsize=12, fontweight='bold')
ax.set_xlabel('Faixa Etária', labelpad=8)
ax.set_ylabel('População Total', labelpad=8)
ax.set_xticks(range(len(faixas)))
ax.set_xticklabels(faixas, rotation=45 if len(faixas) > 3 else 0)

# 6. Limpeza radical
ax.spines[['right', 'top', 'left']].set_visible(False)  # Remove todas as bordas
ax.yaxis.grid(True, linestyle=':', alpha=0.3)  # Grade horizontal muito sutil
ax.tick_params(axis='both', which='both', length=0)  # Remove marcadores

# 7. Ajuste preciso do layout
plt.tight_layout(pad=1.5)
plt.show()

#grafico 03 é de municipios com mais favelas 
#grafico 04 é de estados com mais favelas 
