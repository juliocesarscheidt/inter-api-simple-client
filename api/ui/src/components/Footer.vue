<template>
  <footer class="flex flex-justify-center flex-align-center flex-column">
    <b-container>
      <div class="flex flex-justify-center flex-align-center flex-column">
        <div class="network-wrapper">
          <a title="LinkedIn" target="_blank" class="flex flex-justify-center flex-align-center network-link" href="https://www.linkedin.com/company/blackdevs-ltda">
            <i class="fab fa-linkedin" aria-hidden="true"></i>
          </a>
          <a title="Youtube" target="_blank" class="flex flex-justify-center flex-align-center network-link" href="https://www.youtube.com/@JulioScheidt?sub_confirmation=1">
            <i class="fab fa-youtube" aria-hidden="true"></i>
          </a>
        </div>

        <div class="texts">
          <small>© {{ new Date().getFullYear() }}. Blackdevs Software LTDA - CNPJ: 31.335.134/0001-97</small><br>
          <small><center>{{ $t('footer.info') }}</center></small>
        </div>
      </div>
    </b-container>
  </footer>
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
    openURL(url) {
      window.open(url, '_blank');
    },
  }
}
</script>

<style scoped>
footer {
  background-color: #efefef;
  box-sizing: border-box;
  width: 100%;
  height: 200px;
  color: #000;
  padding: 10px;
}

.link--footer {
  color: #fff;
  text-decoration: none;
  font-size: 16px;
  font-weight: bold;
  margin-left: 10px;
  margin-right: 10px;
  transition: color .35s;
}

.link--footer:hover {
  color: #f22;
}

.texts {
  word-wrap: wrap;
  text-align: justify;
}

.network-wrapper {
  height: 34px;
  width: auto;
  margin-top: 20px;
  margin-bottom: 20px;
}

.network-wrapper i {
  font-size: 22px;
  color: #000;
  font-weight: bold;
  transition: transform .35s, color .35s;
}

.network-link {
  float: left;
  width: 34px;
  height: 34px;
  box-sizing: border-box;
  border-radius: 0.3em;
  text-align: center;
  cursor: pointer;
  transition: background-color .35s, transform .35s;
  text-decoration: none;
}

.network-link:hover {
  transform: rotateZ(90deg);
}

.network-link:hover i {
  transform: rotateZ(-90deg);
  color: #fff;
}

.network-link:nth-child(1):hover {
  background-color: rgba(6, 119, 180, 1);
}

.network-link:nth-child(2):hover {
  background-color: rgb(255, 0, 0, 1);
}

.network-link:nth-child(3):hover {
  background-color: rgba(67, 103, 176, 1);
}

.network-link:nth-child(4):hover {
  background-color: rgba(15, 131, 253, 1);
}
</style>
