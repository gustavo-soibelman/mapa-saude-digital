import pandas as pd
import streamlit as st
from io import BytesIO

@st.cache_data
def carregar_dados():
    df = pd.read_csv("dados/experiencias_selecionadas_mapa.csv")
    df = df[df["codigo_municipio"] != 0].copy()
    df['titulo'] = df['titulo'].str.upper()
    return df

@st.cache_data
def carregar_centroides():
    return pd.read_csv("dados/municipios_com_centroides.csv")

@st.cache_data
def carregar_dicionario_ufs():
    return pd.read_csv("dados/estados.csv")

@st.cache_data
def gerar_excel_para_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='dados_filtrados')
    return output.getvalue()

def carregar_dados_filtrados():
    df_trabalhos = carregar_dados()
    df_centroides = carregar_centroides()

    st.sidebar.header("\U0001F3AF FILTROS")

    # === FILTROS ===
    anos = sorted(df_trabalhos["ano"].dropna().unique())
    anos_sel = st.sidebar.multiselect("Ano", ["Todos"] + list(anos), default=["Todos"])
    if "Todos" in anos_sel:
        anos_sel = anos
    df = df_trabalhos[df_trabalhos["ano"].isin(anos_sel)]

    regioes = sorted(df["regiao"].dropna().unique())
    regioes_sel = st.sidebar.multiselect("Região", ["Todos"] + list(regioes), default=["Todos"])
    if "Todos" in regioes_sel:
        regioes_sel = regioes
    df = df[df["regiao"].isin(regioes_sel)]

    estados = sorted(df["estado"].dropna().unique())
    estados_sel = st.sidebar.multiselect("Estado", ["Todos"] + list(estados), default=["Todos"])
    if "Todos" in estados_sel:
        estados_sel = estados
    df = df[df["estado"].isin(estados_sel)]

    cidades = sorted(df["cidade"].dropna().unique())
    cidades_sel = st.sidebar.multiselect("Cidade", ["Todos"] + list(cidades), default=["Todos"])
    if "Todos" in cidades_sel:
        cidades_sel = cidades
    df = df[df["cidade"].isin(cidades_sel)]

    palavras = sorted(set(
        p.strip()
        for col in ["palavras_chave_saude_digital", "palavras_chave_APS"]
        for sublist in df_trabalhos[col].dropna().astype(str)
        for p in sublist.split(",")
    ))
    palavras_sel = st.sidebar.multiselect("Palavras-chave detectadas", ["Todos"] + palavras, default=["Todos"])
    if "Todos" not in palavras_sel:
        df = df[
            df[["palavras_chave_saude_digital", "palavras_chave_APS"]].fillna("").apply(
                lambda row: any(p in row[0] or p in row[1] for p in palavras_sel), axis=1
            )
        ]

    # Merge com centroides para mapa
    df_map = df.merge(df_centroides[['codigo_municipio', 'latitude', 'longitude']], on='codigo_municipio', how='left')
    df_map = df_map.dropna(subset=['latitude', 'longitude'])

    return df, df_map, len(df)
