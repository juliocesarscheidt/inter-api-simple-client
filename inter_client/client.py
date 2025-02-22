import json
import string
import random
import requests
from time import time
from inter_client.decorator import request_retry

INTER_BASE_URL = "https://cdpj.partners.bancointer.com.br"


class InterClient:
    def __init__(
        self,
        cert_path: str,
        cert_key_path: str,
        client_id: str,
        client_secret: str,
        account=None,
        base_url=INTER_BASE_URL,
    ):
        self.cert_path = cert_path
        self.cert_key_path = cert_key_path
        self.client_id = client_id
        self.client_secret = client_secret
        self.account = account
        self.base_url = base_url
        self.token_cache = {}

    def build_headers(self, token: str):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "Application/json",
        }
        if self.account is not None:
            headers["x-conta-corrente"] = self.account
        return headers

    @request_retry
    def get_token(self, scope: str):
        if self.token_cache.get(scope):
            cached_token = self.token_cache.get(scope)
            # token is still valid
            if cached_token.get("expires_at") > int(time()):
                return cached_token["token"]

        request_string = f"client_id={self.client_id}&client_secret={self.client_secret}&scope={scope}&grant_type=client_credentials"
        response = requests.post(
            url=f"{self.base_url}/oauth/v2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            cert=(self.cert_path, self.cert_key_path),
            data=request_string,
        )
        data_json = response.json()
        token = data_json.get("access_token")
        self.token_cache[scope] = {
            "token": token,
            "expires_at": data_json.get("expires_in") + int(time()),
        }
        return token

    @request_retry
    def get_balance(self, search_date: str = None):
        token = self.get_token("extrato.read")
        response = requests.get(
            f"{self.base_url}/banking/v2/saldo",
            params={"dataSaldo": search_date},
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
        )
        return response.json()

    @request_retry
    def get_statements(self, start_date: str, end_date: str):
        token = self.get_token("extrato.read")
        response = requests.get(
            f"{self.base_url}/banking/v2/extrato",
            params={"dataInicio": start_date, "dataFim": end_date},
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
        )
        return response.json()

    @request_retry
    def send_pix_payment_by_key(
        self, pix_receiver_key: str, pix_amount: str, pix_description: str
    ):
        token = self.get_token("pagamento-pix.write")
        request_body = {
            "valor": pix_amount,
            "descricao": pix_description,
            "destinatario": {
                "tipo": "CHAVE",
                "chave": pix_receiver_key,
            },
        }
        response = requests.post(
            f"{self.base_url}/banking/v2/pix",
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
            data=json.dumps(request_body),
        )
        return response.json()

    @request_retry
    def send_pix_payment_by_copy_and_paste_code(
        self, pix_copy_and_paste_code: str, pix_amount: str, pix_description: str
    ):
        token = self.get_token("pagamento-pix.write")
        request_body = {
            "valor": pix_amount,
            "descricao": pix_description,
            "destinatario": {
                "tipo": "PIX_COPIA_E_COLA",
                "pixCopiaECola": pix_copy_and_paste_code,
            },
        }
        response = requests.post(
            f"{self.base_url}/banking/v2/pix",
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
            data=json.dumps(request_body),
        )
        return response.json()


    @request_retry
    def get_pix_payment(self, pix_code: str):
        token = self.get_token("pagamento-pix.read")
        response = requests.get(
            f"{self.base_url}/banking/v2/pix/{pix_code}",
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
        )
        return response.json()

    @request_retry
    def send_pix_charge(
        self,
        pix_receiver_key: str,
        pix_amount: str,
        pix_description: str,
        pix_debtor: dict = None,
        expiration_time: int = 3600,
    ):
        token = self.get_token("cob.write")
        request_body = {
            "calendario": {
                "expiracao": expiration_time,
            },
            "valor": {"original": pix_amount, "modalidadeAlteracao": 1},
            "chave": pix_receiver_key,
            "solicitacaoPagador": pix_description,
        }
        if pix_debtor is not None:
            request_body["devedor"] = pix_debtor

        # generate random string
        txid = "".join(random.choices(string.ascii_letters + string.digits, k=32))
        response = requests.put(
            f"{self.base_url}/pix/v2/cob/{txid}",
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
            data=json.dumps(request_body),
        )
        data = response.json()
        data["txid"] = txid
        return data

    @request_retry
    def get_pix_charge(self, txid):
        token = self.get_token("cob.read")
        response = requests.get(
            f"{self.base_url}/pix/v2/cob/{txid}",
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
        )
        return response.json()

    @request_retry
    def send_charge(
        self,
        ticket_number: str,
        ticket_amount: float,
        due_date: str,
        expiration_days: int,
        ticket_payer: dict,
    ):
        token = self.get_token("boleto-cobranca.write")
        # ticket_payer example
        """
    {
      "cpfCnpj": "<cnpj do pagador>",
      "tipoPessoa": "FISICA",
      "nome": "nome do pagador",
      "endereco": "<endereço do pagador>",
      "cidade": "<cidade do pagador>",
      "uf": "<UF do pagador>",
      "cep": "<CEP do pagador>",
      # optional fields
      "email": "<email do pagador>",
      "ddd": "<DDD do pagador>",
      "telefone": "<telefone do pagador>",
      "numero": "<numero no endereço do pagador>",
      "complemento": "Casa",
      "bairro": "<bairro do pagador>",
    }
    """
        request_body = {
            "seuNumero": ticket_number,
            "valorNominal": ticket_amount,
            "dataVencimento": due_date,
            "numDiasAgenda": expiration_days,
            "pagador": ticket_payer,
            "desconto": None,  # optional, it could be implemented further
            "multa": None,  # optional, it could be implemented further
            "mora": None,  # optional, it could be implemented further
            "mensagem": None,  # optional, it could be implemented further
            "beneficiarioFinal": None,  # optional, it could be implemented further
            "formasRecebimento": ["BOLETO", "PIX"],
        }
        response = requests.post(
            f"{self.base_url}/cobranca/v3/cobrancas",
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
            data=json.dumps(request_body),
        )
        return response.json()

    @request_retry
    def get_charge(self, request_code):
        token = self.get_token("boleto-cobranca.read")
        response = requests.get(
            f"{self.base_url}/cobranca/v3/cobrancas/{request_code}",
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
        )
        return response.json()

    @request_retry
    def get_charge_pdf(self, request_code):
        token = self.get_token("boleto-cobranca.read")
        response = requests.get(
            f"{self.base_url}/cobranca/v3/cobrancas/{request_code}/pdf",
            headers=self.build_headers(token),
            cert=(self.cert_path, self.cert_key_path),
        )
        return response.json()
