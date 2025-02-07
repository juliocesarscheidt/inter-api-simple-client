const axios = require('axios');

const apiBaseURL = 'http://localhost:5000';

const axiosClient = axios.create({
  baseURL: apiBaseURL,
  timeout: 10000,
});

const getCobrancaPDF = async (codigoSolicitacao) => {
  const url = `/v1/boletos/${codigoSolicitacao}/pdf`;
  const headers = {
    'Authorization': 'Bearer <TOKEN_DA_API_E_NAO_DO_INTER>',
    'Content-Type': 'application/json',
  };
  const response = await axiosClient.get(url, { headers, responseType: 'blob' });
  return response;
}

const getCobranca = async (codigoSolicitacao) => {
  const url = `/v1/boletos/${codigoSolicitacao}`;
  const headers = {
    'Authorization': 'Bearer <TOKEN_DA_API_E_NAO_DO_INTER>',
    'Content-Type': 'application/json',
  };
  const response = await axiosClient.get(url, { headers });
  return response;
}

const cancelCobranca = async (codigoSolicitacao) => {
  const url = `/v1/boletos/${codigoSolicitacao}/cancelar`;
  const headers = {
    'Authorization': 'Bearer <TOKEN_DA_API_E_NAO_DO_INTER>',
    'Content-Type': 'application/json',
  };
  await axiosClient.put(url, {
    motivo: 'Cancelamento solicitado pelo cliente',
  }, { headers });
}

export {
  getCobrancaPDF,
  getCobranca,
  cancelCobranca,
}
