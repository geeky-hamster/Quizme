<script>
import userMixin from './mixins/userMixin'

export default {
  name: 'App',
  mixins: [userMixin],
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('userRole')
      this.isLoggedIn = false
      this.isAdmin = false
      this.$router.push('/login')
    }
  }
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/">Quiz Master</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item" v-if="isLoggedIn && isAdmin">
            <router-link class="nav-link" to="/admin/subjects">Manage Subjects</router-link>
          </li>
          <li class="nav-item" v-if="isLoggedIn && !isAdmin">
            <router-link class="nav-link" to="/quizzes">Available Quizzes</router-link>
          </li>
          <li class="nav-item" v-if="isLoggedIn && !isAdmin">
            <router-link class="nav-link" to="/my-scores">My Scores</router-link>
          </li>
        </ul>
        <ul class="navbar-nav">
          <template v-if="!isLoggedIn">
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">Register</router-link>
            </li>
          </template>
          <li class="nav-item" v-else>
            <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container mt-4">
    <router-view/>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.navbar-nav .router-link-active {
  font-weight: bold;
}
</style>
