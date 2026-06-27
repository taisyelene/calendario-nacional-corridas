# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:20:57 2026

@author: peque
"""

import time
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup


def minerar_corridas_brasil():
    print("🚀 Iniciando o Robô Minerador do Pace & Pixels...")

    # Lista de estados que você quer varrer no site
    estados_alvo = ["SC", "GO", "SP"]
    todas_corridas = []

    # Ano atual para complementar as datas do site
    ano_atual = datetime.now().year

    for estado in estados_alvo:
        print(f"📦 Varrendo corridas de: {estado}...")
        # O site usa a sigla em letras minúsculas na URL
        url = f"https://www.corridasbr.com.br/{estado.lower()}/"

        try:
            # Simulando um navegador real para o site não bloquear o robô
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # O CorridasBR organiza os eventos dentro de tabelas (tags <table> ou elementos de calendário)
                # Vamos buscar as linhas de tabela (<tr>) que contêm as informações das provas
                linhas = soup.find_all("tr")

                for linha in linhas:
                    colunas = linha.find_all("td")

                    # Uma linha válida geralmente tem colunas para Data, Nome/Local e Link
                    if len(colunas) >= 2:
                        texto_completo = linha.get_text().strip()

                        # Filtro básico: se a linha tem uma data (ex: 15/08 ou 15/08/2026)
                        if (
                            "/" in colunas[0].get_text()
                            and len(colunas[0].get_text().strip()) <= 10
                        ):
                            data_bruta = colunas[0].get_text().strip()

                            # Tratamento do nome do evento e distâncias se houver
                            info_evento = colunas[1].get_text().strip()

                            # Descobre o link para detalhes/inscrição
                            link_tag = linha.find("a")
                            link_final = (
                                f"https://www.corridasbr.com.br/{estado.lower()}/{link_tag['href']}"
                                if link_tag
                                else url
                            )

                            # Identifica o mês com base na data encontrada
                            partes_data = data_bruta.split("/")
                            meses_nome = {
                                "01": "Janeiro",
                                "02": "Fevereiro",
                                "03": "Março",
                                "04": "Abril",
                                "05": "Maio",
                                "06": "Junho",
                                "07": "Julho",
                                "08": "Agosto",
                                "09": "Setembro",
                                "10": "Outubro",
                                "11": "Novembro",
                                "12": "Dezembro",
                            }
                            nome_mes = meses_nome.get(
                                partes_data[1], "Não Identificado"
                            )

                            # Tenta capturar distâncias se estiverem no texto (ex: 5k, 10k, 21k)
                            # Se não achar, deixa como "Consultar site" para não limitar o usuário
                            distancias = "Consultar site"
                            for termo in [
                                "5k",
                                "10k",
                                "21k",
                                "42k",
                                "5 km",
                                "10 km",
                                "21 km",
                            ]:
                                if termo in info_evento.lower():
                                    distancias = (
                                        termo.upper()
                                        if distancias == "Consultar site"
                                        else f"{distancias}, {termo.upper()}"
                                    )

                            # Monta o dicionário no formato exato que o nosso app.py espera
                            corrida_formatada = {
                                "Mês": nome_mes,
                                "Estado": estado,
                                "Data": data_bruta,
                                "Corrida": info_evento.split("\n")[0].strip(),
                                "Distâncias": distancias,
                                "Inscrição": link_final,
                            }

                            todas_corridas.append(corrida_formatada)

            # Pausa de 2 segundos entre os estados para respeitar o servidor do site
            time.sleep(2)

        except Exception as e:
            print(f"❌ Erro ao acessar {estado}: {e}")

    # Salva todos os achados no arquivo que o Streamlit vai ler
    if todas_corridas:
        df_auto = pd.DataFrame(todas_corridas)
        # Remove duplicados para garantir limpeza
        df_auto = df_auto.drop_duplicates(subset=["Data", "Corrida"])
        df_auto.to_csv("corridas_automaticas.csv", index=False)
        print(
            f"✅ Sucesso! {len(df_auto)} corridas foram mineradas e salvas em 'corridas_automaticas.csv'."
        )
    else:
        print("⚠️ Nenhuma corrida nova foi encontrada nessa rodada.")


if __name__ == "__main__":
    minerar_corridas_brasil()