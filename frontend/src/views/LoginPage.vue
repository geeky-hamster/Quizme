<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">
          <h3 class="text-center">Login</h3>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="username" class="form-label">Email</label>
              <input 
                type="email" 
                class="form-control" 
                id="username" 
                v-model="username" 
                required
              >
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input 
                type="password" 
                class="form-control" 
                id="password" 
                v-model="password" 
                required
              >
            </div>
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>
            </div>
          </form>
          <div class="text-center mt-3">
            <router-link to="/register">Don't have an account? Register here</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import userMixin from '../mixins/userMixin'

export default {
  name: 'LoginPage',
  mixins: [userMixin],
  data() {
    return {
      username: '',
      password: '',
      error: null,
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      this.loading = true
      this.error = null
      
      const result = await this.login(this.username, this.password)
      
      if (result.success) {
        this.$router.push(this.isAdmin ? '/admin/subjects' : '/quizzes')
      } else {
        this.error = result.error
      }
      
      this.loading = false
    }
  }
}
</script>