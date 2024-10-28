# Inter API simple client for Python

A simple client using some endpoints from Inter Bank.

## Install requirements

```bash
pip install -r requirements.txt
```

## Setup environment variables for the client

```bash
export ACCOUNT="" # Inter account
export CLIENT_ID="" # Inter integration client id
export CLIENT_SECRET="" # Inter integration client secret
export CERT_PATH="" # Inter integration certificate (.crt) path
export CERT_KEY_PATH="" # Inter integration key (.key) path
```

## Running

```bash
python main.py \
  --key "<ALGUMA_CHAVE_PIX>" \
  --amount "<VALOR_PIX>" \
  --description "<DESCRICAO_PIX>"
```

Implemented endpoints:

- [Fetch balance](https://developers.inter.co/references/banking#tag/Saldo/operation/Saldo)

- [Pay with PIX](https://developers.inter.co/references/banking#tag/Pix-Pagamento/operation/realizarPagamentoPix)

- [Fetch PIX payment](https://developers.inter.co/references/banking#tag/Pix-Pagamento/operation/consultarPagamentoPix)
