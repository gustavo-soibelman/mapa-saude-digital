import streamlit as st
import pandas as pd


def render_tabela(df_filtrado):
    st.markdown("### Tabela de Experiências Filtradas")

    # Selecionar colunas de exibição
    colunas = [
        'ano', 'regiao', 'estado', 'cidade', 'titulo',
        'palavras_chave_saude_digital', 'palavras_chave_APS', 'autoria', 'fonte', 'link_experiencia'
    ]

    df_visivel = df_filtrado[colunas].copy()
    df_visivel = df_visivel.sort_values(by=['estado', 'cidade', 'fonte', 'ano', 'titulo'])

    # Caixa de busca opcional
    busca = st.text_input("Buscar por título, cidade ou autor (contém):")
    if busca:
        busca_lower = busca.lower()
        df_visivel = df_visivel[df_visivel.apply(
            lambda row: busca_lower in str(row['titulo']).lower()
            or busca_lower in str(row['cidade']).lower()
            or busca_lower in str(row['autoria']).lower(), axis=1
        )]

    st.dataframe(
        df_visivel,
        use_container_width=True,
        hide_index=True,
        column_config={"link_experiencia": st.column_config.LinkColumn("Link")}
    )
