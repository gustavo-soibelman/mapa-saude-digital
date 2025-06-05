import pandas as pd
import folium
from folium import Popup
import streamlit as st
from streamlit_folium import st_folium
from io import BytesIO

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(
    page_title="MAPA DE EXPERIÊNCIAS DE SAÚDE DIGITAL CONASEMS E IDEIASUS",
    layout="wide"
)
st.title("MAPA DE EXPERIÊNCIAS DE SAÚDE DIGITAL CONASEMS E IDEIASUS")

# === CACHES DE DADOS ===
@st.cache_data
def carregar_dados():
    df = pd.read_csv("experiencias_selecionadas_mapa.csv")
    df = df[df["codigo_municipio"] != 0].copy()
    df['titulo'] = df['titulo'].str.upper()
    return df

@st.cache_data
def carregar_centroides():
    return pd.read_csv("municipios_com_centroides.csv")

df_trabalhos = carregar_dados()
df_centroides = carregar_centroides()

# === FUNÇÃO: MULTISELECT COM OPÇÃO "TODOS" ===
def atualizar_multiselect(label, opcoes, selecionados):
    todos_label = "Todos"
    opcoes_com_todos = [todos_label] + list(opcoes)

    if not selecionados:
        selecionados = [todos_label]
    elif todos_label in selecionados and len(selecionados) > 1:
        selecionados = [todos_label]
    elif todos_label not in selecionados and set(selecionados) == set(opcoes):
        selecionados = [todos_label]

    selecionados = st.sidebar.multiselect(label, options=opcoes_com_todos, default=selecionados)

    if todos_label in selecionados:
        return list(opcoes)
    else:
        return selecionados

# === FILTROS DINÂMICOS ===
st.sidebar.header("🎯 FILTROS")

anos_unicos = sorted(df_trabalhos["ano"].dropna().unique())
anos_selecionados = atualizar_multiselect("Ano", anos_unicos, ["Todos"])
df_filtrado = df_trabalhos[df_trabalhos["ano"].isin(anos_selecionados)]

regioes_unicas = sorted(df_filtrado["regiao"].dropna().unique())
regioes_selecionadas = atualizar_multiselect("Região", regioes_unicas, ["Todos"])
df_filtrado = df_filtrado[df_filtrado["regiao"].isin(regioes_selecionadas)]

estados_unicos = sorted(df_filtrado["estado"].dropna().unique())
estados_selecionados = atualizar_multiselect("Estado", estados_unicos, ["Todos"])
df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados_selecionados)]

cidades_unicas = sorted(df_filtrado["cidade"].dropna().unique())
cidades_selecionadas = atualizar_multiselect("Cidade", cidades_unicas, ["Todos"])
df_filtrado = df_filtrado[df_filtrado["cidade"].isin(cidades_selecionadas)]

# === PALAVRAS-CHAVE (combinando saúde digital + APS) ===
todas_palavras = sorted(set(
    palavra.strip()
    for col in ['palavras_chave_saude_digital', 'palavras_chave_APS']
    for sublist in df_trabalhos[col].dropna().astype(str)
    for palavra in sublist.split(",")
))
palavras_selecionadas = atualizar_multiselect("Palavras-chave detectadas", todas_palavras, ["Todos"])

if palavras_selecionadas:
    df_filtrado = df_filtrado[
        df_filtrado[["palavras_chave_saude_digital", "palavras_chave_APS"]].fillna("").apply(
            lambda row: any(p in row[0] or p in row[1] for p in palavras_selecionadas),
            axis=1
        )
    ]

# === JUNTAR COM CENTRÓIDES ===
df_map = df_filtrado.merge(
    df_centroides[['codigo_municipio', 'latitude', 'longitude']],
    on='codigo_municipio',
    how='left'
).dropna(subset=['latitude', 'longitude'])

# === CONTADOR DE RESULTADOS ===
st.markdown(f"**🔍 {len(df_filtrado)} experiências encontradas com os filtros aplicados.**")

# === BOTÃO DE DOWNLOAD COMO EXCEL ===
@st.cache_data
def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='dados_filtrados')
    return output.getvalue()

excel_bytes = gerar_excel(df_filtrado)

st.download_button(
    label="📥 Baixar dados filtrados (.xlsx)",
    data=excel_bytes,
    file_name="experiencias_filtradas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# === MAPA COM FOLIUM ===
m = folium.Map(location=[-15, -55], zoom_start=4, tiles='cartodbpositron')

grouped = df_map.groupby("codigo_municipio")

for codigo, group in grouped:
    info = group.iloc[0]
    municipio_nome = info['cidade']
    estado = info['estado']
    regiao = info['regiao']
    latitude = info['latitude']
    longitude = info['longitude']

    links_html = ""
    for _, row in group.iterrows():
        titulo = row['titulo']
        link = row['link_experiencia']
        palavras = (
            str(row.get('palavras_chave_saude_digital', '')) + " | " +
            str(row.get('palavras_chave_APS', ''))
        )
        links_html += f"""
        <tr>
            <td><a href="{link}" target="_blank">{titulo}</a></td>
            <td>{palavras}</td>
        </tr>
        """

    popup_html = f"""
    <b>{municipio_nome.upper()}/{estado.upper()}</b><br>
    <b>REGIÃO:</b> {regiao.upper()}<br>
    <b>EXPERIÊNCIAS:</b> {len(group)}<br><br>
    <table border="1" style="font-size:10px;">
        <tr><th>TÍTULO</th><th>PALAVRAS-CHAVE</th></tr>
        {links_html}
    </table>
    """

    folium.CircleMarker(
        location=[latitude, longitude],
        radius=3 + len(group) ** 0.5,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=Popup(popup_html, max_width=600),
        tooltip=f"{municipio_nome.upper()}/{estado.upper()} ({len(group)} PUBLICAÇÕES)"
    ).add_to(m)

st_folium(m, width=1200, height=700)
