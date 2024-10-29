# Inter Banking simple client for Python

A simple client using some endpoints from Inter Banking API.

## Install requirements

```bash
pip install -r requirements.txt
```

## Setup environment variables for the client

```bash
export CLIENT_ID="" # Inter integration client id
export CLIENT_SECRET="" # Inter integration client secret
export CERT_PATH="" # Inter integration certificate (.crt) path
export CERT_KEY_PATH="" # Inter integration key (.key) path
export ACCOUNT="" # Inter account - required if there are multiple accounts
```

## Running sample clients

```bash
python sample_client_fetch_balance.py

python sample_client_send_pix.py \
  --receiverkey "<ALGUMA_CHAVE_PIX>" \
  --amount "<VALOR_PIX>" \
  --description "<DESCRICAO_PIX>"

python sample_client_charge_pix.py \
  --receiverkey "<ALGUMA_CHAVE_PIX>" \
  --amount "<VALOR_PIX>" \
  --description "<DESCRICAO_PIX>" \
  --debtorname "<NOME_DEVEDOR>" \
  --debtorcpf "<CPF_DEVEDOR>"
```

Implemented endpoints:

- [Fetch balance](https://developers.inter.co/references/banking#tag/Saldo/operation/Saldo)

- [Fetch statements](https://developers.inter.co/references/banking#tag/Extrato/operation/Extrato)

- [Pay with PIX](https://developers.inter.co/references/banking#tag/Pix-Pagamento/operation/realizarPagamentoPix)

- [Fetch PIX payment](https://developers.inter.co/references/banking#tag/Pix-Pagamento/operation/consultarPagamentoPix)

- [Charge with PIX](https://developers.inter.co/references/pix#tag/Cobranca-Imediata/paths/~1cob~1%7Btxid%7D/put)

- [Fetch PIX charge](https://developers.inter.co/references/pix#tag/Cobranca-Imediata/paths/~1cob~1%7Btxid%7D/get)
