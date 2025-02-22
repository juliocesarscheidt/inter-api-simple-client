# Inter Banking simple client for Python

A simple client using some endpoints from Inter Banking API.

## Install requirements

```bash
pip install -r requirements.txt
```

## Setup environment variables for the client

```bash
# linux
export CLIENT_ID="" # Inter integration client id
export CLIENT_SECRET="" # Inter integration client secret
export CERT_PATH="" # Inter integration certificate (.crt) path
export CERT_KEY_PATH="" # Inter integration key (.key) path
export ACCOUNT="" # Inter account - required if there are multiple accounts
# windows
set CLIENT_ID=
set CLIENT_SECRET=
set CERT_PATH=
set CERT_KEY_PATH=
set ACCOUNT=
```

## Using client

> Example to send a PIX payment

```python
from inter_client.client import InterClient

interClient = InterClient(CERT_PATH, CERT_KEY_PATH, CLIENT_ID, CLIENT_SECRET, ACCOUNT)

interClient.send_pix_payment_by_key("<ALGUMA_CHAVE_PIX>", "<VALOR_PIX>", "<VALOR_PIX>")
```

## Running sample clients through CLI

```bash
python sample_client_fetch_balance.py

python sample_client_send_pix_by_key.py \
  --receiverkey "<ALGUMA_CHAVE_PIX>" \
  --amount "<VALOR_PIX>" \
  --description "<DESCRICAO_PIX>"

python sample_client_send_pix_by_copy_and_paste_code.py \
  --receivercode "<ALGUMA_CODIGO_COPIA_E_COLA_PIX>" \
  --amount "<VALOR_PIX>" \
  --description "<DESCRICAO_PIX>"

python sample_client_charge_pix.py \
  --receiverkey "<ALGUMA_CHAVE_PIX>" \
  --amount "<VALOR_PIX>" \
  --description "<DESCRICAO_PIX>" \
  --debtorname "<NOME_DEVEDOR>" \
  --debtorcpf "<CPF_DEVEDOR>"

python sample_client_charge_ticket.py \
  --amount <VALOR_BOLETO> \
  --duedate "<DATA_VENCIMENTO_BOLETO>" \
  --expirationdays <DIAS_EXPIRACAO_BOLETO> \
  --payercpfcnpj "<CPF_CNPJ_PAGADOR>" \
  --payertype "<TIPO_PAGADOR>" \
  --payername "<NOME_PAGADOR>" \
  --payeraddress "<ENDERECO_PAGADOR>" \
  --payercity "<CIDADE_PAGADOR>" \
  --payeruf "<UF_PAGADOR>" \
  --payercep "<CEP_PAGADOR>"
```

Implemented endpoints:

> Balance and statements

- [Fetch balance](https://developers.inter.co/references/banking#tag/Saldo/operation/Saldo)

- [Fetch statements](https://developers.inter.co/references/banking#tag/Extrato/operation/Extrato)

> PIX

- [Pay with PIX](https://developers.inter.co/references/banking#tag/Pix-Pagamento/operation/realizarPagamentoPix)

- [Fetch PIX payment](https://developers.inter.co/references/banking#tag/Pix-Pagamento/operation/consultarPagamentoPix)

- [Charge with PIX](https://developers.inter.co/references/pix#tag/Cobranca-Imediata/paths/~1cob~1%7Btxid%7D/put)

- [Fetch PIX charge](https://developers.inter.co/references/pix#tag/Cobranca-Imediata/paths/~1cob~1%7Btxid%7D/get)

> Charge (ticket)

- [Charge](https://developers.inter.co/references/cobranca-bolepix#tag/Cobranca/operation/emitirCobrancaAsync)

- [Fetch charge](https://developers.inter.co/references/cobranca-bolepix#tag/Cobranca/operation/recuperarCobrancaDetalhada)

- [Fetch charge PDF](https://developers.inter.co/references/cobranca-bolepix#tag/Cobranca/operation/obterPdfCobranca)
