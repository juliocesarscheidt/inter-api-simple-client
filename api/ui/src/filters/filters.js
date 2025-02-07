const currency = value => `R$ ${parseFloat(value).toFixed(2).toLocaleString()}`

export {
  currency
}
