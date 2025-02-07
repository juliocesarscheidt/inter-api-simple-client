import Vue from 'vue';
import Router from 'vue-router';

import Home from './components/pages/Home';
import NotFound from './components/pages/NotFound';

Vue.use(Router);

export default new Router({
  mode: 'hash',
  routes: [
    { path: '/', name: 'Home', component: Home },
    { path: '/not-found', name: 'NotFound', component: NotFound, alias: ['/not-found'] },
    { path: '*', name: 'Default', redirect: { name: 'NotFound' } },
  ],
});
