# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:20:57 2026

@author: peque
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup


def minerar_corridas():
    st.info("Iniciando a busca automática de corridas...")

    # Exemplo de URL de um portal de inscrições (ou uma página de eventos)
    url = "https://exemplo-portal-de-corridas.com.br/calendario"

    # Simulando a raspagem (Web Scraping)
    # Na prática, o robô requisita a página e varre as tags HTML do site
    try:
        # response = requests.get(url)
        # soup = BeautifulSoup(response.text, 'html.parser')

        # Simulando os dados capturados pelo robô após ler o HTML
        dados_raspados = [
            {
                "Mês": "Agosto",
                "Estado": "SP",
                "Data": "23/08/2026",
                "Corrida": "Circuito das Estações - Etapa Primavera",
                "Distâncias": "5k, 10k",
                "Inscrição": "https://www.ticketsports.com.br",
            },
            {
                "Mês": "Setembro",
                "Estado": "SC",
                "Data": "06/09/2026",
                "Corrida": "Corrida Noturna de Jaraguá do Sul",
                "Distâncias": "5k, 10k",
                "Inscrição": "https://www.ticketsports.com.br",
            },
        ]

        # Salva o resultado no arquivo automático
        df_auto = pd.DataFrame(dados_raspados)
        df_auto.to_csv("corridas_automaticas.csv", index=False)
        print("Planilha automatizada atualizada com sucesso!")

    except Exception as e:
        print(f"Erro ao minerar dados: {e}")


if __name__ == "__main__":
    minerar_corridas()