# Análise do crescimento da população em favelas e sua relação com a raça

import pandas as pd
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
import numpy as np
from scipy.stats import pearsonr


# -------------------------
# Etapa 1: Carregar dados populacionais de favelas (2010 e 2022)
# -------------------------
pop_favela_2010 = pd.read_csv("C:\\Users\\Cecília Barbosa\\Documents\\000000_dados\\ciencia-dados-\\meta_dados\\pop_favela_uf_2010.csv", sep=";", skiprows=5, names=["UF", "Populacao_Favela_2010"])
pop_favela_2010["UF"] = pop_favela_2010["UF"].str.replace('"', '').str.strip()
pop_favela_2010 = pop_favela_2010[pop_favela_2010["UF"] != "Brasil"]
# Limpar caracteres não numéricos e remover vazios antes de converter
pop_favela_2010["Populacao_Favela_2010"] = (
    pop_favela_2010["Populacao_Favela_2010"]
    .astype(str)
    .str.replace(r"[^\d]", "", regex=True)
)

# Remover linhas onde a coluna está vazia depois da limpeza
pop_favela_2010 = pop_favela_2010[pop_favela_2010["Populacao_Favela_2010"] != ""]

# Converter para inteiro com segurança
pop_favela_2010["Populacao_Favela_2010"] = pop_favela_2010["Populacao_Favela_2010"].astype(int)


pop_favela_2022 = pd.read_csv(r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\favela_popu_por_uf.csv", sep=";", skiprows=6, names=["UF", "Grupo_Idade", "Populacao_Favela_2022"])
pop_favela_2022 = pop_favela_2022[pop_favela_2022["Grupo_Idade"] == "Total"]
pop_favela_2022["UF"] = pop_favela_2022["UF"].str.strip()
pop_favela_2022["Populacao_Favela_2022"] = pop_favela_2022["Populacao_Favela_2022"].astype(str).str.replace(r"[^\d]", "", regex=True).astype(int)

# Padronizar UFs
padronizar = lambda s: s.str.upper().apply(lambda x: unicodedata.normalize("NFKD", x).encode("ASCII", "ignore").decode("utf-8").strip())
pop_favela_2010["UF"] = padronizar(pop_favela_2010["UF"])
pop_favela_2022["UF"] = padronizar(pop_favela_2022["UF"])

# Merge e cálculo do crescimento
df = pd.merge(pop_favela_2010, pop_favela_2022[["UF", "Populacao_Favela_2022"]], on="UF", how="inner")
df["Crescimento_Pop_Favela_%"] = ((df["Populacao_Favela_2022"] - df["Populacao_Favela_2010"]) / df["Populacao_Favela_2010"]) * 100

# -------------------------
# Etapa 2: Carregar dados de raça por UF (IBGE)
# -------------------------
df_raca_raw = pd.read_excel(r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\brasil_populacao_por_uf.xlsx", skiprows=5)

df_raca = df_raca_raw.rename(columns={
    "Unnamed: 0": "UF",
    "Total": "Pop_Total",
    "Unnamed: 5": "Preta",
    "Unnamed: 7": "Parda"
})
df_raca = df_raca[["UF", "Pop_Total", "Preta", "Parda"]].dropna()
df_raca = df_raca[~df_raca["UF"].str.contains("BRASIL", case=False)]

for col in ["Pop_Total", "Preta", "Parda"]:
    df_raca[col] = df_raca[col].astype(str).str.replace(r"[^\d]", "", regex=True).astype(float)

df_raca["Perc_Preto_Pardo"] = ((df_raca["Preta"] + df_raca["Parda"]) / df_raca["Pop_Total"]) * 100
df_raca["UF"] = padronizar(df_raca["UF"])

# -------------------------
# Etapa 3: Unir as bases e realizar análise estatística
# -------------------------
df_final = pd.merge(df, df_raca[["UF", "Perc_Preto_Pardo"]], on="UF", how="left")
df_clean = df_final.dropna(subset=["Crescimento_Pop_Favela_%", "Perc_Preto_Pardo"])

# Correlação de Pearson
r, p_corr = stats.pearsonr(df_clean["Crescimento_Pop_Favela_%"], df_clean["Perc_Preto_Pardo"])

# Teste t de grupos
mediana_pp = df_clean["Perc_Preto_Pardo"].median()
grupo_alto = df_clean[df_clean["Perc_Preto_Pardo"] >= mediana_pp]["Crescimento_Pop_Favela_%"]
grupo_baixo = df_clean[df_clean["Perc_Preto_Pardo"] < mediana_pp]["Crescimento_Pop_Favela_%"]
t_stat, p_tteste = stats.ttest_ind(grupo_alto, grupo_baixo, equal_var=False)

# Regressão Linear Simples
X = sm.add_constant(df_clean["Perc_Preto_Pardo"])
y = df_clean["Crescimento_Pop_Favela_%"]
modelo = sm.OLS(y, X).fit()

# Gráfico
plt.figure(figsize=(10, 6))
sns.regplot(x="Perc_Preto_Pardo", y="Crescimento_Pop_Favela_%", data=df_clean)
plt.title("Regressão Linear: Crescimento de Favelas vs. % Pretos/Pardos")
plt.xlabel("% Pretos ou Pardos (2022)")
plt.ylabel("Crescimento da População em Favelas (2010–2022)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Resumo dos resultados
print("Correlação de Pearson:", round(r, 4), "(p =", round(p_corr, 4), ")")
print("P-valor do teste t entre grupos (alto vs. baixo % pretos/pardos):", round(p_tteste, 4))
print("\nResumo da Regressão Linear:\n")
print(modelo.summary())


#-------- 2 escolaridade -------------


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