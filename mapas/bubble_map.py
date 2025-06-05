import folium
import os
import json
from folium import Popup
from streamlit_folium import st_folium


def render_bubble_map(df_map):
    m = folium.Map(location=[-15, -55], zoom_start=4, tiles='cartodbpositron')

    # === Adicionar bordas dos estados ===
    estados_presentes = df_map['estado'].dropna().unique().tolist()
    for uf in estados_presentes:
        geo_path = f"dados/estados/{uf}.geojson"
        if os.path.exists(geo_path):
            with open(geo_path, encoding='utf-8') as f:
                geo = json.load(f)
                folium.GeoJson(
                    geo,
                    name=f"Borda {uf}",
                    style_function=lambda x: {
                        'fillOpacity': 0,
                        'color': 'black',
                        'weight': 1
                    }
                ).add_to(m)

    # === Agrupar por município ===
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
                <td><a href=\"{link}\" target=\"_blank\">{titulo}</a></td>
                <td>{palavras}</td>
            </tr>
            """

        popup_html = f"""
        <b>{municipio_nome.upper()}/{estado.upper()}</b><br>
        <b>REGIÃO:</b> {regiao.upper()}<br>
        <b>EXPERIÊNCIAS:</b> {len(group)}<br><br>
        <table border=\"1\" style=\"font-size:10px;\">
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