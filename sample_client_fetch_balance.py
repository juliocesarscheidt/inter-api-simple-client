import os
from time import time
from datetime import date
from inter_client.client import InterClient

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CERT_PATH = os.environ.get("CERT_PATH")
CERT_KEY_PATH = os.environ.get("CERT_KEY_PATH")
ACCOUNT = os.environ.get("ACCOUNT", None)

if __name__ in "__main__":
    interClient = InterClient(
        CERT_PATH, CERT_KEY_PATH, CLIENT_ID, CLIENT_SECRET, ACCOUNT
    )

    time_now = time()
    yesterday = date.fromtimestamp(time_now - 60 * 60 * 24)
    today = date.fromtimestamp(time_now)
    print(f"yesterday: {yesterday} - today: {today}")

    balance_data = interClient.get_balance(today)
    print(balance_data)

    statements_data = interClient.get_statements(yesterday, today)
    print(statements_data)
