import pandas as pd
import glob
import os

# 1. Procurar todos os arquivos dentro da pasta 'grades'
arquivos = glob.glob("grades/*.csv")

if not arquivos:
    print("Nenhum arquivo encontrado na pasta 'grades'.")
else:
    # 2. Ler e juntar todos os arquivos
    lista_dfs = [pd.read_csv(f) for f in arquivos]
    df_consolidado = pd.concat(lista_dfs)

    # 3. Remover duplicatas
    df_consolidado = df_consolidado.drop_duplicates(subset=['Data', 'Hora', 'Programa'], keep='first')

    # --- NOVO: Ordenar por Data e Hora ---
    # Transforma temporariamente em data real para ordenar (formato DD/MM/YYYY)
    df_consolidado['Dia_Data'] = pd.to_datetime(df_consolidado['Data'], format='%d/%m/%Y')
    
    # Ordena primeiro pelo dia e depois pelo horário
    df_consolidado = df_consolidado.sort_values(by=['Dia_Data', 'Hora'], ascending=[True, True])
    
    # Remove a coluna temporária e mantém o arquivo limpo
    df_consolidado = df_consolidado.drop(columns=['Dia_Data'])
    # -------------------------------------

    # 4. Salvar na raiz
    df_consolidado.to_csv("grade_completa.csv", index=False, encoding='utf-8-sig')
    print(f"Sucesso! {len(arquivos)} arquivos foram unidos em 'grade_completa.csv'.")
