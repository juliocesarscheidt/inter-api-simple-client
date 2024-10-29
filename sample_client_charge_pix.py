import os
import argparse
from inter_client.client import InterClient

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CERT_PATH = os.environ.get("CERT_PATH")
CERT_KEY_PATH = os.environ.get("CERT_KEY_PATH")
ACCOUNT = os.environ.get("ACCOUNT", None)

def get_argument_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('--receiverkey', type=str, required=True, help='PIX receiver key',)
  parser.add_argument('--amount', type=str, required=True, help='PIX amount',)
  parser.add_argument('--description', type=str, required=False, help='PIX description', default='PIX')
  parser.add_argument('--debtorname', type=str, required=False, help='PIX debtor name', default=None)
  parser.add_argument('--debtorcnpj', type=str, required=False, help='PIX debtor cnpj', default=None)
  parser.add_argument('--debtorcpf', type=str, required=False, help='PIX debtor cpf', default=None)
  return parser.parse_args()

if __name__ in "__main__":
  args = get_argument_parser()
  interClient = InterClient(CERT_PATH, CERT_KEY_PATH, CLIENT_ID, CLIENT_SECRET, ACCOUNT)

  debtor = None
  if args.debtorname:
    debtor = {
      'nome': args.debtorname,
    }
    if args.debtorcnpj is not None:
      debtor['cnpj'] = args.debtorcnpj
    elif args.debtorcpf is not None:
      debtor['cpf'] = args.debtorcpf

  pix_charge = interClient.send_pix_charge(args.receiverkey, args.amount, args.description, debtor)
  print(pix_charge)

  txid = pix_charge.get('txid')
  pix_charge_status = interClient.get_pix_charge(txid)
  print(pix_charge_status)

  print("location", pix_charge_status.get("location"))
  print("pixCopiaECola", pix_charge_status.get("pixCopiaECola"))
