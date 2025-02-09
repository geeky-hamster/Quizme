<template>
  <div>
    <h2>Manage Chapters for {{ subjectName }}</h2>
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h4>Add New Chapter</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="name" class="form-label">Chapter Name</label>
                <input type="text" class="form-control" id="name" v-model="newChapter.name" required>
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea class="form-control" id="description" v-model="newChapter.description" rows="3"></textarea>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Adding...' : 'Add Chapter' }}
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
            <h4>Chapter List</h4>
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
                  <tr v-for="chapter in chapters" :key="chapter.id">
                    <td>{{ chapter.name }}</td>
                    <td>{{ chapter.description }}</td>
                    <td>
                      <router-link :to="'/admin/chapters/' + chapter.id + '/quizzes'" class="btn btn-info btn-sm me-2">
                        Manage Quizzes
                      </router-link>
                      <button class="btn btn-danger btn-sm" @click="deleteChapter(chapter.id)">
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
  name: 'ChaptersPage',
  mixins: [userMixin],
  data() {
    return {
      subjectName: '',
      chapters: [],
      newChapter: {
        name: '',
        description: ''
      },
      loading: false,
      error: null
    }
  },
  created() {
    this.fetchSubjectDetails()
    this.fetchChapters()
  },
  methods: {
    async fetchSubjectDetails() {
      try {
        const response = await fetch(`http://localhost:5000/subjects/${this.$route.params.subjectId}`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          const subject = await response.json()
          this.subjectName = subject.name
        }
      } catch (error) {
        console.error('Error:', error)
      }
    },
    async fetchChapters() {
      try {
        const response = await fetch(`http://localhost:5000/subjects/${this.$route.params.subjectId}/chapters`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.chapters = await response.json()
        }
      } catch (error) {
        this.error = 'Failed to fetch chapters'
        console.error('Error:', error)
      }
    },
    async handleSubmit() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch(`http://localhost:5000/subjects/${this.$route.params.subjectId}/chapters`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(this.newChapter)
        })
        
        if (response.ok) {
          await this.fetchChapters()
          this.newChapter.name = ''
          this.newChapter.description = ''
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to add chapter'
        console.error('Error:', error)
      }
      this.loading = false
    },
    async deleteChapter(id) {
      if (!confirm('Are you sure you want to delete this chapter?')) return
      
      try {
        const response = await fetch(`http://localhost:5000/chapters/${id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        if (response.ok) {
          await this.fetchChapters()
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to delete chapter'
        console.error('Error:', error)
      }
    }
  }
}
</script> 