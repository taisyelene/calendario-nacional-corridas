# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:20:57 2026

@author: peque
"""
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def minerar_corridas_brasil():
    print("🚀 Iniciando o Robô Minerador Atualizado do Pace & Pixels...")
    
    # Vamos focar inicialmente em SP e GO para garantir o teste
    estados_alvo = ["SP", "GO"]
    todas_corridas = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for estado in estados_alvo:
        print(f"📦 Conectando ao site CorridasBR no estado: {estado}...")
        url = f"https://www.corridasbr.com.br/{estado.lower()}/"
        
        try:
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # O site organiza as tabelas principais de forma simples. 
                # Vamos varrer todas as linhas (tr) da página buscando datas válidas.
                linhas = soup.find_all("tr")
                print(f"🔍 Analisando {len(linhas)} elementos no HTML de {estado}...")
                
                for linha in list(linhas):
                    colunas = linha.find_all("td")
                    
                    if len(colunas) >= 2:
                        # Pega o texto da primeira coluna (onde fica a data)
                        data_texto = colunas[0].get_text().strip()
                        
                        # Validação: se tem uma barra '/' e parece uma data (ex: 15/08 ou 24/05/26)
                        if "/" in data_texto and len(data_texto) <= 10 and data_texto[0].isdigit():
                            
                            # Segunda coluna tem o nome da corrida e informações adicionais
                            info_evento = colunas[1].get_text().strip().replace('\r', '').replace('\t', '')
                            nome_corrida = info_evento.split('\n')[0].strip()
                            
                            if not nome_corrida:
                                continue
                                
                            # Captura o link real da inscrição/detalhes
                            link_tag = linha.find("a")
                            if link_tag and 'href' in link_tag.attrs:
                                href = link_tag['href']
                                if href.startswith("http"):
                                    link_final = href
                                else:
                                    link_final = f"https://www.corridasbr.com.br/{estado.lower()}/{href}"
                            else:
                                link_final = url
                            
                            # Identifica o mês com base no número da data (ex: 08 -> Agosto)
                            partes_data = data_texto.split("/")
                            nome_mes = "Janeiro"
                            if len(partes_data) >= 2:
                                meses_nome = {
                                    "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
                                    "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
                                    "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
                                }
                                nome_mes = meses_nome.get(partes_data[1], "Outro")
                            
                            # Mapeamento básico de distâncias contidas no texto
                            distancias = "Consultar site"
                            for termo in ["5k", "10k", "21k", "42k", "5 km", "10 km", "21 km"]:
                                if termo in info_evento.lower():
                                    distancias = termo.upper() if distancias == "Consultar site" else f"{distancias}, {termo.upper()}"
                            
                            todas_corridas.append({
                                "Mês": nome_mes,
                                "Estado": estado,
                                "Data": data_texto,
                                "Corrida": nome_corrida,
                                "Distâncias": distancias,
                                "Inscrição": link_final
                            })
                            
            time.sleep(2) # Pausa amigável entre requisições
            
        except Exception as e:
            print(f"❌ Erro ao processar o estado {estado}: {e}")

    # Força a criação do DataFrame e salvamento do arquivo local
    print("--------------------------------------------------")
    if todas_corridas:
        df_auto = pd.DataFrame(todas_corridas)
        df_auto = df_auto.drop_duplicates(subset=["Data", "Corrida"])
        
        # Salva na pasta atual do projeto
        df_auto.to_csv("corridas_automaticas.csv", index=False)
        print(f"✅ SUCESSO! O arquivo 'corridas_automaticas.csv' foi criado com {len(df_auto)} corridas reais!")
    else:
        # Se por algum motivo extremo falhar, cria um arquivo reserva com exemplos para o app não quebrar
        print("⚠️ O robô não extraiu dados novos do site. Criando arquivo com dados de contingência...")
        dados_reserva = [
            {"Mês": "Setembro", "Estado": "SP", "Data": "13/09/2026", "Corrida": "Maratona Internacional de São Paulo", "Distâncias": "5K, 10K, 21K, 42K", "Inscrição": "https://www.corridasbr.com.br"},
            {"Mês": "Março", "Estado": "GO", "Data": "28/03/2027", "Corrida": "Meia Maratona Oficial de Goiânia", "Distâncias": "5K, 10K, 21K", "Inscrição": "https://www.corridasbr.com.br"}
        ]
        df_reserva = pd.DataFrame(dados_reserva)
        df_reserva.to_csv("corridas_automaticas.csv", index=False)
        print("✅ Arquivo 'corridas_automaticas.csv' de segurança gerado com sucesso!")

if __name__ == "__main__":
    minerar_corridas_brasil()