# Correlação entre população em favelas (2022) e % de pretos/pardos por UF

import pandas as pd
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
import numpy as np

# -------------------------
# Etapa 1: Carregar dados populacionais de favelas 2022
# -------------------------
pop_favela_2022 = pd.read_csv(
    r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\favela_popu_por_uf.csv",
    sep=";", skiprows=6, names=["UF", "Grupo_Idade", "Populacao_Favela_2022"]
)
pop_favela_2022 = pop_favela_2022[pop_favela_2022["Grupo_Idade"] == "Total"]
pop_favela_2022["UF"] = pop_favela_2022["UF"].str.strip()
pop_favela_2022["Populacao_Favela_2022"] = (
    pop_favela_2022["Populacao_Favela_2022"]
    .astype(str)
    .str.replace(r"[^\d]", "", regex=True)
    .astype(int)
)

# Padronizar UFs
padronizar = lambda s: s.str.upper().apply(
    lambda x: unicodedata.normalize("NFKD", x)
    .encode("ASCII", "ignore")
    .decode("utf-8")
    .strip()
)
pop_favela_2022["UF"] = padronizar(pop_favela_2022["UF"])

# -------------------------
# Etapa 2: Carregar dados de raça por UF (IBGE)
# -------------------------
df_raca_raw = pd.read_excel(
    r"C:\Users\Cecília Barbosa\Documents\000000_dados\ciencia-dados-\meta_dados\brasil_populacao_por_uf.xlsx",
    skiprows=5
)

df_raca = df_raca_raw.rename(columns={
    "Unnamed: 0": "UF",
    "Total": "Pop_Total",
    "Unnamed: 5": "Preta",
    "Unnamed: 7": "Parda"
})
df_raca = df_raca[["UF", "Pop_Total", "Preta", "Parda"]].dropna()
df_raca = df_raca[~df_raca["UF"].str.contains("BRASIL", case=False)]

for col in ["Pop_Total", "Preta", "Parda"]:
    df_raca[col] = (
        df_raca[col]
        .astype(str)
        .str.replace(r"[^\d]", "", regex=True)
        .astype(float)
    )

df_raca["Perc_Preto_Pardo"] = ((df_raca["Preta"] + df_raca["Parda"]) / df_raca["Pop_Total"]) * 100
df_raca["UF"] = padronizar(df_raca["UF"])

# -------------------------
# Etapa 3: Unir as bases e realizar análise estatística
# -------------------------
df_final = pd.merge(pop_favela_2022[["UF", "Populacao_Favela_2022"]], df_raca[["UF", "Perc_Preto_Pardo"]], on="UF", how="inner")
df_clean = df_final.dropna()

# Correlação de Pearson
r, p_corr = stats.pearsonr(df_clean["Populacao_Favela_2022"], df_clean["Perc_Preto_Pardo"])

# Regressão Linear
X = sm.add_constant(df_clean["Perc_Preto_Pardo"])
y = df_clean["Populacao_Favela_2022"]
modelo = sm.OLS(y, X).fit()

# Gráfico
plt.figure(figsize=(10, 6))
sns.regplot(x="Perc_Preto_Pardo", y="Populacao_Favela_2022", data=df_clean, scatter_kws={"s": 50}, line_kws={"color": "blue"})
plt.title("Regressão Linear: População em Favelas vs. % Pretos/Pardos")
plt.xlabel("% Pretos ou Pardos (2022)")
plt.ylabel("População em Favelas (2022)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Resumo dos resultados
print("Correlação de Pearson:", round(r, 4), "(p =", round(p_corr, 4), ")")
print("\nResumo da Regressão Linear:\n")
print(modelo.summary())

# -------------------------
# Etapa adicional: Correlação entre população preta+parda (absoluta) e população em favelas (2022)
# -------------------------

# Unir dados populacionais de favelas com totais absolutos de pretos+pardos
df_raca["Total_Preto_Pardo"] = df_raca["Preta"] + df_raca["Parda"]

df_absoluto = pd.merge(
    pop_favela_2022[["UF", "Populacao_Favela_2022"]],
    df_raca[["UF", "Total_Preto_Pardo"]],
    on="UF",
    how="inner"
)

# Correlação de Pearson
r_abs, p_abs = stats.pearsonr(df_absoluto["Total_Preto_Pardo"], df_absoluto["Populacao_Favela_2022"])

# Regressão Linear
X_abs = sm.add_constant(df_absoluto["Total_Preto_Pardo"])
y_abs = df_absoluto["Populacao_Favela_2022"]
modelo_abs = sm.OLS(y_abs, X_abs).fit()

# Gráfico
plt.figure(figsize=(10, 6))
sns.regplot(
    x="Total_Preto_Pardo",
    y="Populacao_Favela_2022",
    data=df_absoluto,
    scatter_kws={'color': 'orange'},
    line_kws={'color': 'red'}
)
plt.title("Correlação: População em Favelas vs. População Preta+Parda")
plt.xlabel("População Preta + Parda (absoluto)")
plt.ylabel("População em Favelas (2022)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Resultado
print("Correlação de Pearson (valores absolutos):", round(r_abs, 4), "(p =", round(p_abs, 4), ")")
print("\nResumo da Regressão Linear com valores absolutos:\n")
print(modelo_abs.summary())


