# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:08:07 2026

@author: peque
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Pace & Pixels - Calendário de Corridas",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INSIRA O ID DA SUA PLANILHA DO GOOGLE SHEETS AQUI ---
# Lembre-se de deixar a sua planilha como "Qualquer pessoa com o link pode ler" no botão Compartilhar do Google
ID_PLANILHA = "1A0kBTwhI5SY1Fa5DIJL5BvqK_nqHijmBSJtEOGg2qy"

# Estilização CSS customizada para deixar o visual moderno, limpo e profissional
st.markdown("""
    <style>
        /* Estilização geral do app */
        .main {
            background-color: #f8fafc;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #1e293b;
            font-family: 'Inter', sans-serif;
        }
        
        /* Card personalizado para a próxima prova (evita quebra de fonte) */
        .destaque-card {
            background-color: #ffffff;
            border-left: 5px solid #3b82f6;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            margin-bottom: 10px;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .destaque-titulo {
            font-size: 13px;
            font-weight: 700;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .destaque-nome {
            font-size: 16px;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.3;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .destaque-meta {
            font-size: 13px;
            color: #64748b;
            font-weight: 500;
        }
        
        /* Ajustes nos cards de métricas padrão do Streamlit */
        div[data-testid="stMetricValue"] {
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 14px;
            color: #475569;
            font-weight: 600;
        }
        
        /* Estilização para deixar a tabela HTML limpa e responsiva */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 14px;
            text-align: left;
        }
        th {
            background-color: #f1f5f9;
            color: #475569;
            font-weight: 600;
            padding: 12px;
            border-bottom: 2px solid #e2e8f0;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            color: #334155;
        }
        tr:hover {
            background-color: #f8fafc;
        }
    </style>
""", unsafe_allow_html=True)

# Função robusta para carregar as duas bases de dados (Automática + Manual)
def carregar_dados_completos():
    colunas_padrao = ["Mês", "Estado", "Data", "Corrida", "Distâncias", "Inscrição"]
    
    # 1. Tenta carregar as corridas do Robô (Local)
    df_auto = pd.DataFrame(columns=colunas_padrao)
    arquivo_csv = "corridas_automaticas.csv"
    if os.path.exists(arquivo_csv):
        try:
            df_auto = pd.read_csv(arquivo_csv)
            # Garante que as colunas obrigatórias existem
            for col in colunas_padrao:
                if col not in df_auto.columns:
                    df_auto[col] = ""
        except Exception as e:
            st.sidebar.error(f"Erro ao ler corridas automáticas: {e}")

    # 2. Tenta carregar as corridas do Google Sheets (Manual)
    df_manual = pd.DataFrame(columns=colunas_padrao)
    if ID_PLANILHA and ID_PLANILHA != "1A0kBTwhI5SY1Fa5DIJL5BvqK_nqHijmBSJtEOGg2qyE":
        try:
            # Link de exportação direta em CSV para o Pandas ler instantaneamente
            url_sheets = f"https://docs.google.com/spreadsheets/d/1A0kBTwhI5SY1Fa5DIJL5BvqK_nqHijmBSJtEOGg2qyE/export?format=csv"
            df_manual = pd.read_csv(url_sheets)
            
            # Padroniza as colunas da planilha para o caso de digitação diferente
            df_manual.columns = [c.strip() for c in df_manual.columns]
            for col in colunas_padrao:
                if col not in df_manual.columns:
                    df_manual[col] = ""
            df_manual = df_manual[colunas_padrao]
        except Exception as e:
            st.sidebar.warning("⚠️ Não foi possível conectar ao Google Sheets. Mostrando apenas dados locais.")
            
    # 3. Une e remove duplicados reais (baseado na combinação de Data e Nome da Corrida)
    if not df_auto.empty or not df_manual.empty:
        df_unido = pd.concat([df_auto, df_manual], ignore_index=True)
        # Limpa espaços extras para evitar duplicados bobos
        df_unido["Corrida"] = df_unido["Corrida"].astype(str).str.strip()
        df_unido["Data"] = df_unido["Data"].astype(str).str.strip()
        df_unido = df_unido.drop_duplicates(subset=["Data", "Corrida"])
        return df_unido
    else:
        # Banco de dados reserva caso tudo falhe
        dados_reserva = [
            {"Mês": "Julho", "Estado": "SP", "Data": "12/07/2026", "Corrida": "Circuito Family Running - Etapa Capital (Reserva)", "Distâncias": "5K, 10K", "Inscrição": "https://www.ticketsports.com.br"},
            {"Mês": "Julho", "Estado": "GO", "Data": "19/07/2026", "Corrida": "Circuito das Estações - Etapa Goiânia (Reserva)", "Distâncias": "5K, 10K", "Inscrição": "https://www.ticketsports.com.br"}
        ]
        return pd.DataFrame(dados_reserva)

# Carrega a base de dados unificada
df_completo = carregar_dados_completos()

# Título Principal do Portal
st.title("🏃‍♂️ Pace & Pixels")
st.subheader("Calendário Nacional de Corridas de Rua")

if df_completo.empty:
    st.warning("Nenhum dado de corrida encontrado. Rode o minerador.py para gerar as provas automáticas!")
else:
    # Extrai todas as distâncias individuais de forma inteligente e limpa
    todas_distancias = set()
    for dist_str in df_completo["Distâncias"].dropna().astype(str):
        partes = [d.strip().upper() for d in dist_str.split(",") if d.strip()]
        todas_distancias.update(partes)
    
    termos_ignorar = {"CONSULTAR SITE", "CONSULTAR NO SITE", "A CONSULTAR", "OUTRO"}
    dist_limpas = {d for d in todas_distancias if d not in termos_ignorar and len(d) <= 10}
    
    def ordenar_distancias(item):
        numeros = "".join([c for c in item if c.isdigit()])
        return int(numeros) if numeros else 999
        
    dist_ordenadas = sorted(list(dist_limpas), key=ordenar_distancias)

    st.sidebar.header("🔍 Filtros de Busca")
    
    # 1. Filtro de Estado
    estados_disponiveis = sorted(df_completo["Estado"].dropna().unique().tolist())
    filtro_estado = st.sidebar.selectbox("Selecionar Estado (UF):", ["Todos"] + estados_disponiveis)
    
    # 2. Filtro de Mês
    meses_disponiveis = ["Todos", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    filtro_mes = st.sidebar.selectbox("Selecionar Mês:", meses_disponiveis)

    # 3. Filtro de Distâncias
    filtro_distancias = st.sidebar.multiselect(
        "Selecionar Distâncias (KM):", 
        options=dist_ordenadas,
        help="Selecione uma ou mais distâncias para filtrar as provas disponíveis."
    )
    
    # Aplicando os filtros na base de dados
    df_filtrado = df_completo.copy()
    
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]
        
    if filtro_mes != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mês"] == filtro_mes]

    if filtro_distancias:
        mascara = df_filtrado["Distâncias"].apply(
            lambda x: any(dist in str(x).upper() for dist in filtro_distancias) if pd.notna(x) else False
        )
        df_filtrado = df_filtrado[mascara]

    total_provas = len(df_filtrado)
    
    prova_destaque_nome = "Nenhuma encontrada"
    prova_destaque_meta = "Ajuste os filtros"
    
    hoje = datetime.now()
    provas_futuras = []
    
    for idx, row in df_filtrado.iterrows():
        try:
            data_str = str(row["Data"]).split()[0]
            data_dt = datetime.strptime(data_str, "%d/%m/%Y")
            if data_dt >= hoje:
                provas_futuras.append((data_dt, row["Corrida"], row["Estado"], row["Data"]))
        except:
            continue
            
    if provas_futuras:
        provas_futuras.sort(key=lambda x: x[0])
        proxima_prova = provas_futuras[0]
        prova_destaque_nome = proxima_prova[1]
        prova_destaque_meta = f"📅 {proxima_prova[3]} | 📍 {proxima_prova[2]}"

    # --- ROW DE MÉTRICAS (KPIs) ---
    col1, col2, col3 = st.columns([1, 1.8, 1.2])
    
    with col1:
        st.metric(
            label="Provas Encontradas", 
            value=f"{total_provas} eventos"
        )
        
    with col2:
        html_card = f"""
        <div class="destaque-card">
            <div class="destaque-titulo">🎯 Próxima Prova em Destaque</div>
            <div class="destaque-nome" title="{prova_destaque_nome}">{prova_destaque_nome}</div>
            <div class="destaque-meta">{prova_destaque_meta}</div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)
        
    with col3:
        if filtro_estado != "Todos":
            st.metric(
                label=f"Eventos em {filtro_estado}", 
                value=f"{total_provas} provas"
            )
        else:
            if not df_filtrado.empty:
                ranking_estados = df_filtrado["Estado"].value_counts()
                estado_lider = ranking_estados.index[0]
                total_lider = ranking_estados.values[0]
                st.metric(
                    label=f"Estado Líder ({estado_lider})", 
                    value=f"{total_lider} provas"
                )
            else:
                st.metric(label="Estado Líder", value="0 provas")

    st.markdown("---")

    # --- SEÇÃO 1: GRÁFICOS E TOTAIS NO TOPO ---
    st.subheader("📊 Distribuição de Provas por Estado")
    
    col_grafico, col_lista = st.columns([1.8, 1.2])
    
    with col_grafico:
        if not df_completo.empty:
            contagem_estados = df_completo["Estado"].value_counts().reset_index()
            contagem_estados.columns = ["Estado", "Total de Provas"]
            contagem_estados = contagem_estados.sort_values(by="Total de Provas", ascending=True)
            
            st.bar_chart(
                data=contagem_estados,
                x="Estado",
                y="Total de Provas",
                use_container_width=True
            )
        else:
            st.info("Sem dados suficientes para gerar os gráficos por estado.")

    with col_lista:
        if not df_completo.empty:
            st.markdown("<p style='font-weight: 600; margin-bottom: 8px;'>Total de Eventos Cadastrados:</p>", unsafe_allow_html=True)
            
            col_list_1, col_list_2 = st.columns(2)
            estados_ordenados = contagem_estados.sort_values(by="Total de Provas", ascending=False)
            metade = (len(estados_ordenados) + 1) // 2
            
            with col_list_1:
                for idx, row in estados_ordenados.iloc[:metade].iterrows():
                    st.markdown(f"📍 **{row['Estado']}**: {row['Total de Provas']} provas")
            with col_list_2:
                for idx, row in estados_ordenados.iloc[metade:].iterrows():
                    st.markdown(f"📍 **{row['Estado']}**: {row['Total de Provas']} provas")
        else:
            st.info("Sem dados cadastrados.")

    st.markdown("---")

    # --- SEÇÃO 2: CALENDÁRIO COMPLETO ABAIXO ---
    st.subheader("🗓️ Calendário de Corridas")
    
    if not df_filtrado.empty:
        df_exibicao = df_filtrado[["Data", "Corrida", "Estado", "Distâncias", "Inscrição"]].copy()
        
        def criar_link(link):
            if pd.isna(link) or not str(link).startswith("http"):
                return "Acessar Site"
            return f'<a href="{link}" target="_blank" style="text-decoration: none; color: #3b82f6; font-weight: 600;">Inscrição 🏃‍♂️</a>'
            
        df_exibicao["Inscrição"] = df_exibicao["Inscrição"].apply(criar_link)
        
        st.write(
            df_exibicao.to_html(escape=False, index=False), 
            unsafe_allow_html=True
        )
    else:
        st.info("Nenhuma corrida encontrada para os filtros selecionados.")

# Rodapé
st.markdown("---")
st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 12px;'>Pace & Pixels © 2026 | Desenvolvido para Corredores</div>", unsafe_allow_html=True)