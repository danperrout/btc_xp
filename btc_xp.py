# importing all the required modules
import PyPDF2
import pandas as pd
import os
   
def list_pdfs():
    return [file for file in os.listdir() if file.endswith('.pdf')]

def string_to_float(string_num):
    # Remover os pontos (separadores de milhares)
    string_num = string_num.replace(".", "")

    # Substituir a vírgula pelo ponto (separador decimal)
    string_num = string_num.replace(",", ".")

    try:
        float_num = float(string_num)
        return (float_num)
    except ValueError:
        # print(f"{string_num} => A string não pode ser convertida em um número float.")
        return string_num
    
def extract_btc_values(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)

    page_number = 0
    data_list = []

    for page in (reader.pages):
        text = reader.pages[page_number].extract_text() 
        
        page_number = page_number + 1
        # print(f'--- Página {page_number} ---')

        allow_value = False
        allow_value_line = 0
        last_line = 12
        data_temp = []
        columns_list = []
        
        # Divide o texto em linhas
        lines = text.splitlines()
        current_line = 0
        # Imprime o texto linha a linha
        for line in lines:        
            if allow_value:
                line_value = (string_to_float(line))
                if isinstance(line_value, float):
                    data_temp.append(line_value)
                else:
                    columns_list.append(line_value)
                    
                allow_value_line = allow_value_line + 1
                
                if allow_value_line == last_line:
                    allow_value_line = 0
                
            if "Resumo Financeiro" in line:
                allow_value = True
                allow_value_line = 0
                
            if "Data de Emissão" in line:
                i = 0
                for i in range(8):           
                    line_value = lines[current_line + i].strip()
                    if i<4:
                        columns_list.append(line_value)
                    else:
                        data_temp.append(line_value)
                
            current_line = current_line + 1  
                
        data_list.append(data_temp)

    # Convertendo a lista de listas em um DataFrame
    df = pd.DataFrame(data_list, columns=columns_list)
    df['Data de Liquidação'] = pd.to_datetime(df['Data de Liquidação'], format='%d/%m/%Y')

    # remove .pdf extension from file:
    pdf_name = pdf_path.split(".")[0]
    
    excel_file = f'{pdf_name}.xlsx'
    
    print(f'Saving: {excel_file}')
    
    df.to_excel(excel_file)

    # Converter as columns_list de datas para o formato %d/%m/%Y
    df['Data de Emissão'] = pd.to_datetime(df['Data de Emissão'], format='%d/%m/%Y', errors='coerce')
    df['Data de Liquidação'] = pd.to_datetime(df['Data de Liquidação'], format='%d/%m/%Y', errors='coerce')

    df['Custos'] = df[['Emolumentos', 'IRRF', 'Execução', 'Clearing']].sum(axis=1)
    # Criar uma nova coluna com o ano da 'Data de Emissão'
    df['Ano'] = df['Data de Liquidação'].dt.year

    # Agrupar por ano e somar as outras columns_list
    df_result = df.groupby('Ano').sum(numeric_only=True)

    # Mostrar o df_result
    print(df_result)

    # Criar novas columns_list para o mês e o ano a partir da coluna 'Data de Emissão'
    df['Ano_Mes'] = df['Data de Liquidação'].dt.to_period('M')

    # Agrupar por Ano_Mes e somar as columns_list numéricas
    df_result = df.groupby('Ano_Mes').sum(numeric_only=True)
    
    # remove column 'Ano' from df:
    del df_result['Ano']

    # Mostrar o df_result
    return (df_result)


if __name__ == "__main__":
    print("Starting...")
    for file in (list_pdfs()):
        print(f'Extracting values from: {file}')
        print(extract_btc_values(file))





   