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
    </style>
""", unsafe_allow_html=True)

# Função para carregar os dados das corridas
@st.cache_data(ttl=600)
def carregar_dados():
    # Caminho do arquivo gerado pelo robô
    arquivo_csv = "corridas_automaticas.csv"
    
    if os.path.exists(arquivo_csv):
        try:
            df = pd.read_csv(arquivo_csv)
            # Garante que as colunas essenciais existem e estão formatadas
            colunas_obrigatorias = ["Mês", "Estado", "Data", "Corrida", "Distâncias", "Inscrição"]
            for col in colunas_obrigatorias:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception as e:
            st.error(f"Erro ao ler os dados locais: {e}")
            return pd.DataFrame()
    else:
        # Banco de dados reserva caso o robô ainda não tenha rodado nenhuma vez
        dados_reserva = [
            {"Mês": "Julho", "Estado": "SP", "Data": "12/07/2026", "Corrida": "Circuito Family Running - Etapa Capital", "Distâncias": "5K, 10K", "Inscrição": "https://www.ticketsports.com.br"},
            {"Mês": "Julho", "Estado": "GO", "Data": "19/07/2026", "Corrida": "Circuito das Estações - Etapa Goiânia", "Distâncias": "5K, 10K", "Inscrição": "https://www.ticketsports.com.br"},
            {"Mês": "Julho", "Estado": "DF", "Data": "26/07/2026", "Corrida": "Circuito Caixa Seguridade - Brasília", "Distâncias": "5K, 10K, 21K", "Inscrição": "https://www.ticketsports.com.br"},
            {"Mês": "Agosto", "Estado": "RJ", "Data": "09/08/2026", "Corrida": "Meia Maratona do Rio de Janeiro 2026", "Distâncias": "5K, 10K, 21K", "Inscrição": "https://www.ticketsports.com.br"},
            {"Mês": "Setembro", "Estado": "MG", "Data": "13/09/2026", "Corrida": "Volta da Pampulha - Belo Horizonte", "Distâncias": "18K", "Inscrição": "https://www.ticketsports.com.br"}
        ]
        return pd.DataFrame(dados_reserva)

# Carrega a base de dados
df_completo = carregar_dados()

# Título Principal do Portal
st.title("🏃‍♂️ Pace & Pixels")
st.subheader("Calendário Nacional de Corridas de Rua")

if df_completo.empty:
    st.warning("Nenhum dado de corrida encontrado. Rode o minerador.py para gerar a lista de provas!")
else:
    # Extrai todas as distâncias individuais de forma inteligente e limpa
    todas_distancias = set()
    for dist_str in df_completo["Distâncias"].dropna().astype(str):
        # Divide por vírgula, remove espaços e padroniza para maiúsculo
        partes = [d.strip().upper() for d in dist_str.split(",") if d.strip()]
        todas_distancias.update(partes)
    
    # Remove textos genéricos/informativos das opções de filtro
    termos_ignorar = {"CONSULTAR SITE", "CONSULTAR NO SITE", "A CONSULTAR", "OUTRO"}
    dist_limpas = {d for d in todas_distancias if d not in termos_ignorar and len(d) <= 10}
    
    # Ordena as distâncias (ex: 5K, 10K, 21K, 42K)
    def ordenar_distancias(item):
        # Tenta extrair o número para ordenar numericamente (ex: "5K" -> 5)
        numeros = "".join([c for c in item if c.isdigit()])
        return int(numeros) if numeros else 999
        
    dist_ordenadas = sorted(list(dist_limpas), key=ordenar_distancias)

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("🔍 Filtros de Busca")
    
    # 1. Filtro de Estado
    estados_disponiveis = sorted(df_completo["Estado"].dropna().unique().tolist())
    filtro_estado = st.sidebar.selectbox("Selecionar Estado (UF):", ["Todos"] + estados_disponiveis)
    
    # 2. Filtro de Mês
    meses_disponiveis = ["Todos", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    filtro_mes = st.sidebar.selectbox("Selecionar Mês:", meses_disponiveis)

    # 3. Filtro de Distâncias (Múltipla Escolha para maior flexibilidade!)
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
        # Mantém a corrida se ela tiver pelo menos uma das distâncias escolhidas pelo usuário
        mascara = df_filtrado["Distâncias"].apply(
            lambda x: any(dist in str(x).upper() for dist in filtro_distancias) if pd.notna(x) else False
        )
        df_filtrado = df_filtrado[mascara]

    # --- PROCESSAMENTO DE MÉTRICAS ---
    total_provas = len(df_filtrado)
    
    # Encontra a prova mais próxima da data atual
    prova_destaque_nome = "Nenhuma encontrada"
    prova_destaque_meta = "Ajuste os filtros"
    
    hoje = datetime.now()
    provas_futuras = []
    
    for idx, row in df_filtrado.iterrows():
        try:
            # Tenta converter a data da prova para comparação (Padrão DD/MM/AAAA)
            data_str = str(row["Data"]).split()[0]
            data_dt = datetime.strptime(data_str, "%d/%m/%Y")
            if data_dt >= hoje:
                provas_futuras.append((data_dt, row["Corrida"], row["Estado"], row["Data"]))
        except:
            continue
            
    if provas_futuras:
        # Ordena pela data mais próxima do dia de hoje
        provas_futuras.sort(key=lambda x: x[0])
        proxima_prova = provas_futuras[0]
        prova_destaque_nome = proxima_prova[1]
        prova_destaque_meta = f"📅 {proxima_prova[3]} | 📍 {proxima_prova[2]}"

    # --- ROW DE MÉTRICAS (KPIs) ---
    col1, col2, col3 = st.columns([1, 1.8, 1.2])
    
    with col1:
        # Total de provas encontradas com base nos filtros
        st.metric(
            label="Provas Encontradas", 
            value=f"{total_provas} eventos"
        )
        
    with col2:
        # Card customizado com HTML para o Destaque da Próxima Prova (Diminuído para caber tudo!)
        html_card = f"""
        <div class="destaque-card">
            <div class="destaque-titulo">🎯 Próxima Prova em Destaque</div>
            <div class="destaque-nome" title="{prova_destaque_nome}">{prova_destaque_nome}</div>
            <div class="destaque-meta">{prova_destaque_meta}</div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)
        
    with col3:
        # Exibe o total por estado selecionado ou o estado líder em eventos
        if filtro_estado != "Todos":
            st.metric(
                label=f"Eventos em {filtro_estado}", 
                value=f"{total_provas} provas"
            )
        else:
            # Mostra qual estado tem mais eventos cadastrados no momento
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

    # --- GRÁFICO E CONTEÚDO PRINCIPAL ---
    col_tabela, col_grafico = st.columns([1.8, 1.2])
    
    with col_tabela:
        st.subheader("🗓️ Calendário de Corridas")
        
        # Formatação amigável para exibição da tabela
        df_exibicao = df_filtrado[["Data", "Corrida", "Estado", "Distâncias", "Inscrição"]].copy()
        
        # Deixa a coluna de inscrição clicável
        def criar_link(link):
            if pd.isna(link) or not str(link).startswith("http"):
                return "Acessar Site"
            return f'<a href="{link}" target="_blank">Inscrição 🏃‍♂️</a>'
            
        df_exibicao["Inscrição"] = df_exibicao["Inscrição"].apply(criar_link)
        
        # Renderiza a tabela bonita em HTML com suporte a links funcionais
        st.write(
            df_exibicao.to_html(escape=False, index=False), 
            unsafe_allow_html=True
        )

    with col_grafico:
        # Seletor dinâmico de gráfico baseado na requisição do usuário (Total por Estado)
        st.subheader("📊 Distribuição de Provas")
        
        if not df_completo.empty:
            # Agrupa os dados reais por estado para mostrar o total de cada um deles
            contagem_estados = df_completo["Estado"].value_counts().reset_index()
            contagem_estados.columns = ["Estado", "Total de Provas"]
            contagem_estados = contagem_estados.sort_values(by="Total de Provas", ascending=True)
            
            # Gráfico de barras horizontal nativo e super limpo do Streamlit
            st.bar_chart(
                data=contagem_estados,
                x="Estado",
                y="Total de Provas",
                use_container_width=True
            )
            
            # Pequeno painel de texto informativo com os totais exatos por estado
            st.markdown("**Lista de Provas por Estado:**")
            for idx, row in contagem_estados.sort_values(by="Total de Provas", ascending=False).iterrows():
                st.write(f"📍 **{row['Estado']}**: {row['Total de Provas']} provas cadastradas")
        else:
            st.info("Sem dados suficientes para gerar os gráficos por estado.")

# Rodapé simples
st.markdown("---")
st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 12px;'>Pace & Pixels © 2026 | Desenvolvido para Corredores</div>", unsafe_allow_html=True)