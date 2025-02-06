import os
import sys
import requests

codigo_solicitacao = os.environ.get("CODIGO_SOLICITACAO", "<ALGUM_CODIGO_DE_SOLICITACAO>")

API_BASE_URL = "http://localhost:5000"

if __name__ == "__main__":
  url = f"{API_BASE_URL}/boletos/{codigo_solicitacao}/pdf"
  headers = {
    "Authorization": "Bearer <TOKEN_DA_API_E_NAO_DO_INTER>",
    "Accept": "application/json"
  }

  try:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      print("Erro obtendo o PDF")
      sys.exit(1)
    
    # salva o conteudo da resposta em um arquivo, pois ja retorna como bytes
    with open(f"{codigo_solicitacao}-cobranca.pdf", "wb") as pdf_file:
      pdf_file.write(response.content)
    print(f"PDF salvo em {codigo_solicitacao}-cobranca.pdf")
    
  except Exception as e:
    print(e)
    sys.exit(1)
