import streamlit as st
import folium
import os
import json
import pandas as pd
from folium import Choropleth, CircleMarker, Popup
from streamlit_folium import st_folium
from utils import carregar_dicionario_ufs

@st.cache_data
def carregar_geojson_uf(uf):
    path = f"dados/estados/{uf}.geojson"
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return None

def render_choropleth_uf(df_filtrado):
    m = folium.Map(location=[-15, -55], zoom_start=4, tiles=None)  # sem tiles para melhorar desempenho

    df_ufs = carregar_dicionario_ufs()[['UF', 'regiao', 'codigo_uf']]
    df_estado_count = df_filtrado.groupby("estado").size().reset_index(name="num_experiencias")

    df_choropleth = pd.merge(df_ufs, df_estado_count, left_on="UF", right_on="estado", how="left")
    df_choropleth["num_experiencias"] = df_choropleth["num_experiencias"].fillna(0).astype(int)

    for _, row in df_choropleth.iterrows():
        uf = row['UF']
        count = row['num_experiencias']
        regiao = row['regiao']
        geo = carregar_geojson_uf(uf)
        if not geo:
            continue

        # Subconjunto das experiências da UF
        experiencias_uf = df_filtrado[df_filtrado['estado'] == uf]
        linhas = ""
        for _, r in experiencias_uf.iterrows():
            titulo = r['titulo']
            link = r['link_experiencia']
            palavras = f"{r.get('palavras_chave_saude_digital', '')} | {r.get('palavras_chave_APS', '')}"
            linhas += f"<tr><td><a href='{link}' target='_blank'>{titulo}</a></td><td>{palavras}</td></tr>"

        popup_html = f"""
        <b>UF:</b> {uf}<br>
        <b>REGIÃO:</b> {regiao}<br>
        <b>EXPERIÊNCIAS:</b> {count}<br><br>
        <div style='max-height:300px;overflow-y:auto'>
        <table border='1' style='font-size:10px;'>
        <tr><th>TÍTULO</th><th>PALAVRAS-CHAVE</th></tr>
        {linhas}
        </table>
        </div>
        """

        folium.GeoJson(
            geo,
            name=f"{uf}",
            style_function=lambda feat, c=count: {
                'fillColor': get_color(c),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6 if c > 0 else 0.1
            },
            tooltip=folium.Tooltip(f"{uf}: {count} experiências"),
            popup=Popup(popup_html, max_width=600)
        ).add_to(m)

    # Adicionar marcadores discretos
    if 'latitude' in df_filtrado.columns and 'longitude' in df_filtrado.columns:
        for _, row in df_filtrado.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=1.5,
                color='blue',
                fill=True,
                fill_opacity=0.4
            ).add_to(m)

    # Legenda
    legend_html = """
     <div style="position: fixed; 
                 bottom: 40px; left: 40px; width: 200px; height: 160px; 
                 background-color: white; border:2px solid grey; z-index:9999; font-size:14px;">
     &nbsp;<b>Experiências por UF</b><br>
     &nbsp;<i style="background:#08306b;width:12px;height:12px;display:inline-block;"></i>&nbsp; >100<br>
     &nbsp;<i style="background:#2171b5;width:12px;height:12px;display:inline-block;"></i>&nbsp; 51-100<br>
     &nbsp;<i style="background:#6baed6;width:12px;height:12px;display:inline-block;"></i>&nbsp; 11-50<br>
     &nbsp;<i style="background:#c6dbef;width:12px;height:12px;display:inline-block;"></i>&nbsp; 1-10<br>
     &nbsp;<i style="background:#f0f0f0;width:12px;height:12px;display:inline-block;"></i>&nbsp; 0<br>
      </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=1200, height=700)

def get_color(value):
    if value > 100:
        return '#08306b'
    elif value > 50:
        return '#2171b5'
    elif value > 10:
        return '#6baed6'
    elif value > 0:
        return '#c6dbef'
    else:
        return '#f0f0f0'