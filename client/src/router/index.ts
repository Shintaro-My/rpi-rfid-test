import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import UserView from '../views/UserView.vue'
import AnonymousView from '../views/AnonymousView.vue'
import BackupView from '../views/BackupView.vue'
import ConfigView from '../views/ConfigView.vue'
import ShutdownView from '../views/ShutdownView.vue'

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
      path: '/config',
      name: 'config',
      component: ConfigView
    },
    {
      path: '/shutdown',
      name: 'shutdown',
      component: ShutdownView
    }
  ]
})

export default router
