import pandas as pd
import os

# CONFIGURAÇÃO
ARQUIVO_MESTRE = "grade_completa.csv"
ARQUIVO_EXTERNO = "programas1.csv" # Nome do arquivo que você quer inserir

if os.path.exists(ARQUIVO_EXTERNO) and os.path.exists(ARQUIVO_MESTRE):
    # 1. Carrega os dois arquivos
    df_mestre = pd.read_csv(ARQUIVO_MESTRE)
    df_externo = pd.read_csv(ARQUIVO_EXTERNO)
    
    print(f"Linhas no mestre: {len(df_mestre)}")
    print(f"Linhas no externo: {len(df_externo)}")

    # 2. Padroniza as colunas do externo para garantir que batam com o mestre
    # (Ajuste os nomes à esquerda se o seu CSV externo usar nomes diferentes)
    df_externo = df_externo.rename(columns={
        'dia': 'Data', 
        'title': 'Programa', 
        'episodeName': 'Episódio', 
        'mediaId': 'Media'
    })

    # 3. Garante que o externo tenha apenas as colunas que o mestre usa
    # (Removendo 'Hora' ou 'Nº do episódio' se existirem no externo)
    colunas_mestre = ['Data', 'Programa', 'Episódio', 'Media']
    df_externo = df_externo[colunas_mestre]

    # 4. Junta os dois
    df_combinado = pd.concat([df_mestre, df_externo], ignore_index=True)

    # 5. REMOVE DUPLICATAS
    # Ele olha para Media, Programa e Episódio. Se forem iguais, ele apaga a cópia.
    df_combinado = df_combinado.drop_duplicates(subset=['Media', 'Programa', 'Episódio'], keep='first')

    # 6. Re-ordena tudo por Data (para não ficar bagunçado no meio)
    df_combinado['Data_Temp'] = pd.to_datetime(df_combinado['Data'], format='%d/%m/%Y', errors='coerce')
    df_combinado = df_combinado.sort_values(by=['Programa', 'Data_Temp'], ascending=[True, True])
    df_combinado = df_combinado.drop(columns=['Data_Temp'])

    # 7. Salva o resultado final no grade_completa.csv
    df_combinado.to_csv(ARQUIVO_MESTRE, index=False, encoding='utf-8-sig')
    
    print(f"Sucesso! Novo total de linhas: {len(df_combinado)}")
    print(f"Foram adicionados {len(df_combinado) - len(df_mestre)} novos registros únicos.")

else:
    print("Erro: Verifique se os nomes dos arquivos estão corretos e se ambos estão na mesma pasta.")
