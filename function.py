import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import pandas as pd
import io

cred = credentials.Certificate("C:/Users/matheus.silva1/OneDrive - SHV Energy N.V/Assistente de Instalações Industriais/05 - Retiradas/Projeto - Cadastro retirada/venv/projeto-retiradas-firebase-adminsdk-fbsvc-b7d9ce440f.json")

firebase_admin.initialize_app(cred, {'storageBucket': 'projeto-retiradas.firebasestorage.app'})
bucket = storage.bucket()
def buscar_dados_cliente(codigo_cliente, nome_arquivo_firebase="Base_Carteira_Cliente.xlsx"):

    try:
        blob = bucket.blob("Base de dados/Base_Carteira_Cliente.xlsx") # Assumindo que o arquivo está na pasta 'retiradas'

        blob_data = blob.download_as_bytes()
        df = pd.read_excel(io.BytesIO(blob_data))
        df['Código do Cliente SAP'] = df['Código do Cliente SAP'].astype(int)
        resultado = df[df['Código do Cliente SAP'] == codigo_cliente]


        if not resultado.empty:
            dados = resultado.to_dict('records')[0]
            return {
                'razao_social': resultado['Razão Social / Nome do cliente'].iloc[0],
                'endereco_do_cliente': resultado['Endereço de entrega Linha 1'].iloc[0],
                'nome_da_oportunidade': resultado['Nome Fantasia / Apelido *'].iloc[0]
            }
        else:
            return "Cliente não encontrado"

    except FileNotFoundError:
        return f"Erro: Arquivo '{nome_arquivo_firebase}' não encontrado."
    except Exception as e:
        return f"Ocorreu um erro ao ler o arquivo Excel: {e}"

if __name__ == "__main__":
    codigo_teste = 12345  # Substitua por um código de cliente existente no seu arquivo Excel no Firebase
    resultado_teste = buscar_dados_cliente(codigo_teste)
    print(f"Resultado para o código {codigo_teste}: {resultado_teste}")

    codigo_nao_existente = 99999  # Um código que provavelmente não existe
    resultado_nao_encontrado = buscar_dados_cliente(codigo_nao_existente)
    print(f"Resultado para o código {codigo_nao_existente}: {resultado_nao_encontrado}")

    # Teste de erro (opcional, se quiser simular um problema)
    # resultado_erro = buscar_dados_cliente_firebase(1, nome_arquivo_firebase="arquivo_inexistente.xlsx")
    # print(f"Resultado para arquivo inexistente: {resultado_erro}")