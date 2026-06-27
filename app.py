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
ID_DA_PLANILHA = "1A0kBTwhI5SY1Fa5DIJL5BvqK_nqHijmBSJtEOGg2qyE"
# =========================================================================

@st.cache_data(ttl=600)  # Atualiza os dados a cada 10 minutos
def carregar_dados_completos():
    if os.path.exists("corridas_automaticas.csv"):
        df_auto = pd.read_csv("corridas_automaticas.csv")
    else:
        df_auto = pd.DataFrame(columns=["Mês", "Estado", "Data", "Corrida", "Distâncias", "Inscrição"])

    df_manual = pd.DataFrame()
    if ID_DA_PLANILHA and ID_DA_PLANILHA != "SEU_ID_DO_GOOGLE_SHEETS_AQUI":
        try:
            url_sheets = f"https://docs.google.com/spreadsheets/d/{ID_DA_PLANILHA}/export?format=csv"
            df_manual = pd.read_csv(url_sheets)
            colunas_obrigatorias = ["Data", "Corrida"]
            if not all(col in df_manual.columns for col in colunas_obrigatorias):
                st.sidebar.warning("⚠️ O Google Sheets foi lido, mas as colunas parecem erradas.")
                df_manual = pd.DataFrame()
        except Exception:
            st.sidebar.error("⚠️ Não foi possível conectar ao Google Sheets. Exibindo apenas dados do Robô.")
            df_manual = pd.DataFrame()

    if not df_auto.empty or not df_manual.empty:
        df_final = pd.concat([df_auto, df_manual], ignore_index=True)
        df_final = df_final.drop_duplicates(subset=["Data", "Corrida"])
        return df_final
    else:
        return pd.DataFrame()

df_comunidade = carregar_dados_completos()

# --- INTERFACE VISUAL DA BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros de Busca")

if not df_comunidade.empty:
    estados_disponiveis = ["Todos"] + sorted(list(df_comunidade["Estado"].dropna().unique()))
    meses_disponiveis = ["Todos"] + list(df_comunidade["Mês"].dropna().unique())
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


# --- BLOCO DE MÉTRICAS NO TOPO ---
st.markdown("---") # Linha divisória sutil

# Criando 3 colunas lado a lado para os cartões
col1, col2, col3 = st.columns(3)

if not df_filtrado.empty:
    # 1. Total de Provas
    total_provas = len(df_filtrado)
    
    # 2. Total de Estados Únicos
    total_estados = df_filtrado["Estado"].nunique()
    
    # 3. Próxima Corrida (Tenta identificar a data mais próxima)
    try:
        # Converte a coluna Data temporariamente para ordenar de verdade
        df_ordenado = df_filtrado.copy()
        df_ordenado["Data_Parsed"] = pd.to_datetime(df_ordenado["Data"], format="%d/%m/%Y", errors='coerce')
        df_ordenado = df_ordenado.dropna(subset=["Data_Parsed"]).sort_values("Data_Parsed")
        
        if not df_ordenado.empty:
            proxima_data = df_ordenado.iloc[0]["Data"]
            nome_proxima = df_ordenado.iloc[0]["Corrida"]
            # Corta o nome se for muito comprido para caber no cartão
            if len(nome_proxima) > 25:
                nome_proxima = nome_proxima[:22] + "..."
            info_proxima = f"{proxima_data} ({nome_proxima})"
        else:
            info_proxima = "Sem datas válidas"
    except Exception:
        info_proxima = df_filtrado.iloc[0]["Data"]
else:
    total_provas = 0
    total_estados = 0
    info_proxima = "Nenhuma"

# Preenchendo os cartões bonitinhos com emojis
col1.metric(label="Total de Provas Mapeadas 👟", value=total_provas)
col2.metric(label="Estados com Eventos 📍", value=total_estados)
col3.metric(label="Próxima Prova no Radar 📅", value=info_proxima)

st.markdown("---")
# ---------------------------------


# --- EXIBIÇÃO DA TABELA PRINCIPAL ---
st.subheader(f"📅 Calendário de Provas Disponíveis")

if not df_filtrado.empty:
    st.dataframe(
        df_filtrado,
        column_config={
            "Mês": st.column_config.TextColumn("Mês 🗓️"),
            "Estado": st.column_config.TextColumn("UF 📍"),
            "Data": st.column_config.TextColumn("Data 📅"),
            "Corrida": st.column_config.TextColumn("Nome do Evento 👟"),
            "Distâncias": st.column_config.TextColumn("Distâncias 🗺️"),
            "Inscrição": st.column_config.LinkColumn("Inscrição 🔗", display_text="Ver Inscrição"),
        },
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("Nenhuma corrida localizada para os filtros selecionados. Altere os filtros na barra lateral!")