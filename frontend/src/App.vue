<script>
import userMixin from './mixins/userMixin'

export default {
  name: 'App',
  mixins: [userMixin],
  created() {
    // Add event listener for storage changes
    window.addEventListener('storage', this.handleStorageChange)
  },
  beforeUnmount() {
    // Remove event listener
    window.removeEventListener('storage', this.handleStorageChange)
  },
  methods: {
    logout() {
      this.handleLogout()
    },
    handleStorageChange(event) {
      // Handle token removal in other tabs
      if (event.key === 'token' && !event.newValue) {
        this.isLoggedIn = false
        this.isAdmin = false
        if (this.$route.meta.requiresAuth) {
          this.$router.push('/login')
        }
      }
    }
  }
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <i class="fas fa-graduation-cap me-2"></i>
        Quiz Master
      </router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <template v-if="isLoggedIn && isAdmin">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard">
                <i class="fas fa-tachometer-alt me-1"></i> Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/subjects">
                <i class="fas fa-book me-1"></i> Manage Subjects
              </router-link>
            </li>
          </template>
          <template v-if="isLoggedIn && !isAdmin">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">
                <i class="fas fa-tachometer-alt me-1"></i> Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/quizzes">
                <i class="fas fa-tasks me-1"></i> Available Quizzes
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/my-scores">
                <i class="fas fa-chart-bar me-1"></i> My Scores
              </router-link>
            </li>
          </template>
        </ul>
        <ul class="navbar-nav">
          <template v-if="!isLoggedIn">
            <li class="nav-item">
              <router-link class="nav-link" to="/login">
                <i class="fas fa-sign-in-alt me-1"></i> Login
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">
                <i class="fas fa-user-plus me-1"></i> Register
              </router-link>
            </li>
          </template>
          <li class="nav-item" v-else>
            <a class="nav-link" href="#" @click.prevent="logout">
              <i class="fas fa-sign-out-alt me-1"></i> Logout
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <main class="container py-4">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>

  <footer class="footer mt-auto py-3 bg-light">
    <div class="container text-center">
      <span class="text-muted">© 2024 Quiz Master. All rights reserved.</span>
    </div>
  </footer>
</template>

<style>
#app {
  font-family: 'Poppins', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

.navbar {
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.navbar-brand {
  font-size: 1.5rem;
  font-weight: 600;
}

.nav-link {
  font-weight: 500;
  padding: 0.5rem 1rem;
  transition: all 0.3s ease;
}

.nav-link:hover {
  transform: translateY(-1px);
}

.router-link-active {
  font-weight: 600;
  position: relative;
}

.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 1rem;
  right: 1rem;
  height: 2px;
  background-color: currentColor;
  border-radius: 2px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Add responsive padding */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
