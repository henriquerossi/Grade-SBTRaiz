import pandas as pd
import os

ARQUIVO_MESTRE = "grade_completa.csv"

if os.path.exists(ARQUIVO_MESTRE):
    # 1. Carrega o arquivo atual
    df = pd.read_csv(ARQUIVO_MESTRE)
    
    # 2. Remove a coluna de Hora (se ela existir)
    if 'Hora' in df.columns:
        df = df.drop(columns=['Hora'])
    
    # 3. Remove duplicatas baseando-se no conteúdo
    # Vamos manter apenas a PRIMEIRA vez que o episódio apareceu (Data mais antiga)
    # Para isso, garantimos que está ordenado por data antes de remover
    df['Data_Temp'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    df = df.sort_values(by=['Data_Temp'])
    
    # Agora removemos as duplicatas de programas/episódios
    # Se o ID 'Media' for igual, ou se Programa + Episódio forem iguais, ele apaga a repetição
    df_limpo = df.drop_duplicates(subset=['Media', 'Programa', 'Episódio'], keep='first')
    
    # 4. Ordenação final para o catálogo (por Programa e Nº do episódio)
    df_limpo = df_limpo.sort_values(by=['Programa', 'Nº do episódio'])
    
    # Remove a coluna de data temporária
    df_limpo = df_limpo.drop(columns=['Data_Temp'])
    
    # 5. Sobrescreve o arquivo com a versão "Catálogo"
    df_limpo.to_csv(ARQUIVO_MESTRE, index=False, encoding='utf-8-sig')
    
    print(f"Sucesso! O arquivo {ARQUIVO_MESTRE} agora é um catálogo único.")
    print(f"Linhas antes: {len(df)} | Linhas agora: {len(df_limpo)}")
else:
    print("Arquivo grade_completa.csv não encontrado na raiz.")
