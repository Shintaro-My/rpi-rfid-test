import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import UserView from '../views/UserView.vue'
import AnonymousView from '../views/AnonymousView.vue'
import BackupView from '../views/BackupView.vue'
import ShatdownView from '../views/ShatdownView.vue'

const router = createRouter({
  // history: createWebHistory(import.meta.env.BASE_URL),
  history: createWebHashHistory(),
  routes: [
    {
      path: '/users',
      name: 'users',
      component: UserView
    },
    {
      path: '/anonymous',
      name: 'anonymous',
      component: AnonymousView
    },
    {
      path: '/backup',
      name: 'backup',
      component: BackupView
    },
    {
      path: '/shutdown',
      name: 'shutdown',
      component: ShatdownView
    }
  ]
})

export default router
