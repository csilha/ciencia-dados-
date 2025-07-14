#-------- 2 escolaridade -------------
import pandas as pd
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
import numpy as np
from scipy.stats import pearsonr 

def normalizar_estado(estado):
    return unicodedata.normalize('NFKD', estado.strip()).encode('ASCII', 'ignore').decode('utf-8').upper()

# Caminho do seu arquivo
file_path = r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\escolaridade_br_22.xlsx"

# Carregar planilha sem cabeçalho
df_raw = pd.read_excel(file_path, header=None)

# A partir da linha 4 estão os dados reais (índice 4 = linha 5 no Excel)
df_dados = df_raw.iloc[4:].copy()

# Coluna 0: estado
df_dados.rename(columns={0: "UF"}, inplace=True)
df_dados = df_dados[df_dados["UF"].notna()]
df_dados["UF"] = df_dados["UF"].astype(str).apply(normalizar_estado)
df_dados = df_dados[~df_dados["UF"].str.contains("BRASIL|FONTE", case=False)]

# Selecionar colunas exatas: manualmente definidas com base na estrutura da planilha
# Exemplo:
# N = índice 13
# Z = índice 25
# AJ = índice 35
# AT = índice 45

df_escolaridade = pd.DataFrame()
df_escolaridade["UF"] = df_dados["UF"]

# Conversão de strings para inteiros
def limpar_valor(x):
    return pd.to_numeric(str(x).replace(".", "").replace(",", "").strip(), errors="coerce")

df_escolaridade["Sem instrução e fundamental incompleto"] = df_dados[13].apply(limpar_valor)
df_escolaridade["Fundamental completo e médio incompleto"] = df_dados[25].apply(limpar_valor)
df_escolaridade["Médio completo e superior incompleto"] = df_dados[35].apply(limpar_valor)
df_escolaridade["Superior completo"] = df_dados[45].apply(limpar_valor)


# Plotar gráfico
plt.figure(figsize=(14, 8))
df_escolaridade.set_index("UF").plot(
    kind="bar", stacked=True, figsize=(14, 8), colormap="tab10"
)
plt.title("Distribuição da Escolaridade por Estado (2022)")
plt.ylabel("População")
plt.xlabel("Estado")
plt.xticks(rotation=45, ha='right')
plt.legend(title="Nível de Escolaridade")
plt.tight_layout()
plt.grid(axis='y')
plt.show()

#------ 2.1 correlação pop_favela e baixa escolaridade 

# Função para normalizar nomes de estados
def normalizar_estado(estado):
    if isinstance(estado, str):
        estado = unicodedata.normalize('NFKD', estado).encode('ASCII', 'ignore').decode('utf-8').strip()
        return estado.lower()
    return estado

# Carregar dados
escolaridade_df = pd.read_excel(r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\escolaridade_br_22_idade.xlsx")
favelas_df = pd.read_csv(r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\favela_popu_por_uf.csv")

# === Renomear coluna com nome longo para 'estado' no favelas_df ===
favelas_df.rename(columns={favelas_df.columns[0]: 'estado'}, inplace=True)

# === Filtrar somente linhas válidas que contêm dados de estados ===
filtros_validos = favelas_df['estado'].str.contains(';Total;', na=False)
favelas_df = favelas_df[filtros_validos].copy()

# === Separar nome do estado e população ===
favelas_df[['estado_nome', 'tag', 'pop_favela']] = favelas_df['estado'].str.split(';', expand=True)

# === Converter população para inteiro ===
favelas_df['pop_favela'] = pd.to_numeric(favelas_df['pop_favela'], errors='coerce')

# === Normalizar nomes dos estados ===
favelas_df['estado'] = favelas_df['estado_nome'].apply(normalizar_estado)
escolaridade_df['estado'] = escolaridade_df['Unnamed: 0'].apply(normalizar_estado)

# === Merge dos dois DataFrames ===
df_merge = pd.merge(escolaridade_df, favelas_df[['estado', 'pop_favela']], on='estado', how='inner')

# === Verificar resultado do merge ===
if df_merge.shape[0] < 10:
    print("⚠️ Merge falhou ou retornou poucos dados.")
    print("Estados no escolaridade_df que não casaram:", set(escolaridade_df['estado']) - set(favelas_df['estado']))
    print("Estados no favelas_df que não casaram:", set(favelas_df['estado']) - set(escolaridade_df['estado']))

# Calcular correlação
correlacao, p_valor = pearsonr(df_merge['baixa'], df_merge['pop_favela'])

# Criar gráfico com Seaborn
plt.figure(figsize=(10, 6))
sns.set(style='whitegrid')

sns.regplot(
    x='baixa',
    y='pop_favela',
    data=df_merge,
    color='orange',
    line_kws={'color': 'red'},
    scatter_kws={'s': 50},
)

# Título com correlação
plt.title(f'Correlação Entre Baixa Escolaridade E População Em Favelas\n'
          f'Coef. de correlação: {correlacao:.2f}, p-valor: {p_valor:.4f}',
          fontsize=12)
plt.xlabel('População com Baixa Escolaridade')
plt.ylabel('População em Favelas')
plt.tight_layout()
plt.show()

# --- 2.2 Regressão Linear: Baixa Escolaridade vs. População em Favelas ---

# Preparar as variáveis para o modelo
X = sm.add_constant(df_merge['baixa'])  # Variável independente com constante
y = df_merge['pop_favela']              # Variável dependente

# Ajustar o modelo OLS
modelo = sm.OLS(y, X).fit()

# Imprimir resumo completo da regressão
print("\nResumo da Regressão Linear entre baixa escolaridade e população em favelas:\n")
print(modelo.summary())
