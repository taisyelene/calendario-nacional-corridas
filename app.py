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

# COLE O ID DA SUA PLANILHA DO GOOGLE SHEETS AQUI:
ID_DA_PLANILHA = "SEU_ID_DO_GOOGLE_SHEETS_AQUI"


@st.cache_data(ttl=600)  # ttl=600 faz o app atualizar o Sheets a cada 10 minutos
def carregar_todos_os_dados():
    # 1. Carrega os dados gerados automaticamente pelo robô (local)
    if os.path.exists("corridas_automaticas.csv"):
        df_auto = pd.read_csv("corridas_automaticas.csv")
    else:
        df_auto = pd.DataFrame()

    # 2. Carrega os dados inseridos manualmente por você no Google Sheets
    try:
        url_sheets = f"https://docs.google.com/spreadsheets/d/1A0kBTwhI5SY1Fa5DIJL5BvqK_nqHijmBSJtEOGg2qyE/export?format=csv"
        df_manual = pd.read_csv(url_sheets)
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
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

    # 3. Une as duas fontes (Robô + Google Sheets)
    df_final = pd.concat([df_auto, df_manual], ignore_index=True)

    # Limpa duplicados e garante ordem cronológica básica
    df_final = df_final.drop_duplicates(subset=["Data", "Corrida"])
    return df_final


# O restante do código de filtros e exibição da tabela continua exatamente igual!
df_comunidade = carregar_todos_os_dados()

# ... (Mantenha a barra lateral e a tabela st.dataframe do código anterior)