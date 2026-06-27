# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:08:07 2026

@author: peque
"""
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Portal da Comunidade - Corridas de Rua",
    page_icon="🏃‍♂️",
    layout="wide",
)

st.title("🏃‍♂️ Calendário Nacional de Corridas de Rua")
st.markdown("O buscador inteligente alimentado por robôs e pela comunidade.")


# Função inteligente que une o Manual + Automático
@st.cache_data
def carregar_todos_os_dados():
    # 1. Carrega os dados do robô (se o arquivo existir)
    if os.path.exists("corridas_automaticas.csv"):
        df_auto = pd.read_csv("corridas_automaticas.csv")
    else:
        df_auto = pd.DataFrame()

    # 2. Carrega os seus dados manuais (se o arquivo existir)
    if os.path.exists("corridas_manuais.csv"):
        df_manual = pd.read_csv("corridas_manuais.csv")
    else:
        # Se não existir, cria o modelo vazio para você preencher depois
        df_manual = pd.DataFrame(
            columns=[
                "Mês",
                "Estado",
                "Data",
                "Corrida",
                "Distâncias",
                "Inscrição",
            ]
        )
        df_manual.to_csv("corridas_manuais.csv", index=False)

    # 3. Junta as duas planilhas em uma só
    df_final = pd.concat([df_auto, df_manual], ignore_index=True)

    # Remove possíveis corridas duplicadas idênticas
    df_final = df_final.drop_duplicates(subset=["Data", "Corrida"])
    return df_final


df_comunidade = carregar_todos_os_dados()

# --- INTERFACE DE FILTROS ---
st.sidebar.header("🔍 Filtros de Busca")
estado_sel = st.sidebar.selectbox(
    "Estado", ["Todos"] + sorted(list(df_comunidade["Estado"].unique()))
)
mes_sel = st.sidebar.selectbox(
    "Mês",
    [
        "Todos",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ],
)
distancia_sel = st.sidebar.text_input("Distância (Ex: 21k, 42k)", "")

# Aplicando os filtros
df_filtrado = df_comunidade.copy()
if estado_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_sel]
if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mês"] == mes_sel]
if distancia_sel:
    df_filtrado = df_filtrado[
        df_filtrado["Distâncias"].str.contains(distancia_sel, case=False)
    ]

# Exibição dos dados
st.subheader(f"📅 Provas Disponíveis ({len(df_filtrado)})")
if not df_filtrado.empty:
    st.dataframe(
        df_filtrado,
        column_config={
            "Mês": st.column_config.TextColumn("Mês 🗓️"),
            "Estado": st.column_config.TextColumn("UF 📍"),
            "Data": st.column_config.TextColumn("Data 📅"),
            "Corrida": st.column_config.TextColumn("Nome do Evento 👟"),
            "Distâncias": st.column_config.TextColumn("Distâncias 🗺️"),
            "Inscrição": st.column_config.LinkColumn(
                "Inscrição 🔗", display_text="Ver Inscrição"
            ),
        },
        hide_index=True,
        use_container_width=True,
    )
else:
    st.warning("Nenhuma corrida encontrada.")