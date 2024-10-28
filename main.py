import os
import argparse
from time import time
from datetime import date
from inter_client.client import InterClient

ACCOUNT = os.environ.get("ACCOUNT")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CERT_PATH = os.environ.get("CERT_PATH")
CERT_KEY_PATH = os.environ.get("CERT_KEY_PATH")

def get_argument_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('--key', type=str, required=True, help='PIX receiver key',)
  parser.add_argument('--amount', type=str, required=True, help='PIX amount',)
  parser.add_argument('--description', type=str, required=False, help='PIX description', default='PIX')
  return parser.parse_args()

if __name__ in "__main__":
  args = get_argument_parser()
  interClient = InterClient(CERT_PATH, CERT_KEY_PATH, CLIENT_ID, CLIENT_SECRET, ACCOUNT)

  # search balance for today
  search_date = date.fromtimestamp(time())
  print(search_date)
  balance_data = interClient.get_balance(search_date)
  print(balance_data)

  # pix_payment = interClient.create_pix_payment("<ALGUMA_CHAVE_PIX>", "<VALOR_PIX>", "<DESCRICAO_PIX>")
  pix_payment = interClient.create_pix_payment(args.key, args.amount, args.description)
  print(pix_payment)

  pix_codigo = pix_payment.get('codigoSolicitacao')
  pix_payment_status = interClient.get_pix_payment(pix_codigo)
  print(pix_payment_status)
