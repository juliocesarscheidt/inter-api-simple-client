<template>
  <main id="app">
    <Header/>
    <b-container>
      <transition name="slide" mode="out-in">
        <router-view></router-view>
      </transition>
      <notifications position="top right" group="notification" class="my-4 mx-4"/>
    </b-container>
    <Footer/>
  </main>
</template>

<script>
import { mapState, mapActions } from 'vuex';

import Header from './components/Header'
import Footer from './components/Footer'

export default {
  components: {
    Header,
    Footer
  },
  computed: {
    ...mapState([]),
  },
  watch: {
  },
  data() {
    return {
    }
  },
  mounted() {
  },
  methods: {
    ...mapActions([]),
  }
}
</script>

<style>
#app {
  width: auto;
  height: 100vh;
  background-color: #fff;
  font-style: normal;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.navbar  {
  background-color: #efefef;
}

.cookies-modal .modal-content {
  position: absolute !important;
  bottom: 0px !important;
}

.cookies-policy-button {
  cursor: pointer;
}

.font-bold {
  font-weight: bold;
}

@keyframes slide-in {
  from {
    transform: translateX(-25px);
    opacity: 0;
  }
  to {
    transform: translateX(0px);
    opacity: 1;
  }
}

@keyframes slide-out {
  from {
    transform: translateX(0px);
    opacity: 1;
  }
  to {
    transform: translateX(+25px);
    opacity: 0;
  }
}

@keyframes slide-up {
  from {
    transform: translateY(+50px);
    opacity: 0;
  }
  to {
    transform: translateY(0px);
    opacity: 1;
  }
}

@keyframes slide-down {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0px);
    opacity: 1;
  }
}

.justify-content-60 {
  width: 60%;
  text-align: justify;
}

.slide-enter-active {
  animation: slide-in 0.25s ease;
}

.slide-leave-active {
  animation: slide-out 0.25s ease;
}

.full-height {
  height: 100%;
  width: auto;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
  background-color: #eff2f5;
  padding: 5px;
}

.flex {
  display: flex;
}

.flex-justify-center {
  justify-content: center;
}

.flex-justify-start {
  justify-content: flex-start;
}

.flex-justify-end {
  justify-content: flex-end;
}

.flex-align-center {
  align-items: center;
}

.flex-align-start {
  align-items: flex-start;
}

.flex-align-end {
  align-items: flex-end;
}

.flex-space-between {
  justify-content: space-between;
}

.flex-space-around {
  justify-content: space-around;
}

.flex-start {
  justify-content: flex-start;
}

.flex-end {
  justify-content: flex-end;
}

.flex-row {
  flex-direction: row;
}

.flex-column {
  flex-direction: column;
}

@media only screen and (max-width: 991px) {
  .justify-content-60 {
    width: 100%;
  }
}
</style>

