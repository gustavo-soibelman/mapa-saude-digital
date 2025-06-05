import streamlit as st
from utils import carregar_dados_filtrados, gerar_excel_para_download
from mapas.bubble_map import render_bubble_map
from mapas.choropleth_uf import render_choropleth_uf
from mapas.choropleth_regiao import render_choropleth_regiao
from mapas.tabela import render_tabela

st.set_page_config(
    page_title="MAPA DE EXPERIÊNCIAS DE SAÚDE DIGITAL CONASEMS E IDEIASUS",
    layout="wide"
)

st.title("MAPA DE EXPERIÊNCIAS DE SAÚDE DIGITAL CONASEMS E IDEIASUS")

# === Carregar dados filtrados ===
df_filtrado, df_map, total_experiencias = carregar_dados_filtrados()

# === Contador de resultados ===
st.markdown(f"**🔍 {total_experiencias} experiências encontradas com os filtros aplicados.**")

# === Tabs de visualização ===
tabs = st.tabs([
    "Mapa por Município (Bubbles)",
    "Choropleth por UF",
    "Choropleth por Região",
    "Tabela de Experiências"
])

with tabs[0]:
    render_bubble_map(df_map)

with tabs[1]:
    render_choropleth_uf(df_filtrado)

with tabs[2]:
    render_choropleth_regiao(df_filtrado)

with tabs[3]:
    render_tabela(df_filtrado)

# === Botão de download ===
st.download_button(
    label="📅 Baixar dados filtrados (.xlsx)",
    data=gerar_excel_para_download(df_filtrado),
    file_name="experiencias_filtradas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
