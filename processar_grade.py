import pandas as pd
import requests
import os
import re
from datetime import datetime

# Configurações
URL_JSON = "https://bridge.evrideo.tv/SBTEPG?ChannelUID=raiz&DurationHours=168"
ARQUIVO_MESTRE = "grade_completa.csv"

def extrair_data_episodio(texto):
    """Procura data DD/MM/YYYY no nome do episódio para ordenação."""
    match = re.search(r'(\d{2}/\d{2}/\d{4})', str(texto))
    if match:
        try:
            return pd.to_datetime(match.group(1), format='%d/%m/%Y')
        except:
            return None
    return None

try:
    # 1. Preparar ambiente
    if not os.path.exists('grades'):
        os.makedirs('grades')

    # 2. Captura de dados
    response = requests.get(URL_JSON)
    df = pd.DataFrame(response.json())

    # 3. Tratamento de Metadados e Datas de Exibição
    df_macros = pd.json_normalize(df['macros'])
    df['content_episode'] = df_macros['content_episode'] # Mantemos aqui apenas para o backup individual
    
    dt_series = pd.to_datetime(df['startTime'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')
    df['Data'] = dt_series.dt.strftime('%d/%m/%Y')
    df['Hora'] = dt_series.dt.strftime('%H:%M')

    # Renomear para o seu padrão
    df = df.rename(columns={'title': 'Programa', 'episodeName': 'Episódio', 'mediaId': 'Media'})

    # --- PASSO A: SALVAR BACKUP COMPLETO (Histórico individual) ---
    # Aqui mantemos Hora e Nº do episódio caso você precise consultar no futuro
    df_backup = df[['Data', 'Hora', 'Programa', 'Episódio', 'content_episode', 'Media']].copy()
    df_backup = df_backup.rename(columns={'content_episode': 'Nº do episódio'})
    
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    df_backup.to_csv(f"grades/grade_{data_hoje}.csv", index=False, encoding='utf-8-sig')

    # --- PASSO B: ATUALIZAR CATÁLOGO (grade_completa.csv) ---
    # Selecionamos apenas as colunas que você quer no catálogo
    df_novo_item = df[['Data', 'Programa', 'Episódio', 'Media']].copy()

    if os.path.exists(ARQUIVO_MESTRE):
        df_mestre = pd.read_csv(ARQUIVO_MESTRE)
        # Unir o que já existe com os novos dados capturados
        df_final = pd.concat([df_mestre, df_novo_item])
    else:
        df_final = df_novo_item

    # 1. Remover Duplicatas (Mantendo o primeiro registro encontrado)
    df_final = df_final.drop_duplicates(subset=['Media', 'Programa', 'Episódio'], keep='first')

    # 2. Ordenação Inteligente
    # Criamos uma coluna de data real baseada no título do episódio
    df_final['Data_Ref'] = df_final['Episódio'].apply(extrair_data_episodio)
    
    # Se não houver data no título, usa a data de exibição como reserva para ordenar
    df_final['Data_Ref'] = df_final['Data_Ref'].fillna(pd.to_datetime(df_final['Data'], format='%d/%m/%Y'))

    # Ordena por Programa e depois pela data do conteúdo
    df_final = df_final.sort_values(by=['Programa', 'Data_Ref'], ascending=[True, True])

    # 3. Remover a coluna de referência e salvar
    df_final = df_final.drop(columns=['Data_Ref'])
    df_final.to_csv(ARQUIVO_MESTRE, index=False, encoding='utf-8-sig')
    
    print(f"Processo concluído: {len(df_final)} itens únicos no catálogo.")

except Exception as e:
    print(f"Erro no processamento: {e}")
