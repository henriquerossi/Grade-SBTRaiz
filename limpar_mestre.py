import pandas as pd
import os
import re

ARQUIVO_MESTRE = "grade_completa.csv"

def extrair_data_episodio(texto):
    # Procura datas no formato DD/MM/YYYY dentro do texto do episódio
    match = re.search(r'(\d{2}/\d{2}/\d{4})', str(texto))
    if match:
        try:
            return pd.to_datetime(match.group(1), format='%d/%m/%Y')
        except:
            return None
    return None

if os.path.exists(ARQUIVO_MESTRE):
    # 1. Carrega o arquivo atual
    df = pd.read_csv(ARQUIVO_MESTRE)
    
    # 2. Remove colunas que você não quer mais no catálogo
    colunas_para_remover = ['Hora', 'Nº do episódio', 'Episódio Nº']
    for col in colunas_para_remover:
        if col in df.columns:
            df = df.drop(columns=[col])
    
    # 3. Limpeza de Duplicatas
    # Ordenamos por Data de exibição antes para garantir que o 'keep=first' pegue a primeira vez
    if 'Data' in df.columns:
        df['Data_Exib_Temp'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
        df = df.sort_values(by='Data_Exib_Temp')
    
    df = df.drop_duplicates(subset=['Media', 'Programa', 'Episódio'], keep='first')

    # 4. Lógica de Ordenação por Data do Conteúdo
    # Criamos a coluna baseada na data que está no NOME do episódio
    df['Data_Conteudo'] = df['Episódio'].apply(extrair_data_episodio)
    
    # Se não tiver data no nome (ex: "Especial"), usa a data de exibição como reserva
    if 'Data_Exib_Temp' in df.columns:
        df['Data_Conteudo'] = df['Data_Conteudo'].fillna(df['Data_Exib_Temp'])
    
    # 5. Ordenação Final: Agrupa por programa e coloca as datas em ordem
    df = df.sort_values(by=['Programa', 'Data_Conteudo'], ascending=[True, True])

    # 6. Limpeza final de colunas temporárias e salvamento
    colunas_finais = [c for c in df.columns if not c.endswith('_Temp') and c != 'Data_Conteudo']
    df_final = df[colunas_finais]
    
    df_final.to_csv(ARQUIVO_MESTRE, index=False, encoding='utf-8-sig')
    
    print(f"Limpeza concluída!")
    print(f"Colunas atuais: {list(df_final.columns)}")
    print(f"Total de itens únicos: {len(df_final)}")
else:
    print(f"Erro: {ARQUIVO_MESTRE} não encontrado.")
