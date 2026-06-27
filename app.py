# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:08:07 2026

@author: peque
"""

import streamlit as st
import pandas as pd

# Configuração da página pública do portal
st.set_page_config(
    page_title="Calendário Nacional de Corridas de Rua",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Cabeçalho do Portal Público
st.title("🏃‍♂️ Calendário Nacional de Corridas de Rua")
st.markdown("Encontre seu próximo desafio! Filtre por região, mês ou distância e clique no link para se inscrever.")

# 1. Banco de Dados Coletivo (Exemplos de provas pelo Brasil para a comunidade)
@st.cache_data
def carregar_dados_publicos():
    dados = [
        {"Mês": "Agosto", "Estado": "GO", "Data": "15/08/2026", "Corrida": "Circuito das Estações - Etapa Goiânia", "Distâncias": "5k, 10k", "Inscrição": "https://www.ticketsports.com.br"},
        {"Mês": "Setembro", "Estado": "SP", "Data": "13/09/2026", "Corrida": "Maratona Internacional de São Paulo", "Distâncias": "5k, 10k, 21k, 42k", "Inscrição": "https://www.ticketsports.com.br"},
        {"Mês": "Outubro", "Estado": "SC", "Data": "18/10/2026", "Corrida": "Meia Maratona Internacional de Florianópolis", "Distâncias": "5k, 21k", "Inscrição": "https://www.ticketsports.com.br"},
        {"Mês": "Novembro", "Estado": "PR", "Data": "15/11/2026", "Corrida": "Maratona de Curitiba", "Distâncias": "10k, 42k", "Inscrição": "https://www.ticketsports.com.br"},
        {"Mês": "Março", "Estado": "GO", "Data": "28/03/2027", "Corrida": "Meia Maratona Oficial de Goiânia", "Distâncias": "5k, 10k, 21k", "Inscrição": "https://www.ticketsports.com.br"},
    ]
    return pd.DataFrame(dados)

df_comunidade = carregar_dados_publicos()

# 2. Barra Lateral de Filtros para o Usuário Procurar as Provas
st.sidebar.header("🔍 Buscar Próximas Corridas")

# Filtro por Estado (UF)
estados = ["Todos"] + sorted(list(df_comunidade["Estado"].unique()))
estado_sel = st.sidebar.selectbox("Filtrar por Estado (UF)", estados)

# Filtro por Mês
meses = ["Todos", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
mes_sel = st.sidebar.selectbox("Filtrar por Mês", meses)

# Filtro por Distância (Texto livre para aceitar qualquer km: 5k, 21k, Ultramaratonas, etc.)
distancia_sel = st.sidebar.text_input("Buscar por distância específica (Ex: 5k, 21k, 42k)", "")

# Aplicando a lógica dos filtros no DataFrame
df_filtrado = df_comunidade.copy()

if estado_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_sel]

if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mês"] == mes_sel]

if distancia_sel:
    df_filtrado = df_filtrado[df_filtrado["Distâncias"].str.contains(distancia_sel, case=False)]

# 3. Exibição dos Resultados para o Público
st.write("---")
st.subheader(f"📅 Provas Encontradas ({len(df_filtrado)})")

if not df_filtrado.empty:
    st.dataframe(
        df_filtrado,
        column_config={
            "Mês": st.column_config.TextColumn("Mês 🗓️"),
            "Estado": st.column_config.TextColumn("UF 📍"),
            "Data": st.column_config.TextColumn("Data 📅"),
            "Corrida": st.column_config.TextColumn("Nome do Evento 👟"),
            "Distâncias": st.column_config.TextColumn("Distâncias Disponíveis 🗺️"),
            "Inscrição": st.column_config.LinkColumn("Link para Inscrição 🔗", display_text="Ver Inscrição")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("Nenhuma corrida localizada para os filtros selecionados. Tente expandir sua busca!")