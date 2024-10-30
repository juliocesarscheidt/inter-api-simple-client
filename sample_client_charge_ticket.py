import os
import random
import argparse
from pathlib import Path
from inter_client.client import InterClient
from base64 import b64decode

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CERT_PATH = os.environ.get("CERT_PATH")
CERT_KEY_PATH = os.environ.get("CERT_KEY_PATH")
ACCOUNT = os.environ.get("ACCOUNT", None)

def get_argument_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('--amount', type=float, required=True, help='Ticket amount',)
  parser.add_argument('--duedate', type=str, required=True, help='Ticket due date',)
  parser.add_argument('--expirationdays', type=int, required=True, help='Ticket expiration days',)
  # payer fields
  parser.add_argument('--payercpfcnpj', type=str, required=True, help='Ticket payer CPF or CNPJ',)
  parser.add_argument('--payertype', type=str, required=True, help='Ticket payer type',)
  parser.add_argument('--payername', type=str, required=True, help='Ticket payer name',)
  parser.add_argument('--payeraddress', type=str, required=True, help='Ticket payer address',)
  parser.add_argument('--payercity', type=str, required=True, help='Ticket payer city',)
  parser.add_argument('--payeruf', type=str, required=True, help='Ticket payer UF',)
  parser.add_argument('--payercep', type=str, required=True, help='Ticket payer CEP',)
  return parser.parse_args()

if __name__ in "__main__":
  args = get_argument_parser()
  interClient = InterClient(CERT_PATH, CERT_KEY_PATH, CLIENT_ID, CLIENT_SECRET, ACCOUNT)

  payer = {
    "cpfCnpj": args.payercpfcnpj,
    "tipoPessoa": args.payertype, # FISICA or JURIDICA
    "nome": args.payername,
    "endereco": args.payeraddress,
    "cidade": args.payercity,
    "uf": args.payeruf, # "AC" "AL" "AP" "AM" "BA" "CE" "DF" "ES" "GO" "MA" "MT" "MS" "MG" "PA" "PB" "PR" "PE" "PI" "RJ" "RN" "RS" "RO" "RR" "SC" "SP" "SE" "TO"
    "cep": args.payercep,
  }

  # generate random number with 8 digits
  ticket_number = str(random.randint(10000000, 99999999))
  print("ticket_number", ticket_number)

  charge = interClient.send_charge(ticket_number, args.amount, args.duedate, args.expirationdays, payer)
  print(charge)
  # {'codigoSolicitacao': ''}

  request_code = charge.get('codigoSolicitacao')
  charge_status = interClient.get_charge(request_code)
  print(charge_status)
  print("codigoBarras", charge_status.get("boleto").get("codigoBarras"))
  print("linhaDigitavel", charge_status.get("boleto").get("linhaDigitavel"))
  print("pixCopiaECola", charge_status.get("pix").get("pixCopiaECola"))

  charge_status_pdf = interClient.get_charge_pdf(request_code)
  pdf_content_base64 = charge_status_pdf["pdf"]
  # convert base64 to bytes
  pdf_content_bytes = b64decode(pdf_content_base64, validate=True)

  # save PDF to file
  with open(f"{ticket_number}.pdf", "wb") as pdf_file:
    pdf_file.write(pdf_content_bytes)
  print(f"saved to {ticket_number}.pdf")
