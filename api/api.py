import os
import json
import requests
from time import time, sleep
from functools import wraps
from base64 import b64decode
from datetime import datetime, timedelta
from flask import Flask, Blueprint, jsonify, request, Response
from flask_mysqldb import MySQL
from flask_cors import CORS
from data import buscar_empresa_por_cpf_cnpj


CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CERT_PATH = os.environ.get("CERT_PATH")
CERT_KEY_PATH = os.environ.get("CERT_KEY_PATH")
ACCOUNT = os.environ.get("ACCOUNT", None)
API_BASE_URL = "https://cdpj.partners.bancointer.com.br"


boletos = Blueprint('boletos', __name__, url_prefix='/v1/boletos')

app = Flask(__name__)
cors = CORS(app, resources={r"/v1/boletos/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "OPTIONS"]}})
app.config["CORS_HEADERS"] = ["Content-Type", "Authorization", "Content-Disposition", "Content-Length"]


app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_PORT"] = 3306
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "admin" # weakest password ever - local only
app.config["MYSQL_DB"] = "boletos"
app.config["MYSQL_CURSORCLASS"] = "DictCursor" # para retornar os dados como dicionarios

"""
setup do banco de dados:

create database boletos;

create table boletos.empresa (
  id_empresa int primary key auto_increment,
  nome varchar(255) not null,
  cpf_cnpj varchar(50) not null,
  tipo_pessoa varchar(50) not null,
  telefone varchar(50) not null,
  endereco varchar(255) not null,
  cidade varchar(255) not null,
  uf varchar(10) not null,
  cep varchar(10) not null,
  UNIQUE (cpf_cnpj)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

exemple de insert:

insert into boletos.empresa (nome, cpf_cnpj, tipo_pessoa, telefone, endereco, cidade, uf, cep) values ('Blackdevs', '31335134000197', 'JURIDICA', '999999999', 'R. Teste 1234', 'Curitiba', 'PR', '81000000');
"""

mysql = MySQL(app)
token_cache = {}

def intercept_options(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if request.method == "OPTIONS":
      response = jsonify({"status": "ok"})
      response.headers.add("Access-Control-Allow-Origin", "*")
      response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,OPTIONS")
      response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,Content-Disposition,Content-Length")
      return response, 200
    return f(*args, **kwargs)
  return decorated

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'authorization' not in request.headers:
      return jsonify({"erro": "Token de acesso necessario"}), 401

    token_header = request.headers['authorization']
    jwt_token = token_header.split(" ")[1]
    # validate token, extract data, etc
    print("jwt_token", jwt_token)
    # hardcoding the payload for testing
    data = {
      "scopes": ["boleto-cobranca.write", "boleto-cobranca.read"]
    }
    return f(data, *args, **kwargs)
  return decorated

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


@boletos.route('/', methods=['POST', 'OPTIONS'])
@intercept_options
@token_required
def gerar_boletos(token_data):
  payload = request.json
  print("payload", payload)

  valor_servico = payload["valor_servico"] if "valor_servico" in payload else None
  cpf_cnpj = payload["cpf_cnpj"] if "cpf_cnpj" in payload else None

  if valor_servico is None or cpf_cnpj is None:
    return jsonify({"erro": "Necessario informar os parametros: valor_servico, cpf_cnpj"}), 400

  scopes = token_data.get('scopes', [])
  print("token_data", token_data)

  if 'boleto-cobranca.write' not in scopes:
    return jsonify({"erro": "Permissao necessaria: boleto-cobranca.write"}), 403

  token = obter_token(scopes)
  if not token:
    return jsonify({"erro": "Falha ao obter o token de acesso"}), 401

  hoje = datetime.now()

  # Verifica se os boletos podem ser gerados
  if hoje.day > 30:
    return jsonify({"erro": "Boletos so podem ser gerados ate o dia 30 de cada mes"}), 403

  empresa = None
  with mysql.connection.cursor() as cursor:
    empresa = buscar_empresa_por_cpf_cnpj(cursor, cpf_cnpj)
    if empresa is None:
      return jsonify({"erro": "Cliente nao encontrado"}), 404
  print("empresa", empresa)

  id_empresa = empresa["id_empresa"]
  vencimento = (hoje + timedelta(days=7)).strftime("%Y-%m-%d")

  dados_cobranca = {
    "seuNumero": f"boleto-{id_empresa}",
    "valorNominal": str(valor_servico),
    "dataVencimento": vencimento,
    "numDiasAgenda": 0,
    "pagador": {
      "cpfCnpj": cpf_cnpj,
      "tipoPessoa": empresa["tipo_pessoa"], # FISICA or JURIDICA
      "nome": empresa["nome"],
      "telefone": empresa["telefone"],
      "endereco": empresa["endereco"],
      "cidade": empresa["cidade"],
      "uf": empresa["uf"],
      "cep": empresa["cep"],
    },
    "formasRecebimento": ["BOLETO", "PIX"],
  }

  emissao_cobranca = emitir_cobranca(token, dados_cobranca)
  codigo_solicitacao = emissao_cobranca.get("codigoSolicitacao") if emissao_cobranca else None
  print("codigo_solicitacao", codigo_solicitacao)

  if codigo_solicitacao is None:
    return jsonify({"erro": "Erro ao emitir cobranca"}), 500

  return jsonify({
    "cliente": empresa,
    "status": "sucesso",
    "codigo_solicitacao": codigo_solicitacao,
  }), 200


@boletos.route('/<codigo_solicitacao>', methods=['GET', 'OPTIONS'])
@intercept_options
@token_required
def recuperar_cobranca(token_data, codigo_solicitacao):
  print("codigo_solicitacao", codigo_solicitacao)

  scopes = token_data.get('scopes', [])
  print("token_data", token_data)

  if 'boleto-cobranca.read' not in scopes:
    return jsonify({"erro": "Permissao necessaria: boleto-cobranca.read"}), 403

  token = obter_token(scopes)
  if not token:
    return jsonify({"erro": "Falha ao obter o token de acesso"}), 401

  cobranca = obter_cobranca(token, codigo_solicitacao)
  if cobranca is None:
    return jsonify({"erro": "Erro ao obter PDF"}), 404

  try:
    codigo_barras = cobranca.get("boleto").get("codigoBarras")
    linha_digitavel = cobranca.get("boleto").get("linhaDigitavel")
    pix_copia_e_cola = cobranca.get("pix").get("pixCopiaECola")

    return jsonify({
      "codigo_solicitacao": codigo_solicitacao,
      "codigo_barras": codigo_barras,
      "linha_digitavel": linha_digitavel,
      "pix_copia_e_cola": pix_copia_e_cola,
    }), 200

  except Exception as e:
    return jsonify({"erro": f"Erro ao buscar cobranca: {e}"}), 500


@boletos.route('/<codigo_solicitacao>/pdf', methods=['GET', 'OPTIONS'])
@intercept_options
@token_required
def recuperar_boleto(token_data, codigo_solicitacao):
  print("codigo_solicitacao", codigo_solicitacao)

  scopes = token_data.get('scopes', [])
  print("token_data", token_data)

  if 'boleto-cobranca.read' not in scopes:
    return jsonify({"erro": "Permissao necessaria: boleto-cobranca.read"}), 403

  token = obter_token(scopes)
  if not token:
    return jsonify({"erro": "Falha ao obter o token de acesso"}), 401

  cobranca_pdf = obter_cobranca_pdf(token, codigo_solicitacao)
  if cobranca_pdf is None:
    return jsonify({"erro": "Erro ao obter PDF"}), 404

  try:
    pdf_content_base64 = cobranca_pdf["pdf"]
    pdf_content_bytes = b64decode(pdf_content_base64, validate=True)
    return Response(pdf_content_bytes,
                    mimetype='application/pdf',
                    headers={
                      "Content-Disposition": "inline; filename=boleto.pdf",
                      "Content-Type": "application/pdf",
                      "Content-Length": len(pdf_content_bytes)
                    })
  except Exception as e:
    return jsonify({"erro": f"Erro ao decodificar PDF: {e}"}), 500


@boletos.route('/<codigo_solicitacao>/cancelar', methods=['PUT', 'OPTIONS'])
@intercept_options
@token_required
def cancelar_boleto(token_data, codigo_solicitacao):
  print("codigo_solicitacao", codigo_solicitacao)

  scopes = token_data.get('scopes', [])
  print("token_data", token_data)

  if 'boleto-cobranca.write' not in scopes:
    return jsonify({"erro": "Permissao necessaria: boleto-cobranca.write"}), 403

  token = obter_token(scopes)
  if not token:
    return jsonify({"erro": "Falha ao obter o token de acesso"}), 401

  motivo = request.json.get("motivo", "Cancelamento solicitado pelo cliente")
  cancelamento = cancelar_cobranca(token, codigo_solicitacao, motivo)
  if not cancelamento:
    return jsonify({"erro": "Erro ao cancelar cobranca"}), 404

  return jsonify({
    "status": "sucesso",
    "mensagem": "cobranca cancelada com sucesso"
  }), 202



if __name__ == "__main__":
  app.register_blueprint(boletos)
  app.run(port=5000, debug=True)
