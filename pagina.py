import pandas as pd
import requests
import folium
from folium import Popup
import streamlit as st
from streamlit_folium import st_folium

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(
    page_title="MAPA DE EXPERIÊNCIAS DE SAÚDE DIGITAL CONASEMS E IDEIASUS",
    layout="wide"
)
st.title("MAPA DE EXPERIÊNCIAS DE SAÚDE DIGITAL CONASEMS E IDEIASUS")

# === CACHE DA LEITURA DO ARQUIVO ===
@st.cache_data
def carregar_dados():
    arquivo_excel = "experiencias_completas_conasems_ideiasus_2025.xlsx"
    df_original = pd.read_excel(arquivo_excel, sheet_name="experiencias_selecionadas_mapa")
    df = df_original[df_original["codigo_municipio"] != 0].copy()
    df['titulo'] = df['titulo'].str.upper()
    return df

df_trabalhos = carregar_dados()

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

palavras_unicas = sorted(set(
    palavra.strip()
    for sublist in df_trabalhos["palavras_chave_detectadas"].dropna().astype(str)
    for palavra in sublist.split(",")
))
palavras_selecionadas = atualizar_multiselect("Palavras-chave detectadas", palavras_unicas, ["Todos"])

if palavras_selecionadas:
    df_filtrado = df_filtrado[
        df_filtrado["palavras_chave_detectadas"].fillna("").apply(
            lambda x: any(p in x for p in palavras_selecionadas)
        )
    ]

# === CACHE DOS CENTRÓIDES E POPUPS ===
@st.cache_data
def gerar_municipios_info(df):
    info = {}
    grouped = df.groupby("codigo_municipio")

    for codigo, group in grouped:
        municipio_nome = group.iloc[0]['cidade']
        estado = group.iloc[0]['estado']
        regiao = group.iloc[0]['regiao']

        url_meta = f"https://servicodados.ibge.gov.br/api/v4/malhas/municipios/{codigo}/metadados"
        try:
            response = requests.get(url_meta)
            data = response.json()
            centroide = data[0]['centroide']
            latitude = centroide['latitude']
            longitude = centroide['longitude']
        except:
            print(f"Erro ao buscar dados de {codigo}")
            continue

        links_html = ""
        for _, row in group.iterrows():
            titulo = row['titulo']
            link = row['link_experiencia']
            palavras = row.get('palavras_chave_detectadas', '')
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

        info[codigo] = {
            "nome": municipio_nome,
            "estado": estado,
            "regiao": regiao,
            "count": len(group),
            "latitude": latitude,
            "longitude": longitude,
            "popup": popup_html
        }

    return info

municipios_info = gerar_municipios_info(df_filtrado)

# === MAPA COM FOLIUM ===
m = folium.Map(location=[-15, -55], zoom_start=4, tiles='cartodbpositron')

for info in municipios_info.values():
    folium.CircleMarker(
        location=[info['latitude'], info['longitude']],
        radius=3 + info['count'] ** 0.5,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=Popup(info['popup'], max_width=600),
        tooltip=f"{info['nome'].upper()}/{info['estado'].upper()} ({info['count']} PUBLICAÇÕES)"
    ).add_to(m)

# === EXIBIR O MAPA ===
st_folium(m, width=1200, height=700)
