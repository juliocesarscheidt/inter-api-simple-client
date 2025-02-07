import Vue from 'vue';
import VueI18n from 'vue-i18n';

import App from './App.vue';
import router from './router';
import store from './store/store';
import { currency } from './filters/filters';
import locales from './utils/translations/index.js';

import './plugins/bootstrap';
import './plugins/notification';
import './plugins/typed';
import './plugins/i18n';

Vue.config.productionTip = false;
Vue.filter('currency', currency);

const i18n = new VueI18n({ locale: 'pt-br', messages: locales });

new Vue({
  router,
  store,
  i18n,
	render: h => h(App),
}).$mount('#app');
