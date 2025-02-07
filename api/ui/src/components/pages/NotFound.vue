<template>
  <section class="flex flex-column flex-justify-start p-2">
    <article class="flex flex-column flex-justify-center flex-align-center">
      <h1>{{ $t('not_found.title') }}! 404</h1>
      <p>{{ $t('not_found.return') }} <a class="link" href="/">site</a></p>
    </article>
  </section>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    ...mapGetters([]),
  },
  data() {
    return {}
  },
  methods: {},
  beforeDestroy() {}
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

section > article > p {
  font-size: 14px;
}

.link {
  cursor: pointer;
  color: #000;
  font-weight: bold;
}

@media only screen and (max-width: 991px) {
}
</style>