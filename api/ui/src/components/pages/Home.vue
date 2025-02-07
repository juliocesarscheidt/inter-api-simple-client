<template>
  <section class="flex flex-column flex-space-between p-2">
    <article class="flex flex-column flex-justify-center flex-align-start">
      <h1 class="mb-4">Boletos Inter</h1>

      <div class="justify-content-60 article-text">
        <input
          type="text"
          class="form-control"
          v-model="codigoSolicitacao"
          placeholder="Código da solicitação"
        />

        <div class="flex flex-row flex-space-between mt-4">
          <button class="btn btn-outline-primary btn-lg" @click="downloadBoletoPDF">Baixar boleto</button>
          <button class="btn btn-outline-secondary btn-lg" @click="showBoletoCodes">Obter códigos</button>
          <button class="btn btn-outline-danger btn-lg" @click="cancelBoleto">Cancelar boleto</button>
        </div>

        <div class="flex flex-column mt-4">
          <div v-if="codigoBarras" class="flex flex-column flex-space-between mt-4">
            <span><b>Código de barras</b></span>
            <code>{{ codigoBarras }}</code>
          </div>

          <div v-if="linhaDigitavel" class="flex flex-column flex-space-between mt-4">
            <span><b>Linha digitável</b></span>
            <code>{{ linhaDigitavel }}</code>
          </div>

          <div v-if="pixCopiaECola" class="flex flex-column flex-space-between mt-4">
            <span><b>PIX copia e cola</b></span>
            <code>{{ pixCopiaECola }}</code>
          </div>
        </div>
      </div>
    </article>
  </section>
</template>

<script>
import { mapGetters, mapState, mapActions } from 'vuex'
import { getCobrancaPDF, getCobranca, cancelCobranca } from '@/services/api'
import humanFormat from 'human-format'

export default {
  computed: {
    ...mapGetters([]),
    ...mapState([]),
  },
  data() {
    return {
      codigoSolicitacao: '',
      codigoBarras: '',
      linhaDigitavel: '',
      pixCopiaECola: '',
    }
  },
  beforeMount() {
  },
  methods: {
    ...mapActions([]),
    humanFormat,
    async downloadBoletoPDF() {
      if (!this.codigoSolicitacao) {
        return;
      }
      const response = await getCobrancaPDF(this.codigoSolicitacao);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const filename = 'boleto.pdf';

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.click()
      URL.revokeObjectURL(link.href)
    },
    async showBoletoCodes() {
      const response = await getCobranca(this.codigoSolicitacao);
      this.codigoBarras = response.data.codigo_barras;
      this.linhaDigitavel = response.data.linha_digitavel;
      this.pixCopiaECola = response.data.pix_copia_e_cola;
    },
    async cancelBoleto() {
      await cancelCobranca(this.codigoSolicitacao);
    },
  },
  mounted() {
  },
  beforeDestroy() {
  },
}
</script>

<style scoped>
section {
  min-height: calc(100vh - 80px);
  width: auto;
}

section > article {
  height: auto;
  padding: 10px;
}

.main-article {
  flex-direction: row;
  align-items: center;
}

.article-main-text {
  animation: slide-up 1s ease;
}

.article-main-text > p {
  font-size: 3rem;
  font-weight: bold;
  max-width: 200px;
}

.article-main-image {
  max-height: 500px;
  min-height: 400px;
  width: 100%;
}

@media only screen and (max-width: 991px) {
  .main-article {
    flex-direction: column;
    align-items: flex-start;
  }

  .article-main-image {
    max-height: 300px;
    min-height: 100px;
  }
}
</style>