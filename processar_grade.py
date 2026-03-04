import pandas as pd
import requests
from datetime import datetime

# Substitua pela URL real do JSON entre as aspas
URL_JSON = "SUA_URL_AQUI"

try:
    response = requests.get(URL_JSON)
    dados = response.json()

    df = pd.DataFrame(dados)

    # 1. Extrair o 'content_episode' de dentro de 'macros'
    df_macros = pd.json_normalize(df['macros'])
    df['content_episode'] = df_macros['content_episode']

    # 2. Tratar Datas e Horários (Fuso de Brasília)
    dt_series = pd.to_datetime(df['startTime'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')
    df['dia'] = dt_series.dt.strftime('%d/%m/%Y')
    df['horario'] = dt_series.dt.strftime('%H:%M')

    # 3. Selecionar colunas pedidas
    colunas_finais = ['dia', 'horario', 'title', 'episodeName', 'content_episode', 'mediaId']
    df_resultado = df[colunas_finais]

    # 4. Criar nome do arquivo com a data de HOJE para não sobrescrever
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    nome_arquivo = f"grade_{data_hoje}.csv"

    # 5. Salvar o novo arquivo
    df_resultado.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
    print(f"Sucesso: Arquivo {nome_arquivo} criado!")

except Exception as e:
    print(f"Erro: {e}")
