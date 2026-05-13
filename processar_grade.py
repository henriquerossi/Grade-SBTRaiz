import pandas as pd
import requests
import os
from datetime import datetime

# URL do JSON do canal
URL_JSON = "https://bridge.evrideo.tv/SBTEPG?ChannelUID=raiz&DurationHours=168"
ARQUIVO_MESTRE = "grade_completa.csv"

try:
    # 1. Criar a pasta 'grades' se ela não existir
    if not os.path.exists('grades'):
        os.makedirs('grades')

    # 2. Coleta de dados
    response = requests.get(URL_JSON)
    dados = response.json()
    df = pd.DataFrame(dados)

    # 3. Extrair 'content_episode' de 'macros'
    df_macros = pd.json_normalize(df['macros'])
    df['content_episode'] = df_macros['content_episode']

    # 4. Tratar Datas e Horários (Fuso de Brasília)
    dt_series = pd.to_datetime(df['startTime'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')
    df['dia'] = dt_series.dt.strftime('%d/%m/%Y')
    df['horario'] = dt_series.dt.strftime('%H:%M')

    # 5. Selecionar e renomear colunas seguindo o seu padrão exato
    df_resultado = df[['dia', 'horario', 'title', 'episodeName', 'content_episode', 'mediaId']].copy()
    df_resultado = df_resultado.rename(columns={
        'dia': 'Data',
        'horario': 'Hora',
        'title': 'Programa',
        'episodeName': 'Episódio',
        'content_episode': 'Nº do episódio',
        'mediaId': 'Media'
    })

    # --- AÇÃO 1: Salvar Backup Individual na pasta 'grades' ---
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    nome_arquivo_backup = f"grades/grade_{data_hoje}.csv"
    df_resultado.to_csv(nome_arquivo_backup, index=False, encoding='utf-8-sig')

    # --- AÇÃO 2: Atualizar Arquivo Mestre na Raiz ---
    if os.path.exists(ARQUIVO_MESTRE):
        # Lê o mestre que já existe
        df_mestre = pd.read_csv(ARQUIVO_MESTRE)
        
        # Junta o antigo com o novo
        df_final = pd.concat([df_mestre, df_resultado])
        
        # Remove duplicados (mesma Data, Hora e Programa)
        df_final = df_final.drop_duplicates(subset=['Data', 'Hora', 'Programa'], keep='first')
        
        # Ordenação cronológica correta
        df_final['Data_Temp'] = pd.to_datetime(df_final['Data'], format='%d/%m/%Y')
        df_final = df_final.sort_values(by=['Data_Temp', 'Hora']).drop(columns=['Data_Temp'])
    else:
        # Se o mestre não existir, ele será o próprio resultado novo
        df_final = df_resultado

    # Salva o arquivo mestre consolidado na raiz
    df_final.to_csv(ARQUIVO_MESTRE, index=False, encoding='utf-8-sig')
    
    print(f"Sucesso: Backup '{nome_arquivo_backup}' e arquivo mestre '{ARQUIVO_MESTRE}' atualizados!")

except Exception as e:
    print(f"Erro no processamento: {e}")
