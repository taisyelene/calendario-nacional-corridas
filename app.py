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

# =========================================================================
# ⚠️ COLOQUE O ID REAL DA SUA PLANILHA DO GOOGLE SHEETS AQUI:
# Exemplo de ID: "1A2B3C4D5E6F7G8H9I0J" (fica entre o /d/ e o /edit no link)
ID_DA_PLANILHA = "1A0kBTwhI5SY1Fa5DIJL5BvqK_nqHijmBSJtEOGg2qyE"
# =========================================================================


@st.cache_data(ttl=600)  # Atualiza os dados a cada 10 minutos
def carregar_dados_completos():
    # 1. Tenta carregar as corridas automáticas que o robô minerou
    if os.path.exists("corridas_automaticas.csv"):
        df_auto = pd.read_csv("corridas_automaticas.csv")
    else:
        df_auto = pd.DataFrame(
            columns=[
                "Mês",
                "Estado",
                "Data",
                "Corrida",
                "Distâncias",
                "Inscrição",
            ]
        )

    # 2. Tenta carregar as corridas manuais do Google Sheets (Modo Blindado)
    df_manual = pd.DataFrame()
    if ID_DA_PLANILHA and ID_DA_PLANILHA != "SEU_ID_DO_GOOGLE_SHEETS_AQUI":
        try:
            url_sheets = f"https://docs.google.com/spreadsheets/d/{ID_DA_PLANILHA}/export?format=csv"
            df_manual = pd.read_csv(url_sheets)

            # Validação simples para garantir que as colunas essenciais existem
            colunas_obrigatorias = ["Data", "Corrida"]
            if not all(col in df_manual.columns for col in colunas_obrigatorias):
                st.sidebar.warning(
                    "⚠️ O Google Sheets foi lido, mas as colunas parecem erradas. Use exatamente: Mês, Estado, Data, Corrida, Distâncias, Inscrição."
                )
                df_manual = pd.DataFrame()
        except Exception:
            # Se der erro no Sheets (link errado, falta de internet, privado), o app avisa e não trava!
            st.sidebar.error(
                "⚠️ Não foi possível conectar ao Google Sheets. Exibindo apenas dados do Robô."
            )
            df_manual = pd.DataFrame()

    # 3. Combina as duas bases de dados (Robô + Manual)
    if not df_auto.empty or not df_manual.empty:
        df_final = pd.concat([df_auto, df_manual], ignore_index=True)
        # Remove registros duplicados que tenham a mesma data e nome de corrida
        df_final = df_final.drop_duplicates(subset=["Data", "Corrida"])
        return df_final
    else:
        return pd.DataFrame()


# Carrega a base unificada de dados
df_comunidade = carregar_dados_completos()

# --- INTERFACE VISUAL DA BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros de Busca")

if not df_comunidade.empty:
    # Cria a lista de estados dinamicamente com base no que existe na base
    estados_disponiveis = ["Todos"] + sorted(
        list(df_comunidade["Estado"].dropna().unique())
    )
    meses_disponiveis = ["Todos"] + list(
        df_comunidade["Mês"].dropna().unique()
    )
else:
    estados_disponiveis = ["Todos"]
    meses_disponiveis = ["Todos"]

estado_sel = st.sidebar.selectbox("Filtrar por Estado (UF):", estados_disponiveis)
mes_sel = st.sidebar.selectbox("Filtrar por Mês:", meses_disponiveis)

# Aplicando os filtros escolhidos pelo usuário
df_filtrado = df_comunidade.copy()

if estado_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_sel]

if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mês"] == mes_sel]

# --- EXIBIÇÃO DA TABELA PRINCIPAL ---
st.subheader(f"📅 Calendário de Provas Disponíveis ({len(df_filtrado)})")

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
    st.info(
        "Nenhuma corrida localizada para os filtros selecionados. Altere os filtros na barra lateral!"
    )