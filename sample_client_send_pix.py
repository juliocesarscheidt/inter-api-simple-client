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
    parser.add_argument(
        "--receiverkey",
        type=str,
        required=True,
        help="PIX receiver key",
    )
    parser.add_argument(
        "--amount",
        type=str,
        required=True,
        help="PIX amount",
    )
    parser.add_argument(
        "--description", type=str, required=False, help="PIX description", default="PIX"
    )
    return parser.parse_args()


if __name__ in "__main__":
    args = get_argument_parser()
    interClient = InterClient(
        CERT_PATH, CERT_KEY_PATH, CLIENT_ID, CLIENT_SECRET, ACCOUNT
    )

    pix_payment = interClient.send_pix_payment(
        args.receiverkey, args.amount, args.description
    )
    print(pix_payment)

    pix_codigo = pix_payment.get("codigoSolicitacao")
    pix_payment_status = interClient.get_pix_payment(pix_codigo)
    print(pix_payment_status)
