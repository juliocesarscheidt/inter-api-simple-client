<template>
  <b-navbar toggleable="lg" type="light">
    <b-container>
      <b-navbar-brand v-bind:to="{name: 'Home'}" class="home-button">
        <img class="home-logo" src="assets/images/blackdevs_logo.png" alt="">
      </b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav right>
        <b-navbar-nav>
          <b-nav-item v-bind:to="{name: 'Home'}">{{ $t('header.home') }}</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-container>
  </b-navbar>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  computed: {
    ...mapGetters([])
  },
  data() {
    return {}
  },
  methods: {
    ...mapActions([]),
  }
}
</script>

<style scoped>
.home-logo {
  width: 80.5px;
  height: 80.5px;
  margin-top: -10px;
  margin-bottom: -10px;
  transition: 0.25s linear;
}

.home-logo:hover {
  opacity: 0.8;
}
</style>