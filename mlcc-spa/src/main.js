// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import iView from 'iview'
import store from './store'
import axios from './http'
import Prism from 'prismjs'
import loadLanguages from 'prismjs/components/index.js'
import 'iview/dist/styles/iview.css'

Vue.use(iView)
Vue.config.productionTip = false
Vue.prototype.axios = axios
loadLanguages(['python'])
Vue.prototype.Prism = Prism
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  store,
  template: '<App/>'
})
