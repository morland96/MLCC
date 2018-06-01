import Vue from 'vue'
import Router from 'vue-router'
import store from '../store'
import axios from '../http'
const Main = () => import('@/components/Main')
const Login = () => import('@/components/Login')
const routes = [
  {
    path: '/',
    component: Main,
    redirect: '/home',
    meta: { requireAuth: true },
    children: [
      {
        path: 'home',
        name: 'home',
        meta: { requireAuth: true },
        component: () => import('@/components/pages/home.vue')
      },
      {
        path: 'data-sets',
        name: 'data-sets',
        meta: { requireAuth: true },
        component: () => import('@/components/pages/data-sets.vue')
      },
      {
        path: 'scripts',
        name: 'scripts',
        meta: { requireAuth: true },
        component: () => import('@/components/pages/scripts.vue')
      },
      {
        path: 'works',
        name: 'works',
        meta: { requireAuth: true },
        component: () => import('@/components/pages/works.vue')
      }
    ]
  },
  { path: '/login', component: Login }
]
Vue.use(Router)

const router = new Router({
  routes,
  mode: 'history'
})
router.beforeEach((to, form, next) => {
  if (to.meta.requireAuth) {
    if (store.getters.token) {
      axios.get('/api/user').then(function (response) {
        store.commit('updateInfo', response.data)
        if (to.meta.requireAdmin) {
          if (store.state.UserInfo.user.privilege !== '1') {
            router.push('/')
          }
        }
      })
      next()
    } else {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  } else {
    // 路由部分

    next()
  }
})
export default router
