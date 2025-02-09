<template>
  <div class="row justify-content-center">
    <div class="col-md-8">
      <div class="card">
        <div class="card-header">
          <h3 class="text-center">Register</h3>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <form @submit.prevent="handleSubmit">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="username" class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  id="username" 
                  v-model="formData.username" 
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label for="password" class="form-label">Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password" 
                  v-model="formData.password" 
                  required
                >
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="full_name" class="form-label">Full Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="full_name" 
                  v-model="formData.full_name" 
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label for="qualification" class="form-label">Qualification</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="qualification" 
                  v-model="formData.qualification" 
                  required
                >
              </div>
            </div>
            <div class="mb-3">
              <label for="dob" class="form-label">Date of Birth</label>
              <input 
                type="date" 
                class="form-control" 
                id="dob" 
                v-model="formData.dob" 
                required
              >
            </div>
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Registering...' : 'Register' }}
              </button>
            </div>
          </form>
          <div class="text-center mt-3">
            <router-link to="/login">Already have an account? Login here</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import userMixin from '../mixins/userMixin'

export default {
  name: 'RegistrationPage',
  mixins: [userMixin],
  data() {
    return {
      formData: {
        username: '',
        password: '',
        full_name: '',
        qualification: '',
        dob: ''
      },
      error: null,
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      this.loading = true
      this.error = null
      
      const result = await this.register(this.formData)
      
      if (result.success) {
        this.$router.push('/login')
      } else {
        this.error = result.error
      }
      
      this.loading = false
    }
  }
}
</script>

<style scoped></style>