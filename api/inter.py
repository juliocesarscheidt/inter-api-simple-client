import os
import json
import requests
from time import time

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CERT_PATH = os.environ.get("CERT_PATH")
CERT_KEY_PATH = os.environ.get("CERT_KEY_PATH")
ACCOUNT = os.environ.get("ACCOUNT", None)
API_BASE_URL = "https://cdpj.partners.bancointer.com.br"

token_cache = {}

def emitir_cobranca(token, payload):
  headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "Application/json",
  }
  try:
    response = requests.post(f"{API_BASE_URL}/cobranca/v3/cobrancas",
                        headers=headers,
                        cert=(CERT_PATH, CERT_KEY_PATH),
                        data=json.dumps(payload))
    return response.json()
  except Exception as e:
    print(e)
    print("Erro ao emitir cobranca")
    return None

def obter_cobranca(token, codigo_solicitacao):
  headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "Application/json",
  }
  try:
    response = requests.get(f"{API_BASE_URL}/cobranca/v3/cobrancas/{codigo_solicitacao}",
                        headers=headers,
                        cert=(CERT_PATH, CERT_KEY_PATH))
    return response.json()
  except Exception as e:
    print(e)
    print("Erro ao obter cobranca")
    return None

def obter_cobranca_pdf(token, codigo_solicitacao):
  headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "Application/json",
  }
  try:
    response = requests.get(f"{API_BASE_URL}/cobranca/v3/cobrancas/{codigo_solicitacao}/pdf",
                        headers=headers,
                        cert=(CERT_PATH, CERT_KEY_PATH))
    return response.json()
  except Exception as e:
    print(e)
    print("Erro ao obter cobranca pdf")
    return None

def cancelar_cobranca(token, codigo_solicitacao, motivo):
  headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "Application/json",
  }
  payload = {
    "motivoCancelamento": motivo
  }
  try:
    response = requests.post(f"{API_BASE_URL}/cobranca/v3/cobrancas/{codigo_solicitacao}/cancelar",
                        headers=headers,
                        cert=(CERT_PATH, CERT_KEY_PATH),
                        data=json.dumps(payload))
    assert response.status_code == 202
    return True
  except Exception as e:
    print(e)
    print("Erro ao cancelar cobranca")
    return False

def obter_token(scopes=["boleto-cobranca.write", "boleto-cobranca.read"]):
  scopes_param = " ".join(scopes)
  if token_cache.get(scopes_param):
    cached_token = token_cache.get(scopes_param)
    # token is still valid
    if cached_token.get("expires_at") > int(time()):
      print("Returning token from cache", cached_token["token"])
      return cached_token["token"]
  try:
    request_string = f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&scope={scopes_param}&grant_type=client_credentials"
    print("request_string", request_string)
    response = requests.post(url=f"{API_BASE_URL}/oauth/v2/token",
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        cert=(CERT_PATH, CERT_KEY_PATH),
                        data=request_string)
    data_json = response.json()
    token = data_json.get("access_token")
    token_cache[scopes_param] = {
      "token": token,
      "expires_at": data_json.get("expires_in") + int(time()),
    }
    print("returning new token", token)
    return token
  except Exception as e:
    print(f"Erro ao obter token de acesso: {e}")
    return None
