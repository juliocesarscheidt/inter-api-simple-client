
def buscar_empresas(cursor, limit=100):
  try:
    cursor.execute("SELECT id_empresa, nome, cpf_cnpj, tipo_pessoa, telefone, endereco, cidade, uf, cep FROM empresa LIMIT %s", [limit])
    clientes = cursor.fetchall()
    if not clientes:
      return []
    return list(clientes)
  except Exception as e:
    print(e)
    print("Erro ao acessar o banco de dados")
    return []

def buscar_empresa_por_cpf_cnpj(cursor, cpf_cnpj):
  try:
    cursor.execute("SELECT id_empresa, nome, cpf_cnpj, tipo_pessoa, telefone, endereco, cidade, uf, cep FROM empresa WHERE cpf_cnpj = %s LIMIT 1", [cpf_cnpj])
    cliente = cursor.fetchone()
    if not cliente:
      return None
    return cliente
  except Exception as e:
    print(e)
    print("Erro ao acessar o banco de dados")
    return None
