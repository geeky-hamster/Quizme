<template>
  <div>
    <h2>Manage Subjects</h2>
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h4>Add New Subject</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="name" class="form-label">Subject Name</label>
                <input type="text" class="form-control" id="name" v-model="newSubject.name" required>
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea class="form-control" id="description" v-model="newSubject.description" rows="3"></textarea>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Adding...' : 'Add Subject' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h4>Subject List</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subject in subjects" :key="subject.id">
                    <td>{{ subject.name }}</td>
                    <td>{{ subject.description }}</td>
                    <td>
                      <router-link :to="'/admin/subjects/' + subject.id + '/chapters'" class="btn btn-info btn-sm me-2">
                        Manage Chapters
                      </router-link>
                      <button class="btn btn-danger btn-sm" @click="deleteSubject(subject.id)">
                        Delete
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import userMixin from '../../mixins/userMixin'

export default {
  name: 'SubjectsPage',
  mixins: [userMixin],
  data() {
    return {
      subjects: [],
      newSubject: {
        name: '',
        description: ''
      },
      loading: false,
      error: null
    }
  },
  created() {
    this.fetchSubjects()
  },
  methods: {
    async fetchSubjects() {
      try {
        const response = await fetch('http://localhost:5000/subjects', {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.subjects = await response.json()
        }
      } catch (error) {
        this.error = 'Failed to fetch subjects'
        console.error('Error:', error)
      }
    },
    async handleSubmit() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('http://localhost:5000/subjects', {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(this.newSubject)
        })
        
        if (response.ok) {
          await this.fetchSubjects()
          this.newSubject.name = ''
          this.newSubject.description = ''
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to add subject'
        console.error('Error:', error)
      }
      this.loading = false
    },
    async deleteSubject(id) {
      if (!confirm('Are you sure you want to delete this subject?')) return
      
      try {
        const response = await fetch(`http://localhost:5000/subjects/${id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        if (response.ok) {
          await this.fetchSubjects()
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to delete subject'
        console.error('Error:', error)
      }
    }
  }
}
</script> 