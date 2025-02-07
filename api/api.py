import uuid
import hashlib
from functools import wraps
from base64 import b64decode
from datetime import datetime, timedelta
from flask import Flask, Blueprint, jsonify, request, Response
from flask_mysqldb import MySQL
from flask_cors import CORS
from data import fetch_company_by_uuid, insert_charge, fetch_charge_by_uuid, update_charge
from inter import emitir_cobranca, obter_cobranca, obter_cobranca_pdf, cancelar_cobranca, obter_token


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
  uuid varchar(36) primary key,
  nome varchar(255) not null,
  cpf_cnpj varchar(50) not null,
  tipo_pessoa varchar(50) not null,
  telefone varchar(50) not null,
  endereco varchar(255) not null,
  cidade varchar(255) not null,
  uf varchar(10) not null,
  cep varchar(10) not null,
  created_at timestamp default current_timestamp,
  updated_at timestamp default current_timestamp on update current_timestamp,
  deleted_at timestamp null,
  UNIQUE (cpf_cnpj)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- exemple de insert:
insert into boletos.empresa
  (uuid, nome, cpf_cnpj, tipo_pessoa, telefone, endereco, cidade, uf, cep)
values
  ('bd65600d-8669-4903-8a14-af88203add38', 'Blackdevs', '31335134000197', 'JURIDICA', '999999999', 'R. Teste 1234', 'Curitiba', 'PR', '81000000');


create table boletos.cobranca (
  uuid varchar(36) primary key,
  uuid_empresa varchar(36) not null,
  valor_servico int not null,
  data_vencimento date not null,
  status enum('ATIVO', 'CANCELADO') not null,
  codigo_solicitacao varchar(36) not null,
  codigo_barras varchar(255) null,
  linha_digitavel varchar(255) null,
  pix_copia_e_cola varchar(255) null,
  pdf_base64 text null,
  created_at timestamp default current_timestamp,
  updated_at timestamp default current_timestamp on update current_timestamp,
  deleted_at timestamp null,
  FOREIGN KEY (uuid_empresa) REFERENCES empresa(uuid),
  UNIQUE (codigo_solicitacao)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

"""

mysql = MySQL(app)


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
    # TODO: implementar validacao do token JWT
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


@boletos.route('/', methods=['POST', 'OPTIONS'])
@intercept_options
@token_required
def gerar_boletos(token_data):
  payload = request.json
  print("payload", payload)

  valor_servico = float(payload["valor_servico"]) if "valor_servico" in payload else None
  uuid_empresa = payload["uuid_empresa"] if "uuid_empresa" in payload else None
  # TODO: validar valor_servico e uuid_empresa
  if valor_servico is None or uuid_empresa is None:
    return jsonify({"erro": "Necessario informar os parametros: valor_servico, uuid_empresa"}), 400

  scopes = token_data.get('scopes', [])
  print("token_data", token_data)

  if 'boleto-cobranca.write' not in scopes:
    return jsonify({"erro": "Permissao necessaria: boleto-cobranca.write"}), 403

  token = obter_token(scopes)
  if not token:
    return jsonify({"erro": "Falha ao obter o token de acesso"}), 401

  hoje = datetime.now()
  if hoje.day > 30:
    return jsonify({"erro": "Boletos so podem ser gerados ate o dia 30 de cada mes"}), 403

  empresa = fetch_company_by_uuid(mysql.connection, uuid_empresa)
  print("empresa", empresa)
  if empresa is None:
    return jsonify({"erro": "Cliente nao encontrado"}), 404

  uuid_cobranca = str(uuid.uuid4())
  print("uuid_cobranca", uuid_cobranca)

  vencimento = (hoje + timedelta(days=7)).strftime("%Y-%m-%d")
  print("vencimento", vencimento)

  uuid_cobranca_hash = hashlib.sha1(uuid_cobranca.encode("UTF-8")).hexdigest()
  print("uuid_cobranca_hash", uuid_cobranca_hash)

  cobranca_payload = {
    "seuNumero": uuid_cobranca_hash[:15], # pode ter ate 15 caracteres
    "valorNominal": str(valor_servico),
    "dataVencimento": vencimento,
    "numDiasAgenda": 0,
    "pagador": {
      "cpfCnpj": empresa["cpf_cnpj"],
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

  cobranca = emitir_cobranca(token, cobranca_payload)
  codigo_solicitacao = cobranca.get("codigoSolicitacao") if cobranca else None
  print("codigo_solicitacao", codigo_solicitacao)

  if codigo_solicitacao is None:
    return jsonify({"erro": "Erro ao emitir cobranca"}), 500

  # salvar cobranca no banco de dados
  charge = {
    "uuid": uuid_cobranca,
    "uuid_empresa": uuid_empresa,
    "valor_servico": int((valor_servico * 100)), # armazenado em centavos
    "data_vencimento": vencimento,
    "status": "ATIVO",
    "codigo_solicitacao": codigo_solicitacao,
  }
  if not insert_charge(mysql.connection, charge):
    return jsonify({"erro": "Erro ao salvar cobranca"}), 500

  return jsonify({
    "uuid_cobranca": uuid_cobranca,
  }), 200


@boletos.route('/<uuid_cobranca>', methods=['GET', 'OPTIONS'])
@intercept_options
@token_required
def recuperar_cobranca(token_data, uuid_cobranca):
  print("uuid_cobranca", uuid_cobranca)
  if not uuid_cobranca or len(uuid_cobranca) != 36:
    return jsonify({"erro": "UUID da cobranca invalido"}), 400

  scopes = token_data.get('scopes', [])
  print("token_data", token_data)

  if 'boleto-cobranca.read' not in scopes:
    return jsonify({"erro": "Permissao necessaria: boleto-cobranca.read"}), 403

  token = obter_token(scopes)
  if not token:
    return jsonify({"erro": "Falha ao obter o token de acesso"}), 401

  try:
    charge = fetch_charge_by_uuid(mysql.connection, uuid_cobranca)
    if charge is None:
      return jsonify({"erro": "Cobranca nao encontrada"}), 404
    if charge["status"] == "CANCELADO":
      return jsonify({"erro": "Cobranca ja esta cancelada"}), 422

    if charge["codigo_barras"] is not None or \
      charge["linha_digitavel"] is not None or \
      charge["pix_copia_e_cola"] is not None:
      return jsonify({
        "codigo_solicitacao": charge["codigo_solicitacao"],
        "codigo_barras": charge["codigo_barras"],
        "linha_digitavel": charge["linha_digitavel"],
        "pix_copia_e_cola": charge["pix_copia_e_cola"],
      }), 200

    codigo_solicitacao = charge["codigo_solicitacao"]
    print("codigo_solicitacao", codigo_solicitacao)

    cobranca = obter_cobranca(token, codigo_solicitacao)
    print("cobranca", cobranca)
    if cobranca is None:
      return jsonify({"erro": "Erro ao obter PDF"}), 404

    codigo_barras = cobranca.get("boleto").get("codigoBarras")
    linha_digitavel = cobranca.get("boleto").get("linhaDigitavel")
    pix_copia_e_cola = cobranca.get("pix").get("pixCopiaECola")

    update_charge(mysql.connection, uuid_cobranca, {
      "codigo_barras": codigo_barras,
      "linha_digitavel": linha_digitavel,
      "pix_copia_e_cola": pix_copia_e_cola,
    })

    return jsonify({
      "codigo_solicitacao": codigo_solicitacao,
      "codigo_barras": codigo_barras,
      "linha_digitavel": linha_digitavel,
      "pix_copia_e_cola": pix_copia_e_cola,
    }), 200

  except Exception as e:
    print(e)
    return jsonify({"erro": f"Erro ao recuperar cobranca"}), 500


@boletos.route('/<uuid_cobranca>/pdf', methods=['GET', 'OPTIONS'])
@intercept_options
@token_required
def recuperar_boleto(token_data, uuid_cobranca):
  print("uuid_cobranca", uuid_cobranca)
  if not uuid_cobranca or len(uuid_cobranca) != 36:
    return jsonify({"erro": "UUID da cobranca invalido"}), 400

  scopes = token_data.get('scopes', [])
  print("token_data", token_data)

  if 'boleto-cobranca.read' not in scopes:
    return jsonify({"erro": "Permissao necessaria: boleto-cobranca.read"}), 403

  token = obter_token(scopes)
  if not token:
    return jsonify({"erro": "Falha ao obter o token de acesso"}), 401

  try:
    charge = fetch_charge_by_uuid(mysql.connection, uuid_cobranca)
    if charge is None:
      return jsonify({"erro": "Cobranca nao encontrada"}), 404
    if charge["status"] == "CANCELADO":
      return jsonify({"erro": "Cobranca ja esta cancelada"}), 422

    codigo_solicitacao = charge["codigo_solicitacao"]
    print("codigo_solicitacao", codigo_solicitacao)

    if charge["pdf_base64"] is not None:
      pdf_content_bytes = b64decode(charge["pdf_base64"], validate=True)
    else:
      cobranca_pdf = obter_cobranca_pdf(token, codigo_solicitacao)
      if cobranca_pdf is None:
        return jsonify({"erro": "Erro ao obter PDF"}), 404

      pdf_content_base64 = cobranca_pdf["pdf"]
      update_charge(mysql.connection, uuid_cobranca, {
        "pdf_base64": pdf_content_base64,
      })

      pdf_content_bytes = b64decode(pdf_content_base64, validate=True)

    return Response(pdf_content_bytes,
                    mimetype='application/pdf',
                    headers={
                      "Content-Disposition": "inline; filename=boleto.pdf",
                      "Content-Type": "application/pdf",
                      "Content-Length": len(pdf_content_bytes)
                    })

  except Exception as e:
    print(e)
    return jsonify({"erro": f"Erro ao recuperar cobranca"}), 500


@boletos.route('/<uuid_cobranca>/cancelar', methods=['PUT', 'OPTIONS'])
@intercept_options
@token_required
def cancelar_boleto(token_data, uuid_cobranca):
  print("uuid_cobranca", uuid_cobranca)
  if not uuid_cobranca or len(uuid_cobranca) != 36:
    return jsonify({"erro": "UUID da cobranca invalido"}), 400

  scopes = token_data.get('scopes', [])
  print("token_data", token_data)

  if 'boleto-cobranca.write' not in scopes:
    return jsonify({"erro": "Permissao necessaria: boleto-cobranca.write"}), 403

  token = obter_token(scopes)
  if not token:
    return jsonify({"erro": "Falha ao obter o token de acesso"}), 401

  try:
    charge = fetch_charge_by_uuid(mysql.connection, uuid_cobranca)
    if charge is None:
      return jsonify({"erro": "Cobranca nao encontrada"}), 404
    if charge["status"] == "CANCELADO":
      return jsonify({"erro": "Cobranca ja esta cancelada"}), 422

    codigo_solicitacao = charge["codigo_solicitacao"]
    print("codigo_solicitacao", codigo_solicitacao)

    motivo = request.json.get("motivo", "Cancelamento solicitado pelo cliente")
    if not cancelar_cobranca(token, codigo_solicitacao, motivo):
      return jsonify({"erro": "Erro ao cancelar cobranca"}), 404

    update_charge(mysql.connection, uuid_cobranca, {
      "status": "CANCELADO",
    })

    return jsonify({
      "mensagem": "Cobranca cancelada com sucesso"
    }), 202

  except Exception as e:
    print(e)
    return jsonify({"erro": f"Erro ao cancelar cobranca"}), 500



if __name__ == "__main__":
  app.register_blueprint(boletos)
  app.run(port=5000, debug=True)
