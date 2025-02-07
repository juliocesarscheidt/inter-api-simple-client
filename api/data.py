def fetch_companies(conn, limit=100):
  try:
    cursor = conn.cursor()
    cursor.execute("""
                  SELECT
                  uuid, nome, cpf_cnpj, tipo_pessoa, telefone, endereco, cidade, uf, cep
                  FROM empresa
                  ORDER BY uuid DESC
                  LIMIT %s
                  """, [limit])
    companies = cursor.fetchall()
    if not companies:
      return []
    return list(companies)
  except Exception as e:
    print(e)
    print("Erro ao acessar o banco de dados")
    return []

def fetch_company_by_uuid(conn, uuid):
  try:
    cursor = conn.cursor()
    cursor.execute("""
                  SELECT
                  uuid, nome, cpf_cnpj, tipo_pessoa, telefone, endereco, cidade, uf, cep
                  FROM empresa
                  WHERE uuid = %s
                  LIMIT 1
                  """, [uuid])
    company = cursor.fetchone()
    if not company:
      return None
    return company
  except Exception as e:
    print(e)
    print("Erro ao acessar o banco de dados")
    return None

def fetch_charge_by_codigo_solicitacao(conn, codigo_solicitacao):
  try:
    cursor = conn.cursor()
    cursor.execute("""
                  SELECT
                  uuid, uuid_empresa, valor_servico, data_vencimento, status, codigo_solicitacao, codigo_barras, linha_digitavel, pix_copia_e_cola, pdf_base64
                  FROM cobranca
                  WHERE codigo_solicitacao = %s AND status = "ATIVO" LIMIT 1
                  """, [codigo_solicitacao])
    charge = cursor.fetchone()
    if not charge:
      return None
    return charge
  except Exception as e:
    print(e)
    print("Erro ao acessar o banco de dados")
    return None

def fetch_charge_by_uuid(conn, uuid):
  try:
    cursor = conn.cursor()
    cursor.execute("""
                  SELECT
                  uuid, uuid_empresa, valor_servico, data_vencimento, status, codigo_solicitacao, codigo_barras, linha_digitavel, pix_copia_e_cola, pdf_base64
                  FROM cobranca
                  WHERE uuid = %s LIMIT 1
                  """, [uuid])
    charge = cursor.fetchone()
    if not charge:
      return None
    return charge
  except Exception as e:
    print(e)
    print("Erro ao acessar o banco de dados")
    return None

def insert_charge(conn, charge_payload):
  try:
    cursor = conn.cursor()
    cursor.execute("""
                  INSERT INTO cobranca
                  (uuid, uuid_empresa, valor_servico, data_vencimento, status, codigo_solicitacao)
                  VALUES
                  (%s, %s, %s, %s, %s, %s)
                  """,
                  [charge_payload['uuid'], charge_payload['uuid_empresa'], charge_payload['valor_servico'],
                    charge_payload['data_vencimento'], charge_payload['status'], charge_payload['codigo_solicitacao']])
    conn.commit()
    return True
  except Exception as e:
    print(e)
    print("Erro ao acessar o banco de dados")
    return False

def update_charge(conn, uuid, charge_payload):
  try:
    if len(charge_payload.items()) == 0:
      return False
    cursor = conn.cursor()
    sql = "UPDATE cobranca SET"
    for key, value in charge_payload.items():
      sql += f" {key} = '{value}',"
    sql = sql[:-1] # Remove a última vírgula
    sql += f" WHERE uuid = '{uuid}'"
    cursor.execute(sql)
    conn.commit()
    return True
  except Exception as e:
    print(e)
    print("Erro ao acessar o banco de dados")
    return False
