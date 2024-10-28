import json
import time
import requests

INTER_BASE_URL = "https://cdpj.partners.bancointer.com.br"

class InterClient():
  def __init__(self, cert_path, cert_key_path, client_id, client_secret, account, base_url=INTER_BASE_URL):
    self.cert_path = cert_path
    self.cert_key_path = cert_key_path
    self.client_id = client_id
    self.client_secret = client_secret
    self.account = account
    self.base_url = base_url
    self.token_cache = {}

  def make_headers(self, token):
    headers={
      "Authorization": "Bearer " + token,
      "x-conta-corrente": self.account,
      "Content-Type": "Application/json",
    }
    return headers

  def get_token(self, scope):
    if self.token_cache.get(scope):
      cached_token = self.token_cache.get(scope)
      # token is still valid
      if cached_token.get("expires_at") > int(time.time()):
        return cached_token

    attemps, wait_time = 0, 2
    while True:
      try:
        request_string = f"client_id={self.client_id}&client_secret={self.client_secret}&scope={scope}&grant_type=client_credentials"
        response = requests.post(url=f"{self.base_url}/oauth/v2/token",
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            cert=(self.cert_path, self.cert_key_path),
                            data=request_string)
        data_json = response.json()
        token = data_json.get("access_token")
        self.token_cache[scope] = {
          "token": token,
          "expires_at": data_json.get("expires_in") + int(time.time()),
        }
        return token

      except Exception as e:
        if attemps >= 5: raise e
        attemps += 1
        print(f"Error getting token. Retrying in {wait_time} seconds")
        time.sleep(wait_time)
        wait_time = wait_time * 2

  def get_balance(self, search_date):
    token = self.get_token("extrato.read")
    response = requests.get(f"{self.base_url}/banking/v2/saldo",
                        params={"dataSaldo": search_date},
                        headers=self.make_headers(token),
                        cert=(self.cert_path, self.cert_key_path))
    return response.json()

  def create_pix_payment(self, pix_key, pix_amount, pix_description):
    token = self.get_token("pagamento-pix.write")
    request_body = json.dumps({
      "valor": pix_amount,
      "descricao": pix_description,
      "destinatario": {
        "tipo": "CHAVE",
        "chave": pix_key,
      },
    })
    response = requests.post(f"{self.base_url}/banking/v2/pix",
                        headers=self.make_headers(token),
                        cert=(self.cert_path, self.cert_key_path),
                        data=request_body)
    return response.json()

  def get_pix_payment(self, pix_code):
    token = self.get_token("pagamento-pix.read")
    response = requests.get(f"{self.base_url}/banking/v2/pix/{pix_code}",
                        headers=self.make_headers(token),
                        cert=(self.cert_path, self.cert_key_path))
    return response.json()
