import streamlit as st
import folium
import os
import json
import pandas as pd
from folium import CircleMarker, Popup
from streamlit_folium import st_folium
from utils import carregar_dicionario_ufs

@st.cache_data
def carregar_geojson_regiao(regiao):
    path = f"dados/regioes/{regiao}.geojson"
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return None

def render_choropleth_regiao(df_filtrado):
    m = folium.Map(location=[-15, -55], zoom_start=4, tiles=None)

    df_ufs = carregar_dicionario_ufs()[['regiao']].drop_duplicates()
    df_regiao_count = df_filtrado.groupby("regiao").size().reset_index(name="num_experiencias")

    df_choropleth = pd.merge(df_ufs, df_regiao_count, on="regiao", how="left")
    df_choropleth["num_experiencias"] = df_choropleth["num_experiencias"].fillna(0).astype(int)

    for _, row in df_choropleth.iterrows():
        regiao = row['regiao']
        count = row['num_experiencias']
        geo = carregar_geojson_regiao(regiao)
        if not geo:
            continue

        experiencias_r = df_filtrado[df_filtrado['regiao'] == regiao]
        linhas = ""
        for _, r in experiencias_r.iterrows():
            titulo = r['titulo']
            link = r['link_experiencia']
            palavras = f"{r.get('palavras_chave_saude_digital', '')} | {r.get('palavras_chave_APS', '')}"
            linhas += f"<tr><td><a href='{link}' target='_blank'>{titulo}</a></td><td>{palavras}</td></tr>"

        popup_html = f"""
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
            name=f"{regiao}",
            style_function=lambda feat, c=count: {
                'fillColor': get_color(c),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6 if c > 0 else 0.1
            },
            tooltip=folium.Tooltip(f"{regiao}: {count} experiências"),
            popup=Popup(popup_html, max_width=600)
        ).add_to(m)

    if 'latitude' in df_filtrado.columns and 'longitude' in df_filtrado.columns:
        for _, row in df_filtrado.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=1.5,
                color='blue',
                fill=True,
                fill_opacity=0.4
            ).add_to(m)

    legend_html = """
     <div style=\"position: fixed; 
                 bottom: 40px; left: 40px; width: 220px; height: 160px; 
                 background-color: white; border:2px solid grey; z-index:9999; font-size:14px;\">
     &nbsp;<b>Experiências por Região</b><br>
     &nbsp;<i style=\"background:#08306b;width:12px;height:12px;display:inline-block;\"></i>&nbsp; >100<br>
     &nbsp;<i style=\"background:#2171b5;width:12px;height:12px;display:inline-block;\"></i>&nbsp; 51-100<br>
     &nbsp;<i style=\"background:#6baed6;width:12px;height:12px;display:inline-block;\"></i>&nbsp; 11-50<br>
     &nbsp;<i style=\"background:#c6dbef;width:12px;height:12px;display:inline-block;\"></i>&nbsp; 1-10<br>
     &nbsp;<i style=\"background:#f0f0f0;width:12px;height:12px;display:inline-block;\"></i>&nbsp; 0<br>
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
