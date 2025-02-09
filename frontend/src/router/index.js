import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegistrationPage from '../views/RegistrationPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import CreateCampaign from '@/views/CreateCampaign.vue'
import EditCampiagn from '@/views/EditCampiagn.vue'
import MyCampaigns from '@/views/MyCampaigns.vue'
import InfluencerDashboard from '@/views/InfluencerDashboard.vue'
import NegotiationPage from '@/views/NegotiationPage.vue'

const routes = [
  {
    path: '/',
    redirect: to => {
      const token = localStorage.getItem('token')
      const userRole = localStorage.getItem('userRole')
      if (!token) return '/login'
      return userRole === 'admin' ? '/admin/dashboard' : '/dashboard'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginPage.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegistrationPage.vue')
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/dashboard',
    name: 'UserDashboard',
    component: () => import('../views/user/UserDashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/subjects',
    name: 'ManageSubjects',
    component: () => import('../views/admin/SubjectsPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects/:subjectId/chapters',
    name: 'ManageChapters',
    component: () => import('../views/admin/ChaptersPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/chapters/:chapterId/quizzes',
    name: 'ManageQuizzes',
    component: () => import('../views/admin/QuizzesPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes/:quizId/questions',
    name: 'ManageQuestions',
    component: () => import('../views/admin/QuestionsPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/quizzes',
    name: 'AvailableQuizzes',
    component: () => import('../views/user/AvailableQuizzes.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/quizzes/:quizId/attempt',
    name: 'AttemptQuiz',
    component: () => import('../views/user/AttemptQuiz.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/my-scores',
    name: 'MyScores',
    component: () => import('../views/user/MyScores.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/create-campaign',
    name: 'createcampaign',
    component: CreateCampaign
  },
  {
    path: '/edit-campaign/:id',
    name: 'editcampaign',
    component: EditCampiagn
  },
  {
    path: '/my-campaigns',
    name: 'mycampaigns',
    component: MyCampaigns
  },
  {
    path: '/influencer-dashboard',
    name: 'influencedashboard',
    component: InfluencerDashboard
  },
  {
    path: '/negotiation/:id',
    name: 'NegotiationPage',
    component: NegotiationPage
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('userRole')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/')
  } else {
    next()
  }
})

export default router
