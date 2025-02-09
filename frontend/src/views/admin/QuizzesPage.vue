<template>
  <div>
    <h2>Manage Quizzes for {{ chapterName }}</h2>
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h4>Add New Quiz</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="title" class="form-label">Quiz Title</label>
                  <input type="text" class="form-control" id="title" v-model="newQuiz.title" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="time_duration" class="form-label">Duration (minutes)</label>
                  <input type="number" class="form-control" id="time_duration" v-model="newQuiz.time_duration" required min="1">
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="start_date" class="form-label">Start Date & Time</label>
                  <input type="datetime-local" class="form-control" id="start_date" v-model="newQuiz.start_date" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="end_date" class="form-label">End Date & Time</label>
                  <input type="datetime-local" class="form-control" id="end_date" v-model="newQuiz.end_date" required>
                </div>
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea class="form-control" id="description" v-model="newQuiz.description" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label for="status" class="form-label">Status</label>
                <select class="form-select" id="status" v-model="newQuiz.status" required>
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                </select>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Adding...' : 'Add Quiz' }}
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
            <h4>Quiz List</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Duration</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="quiz in quizzes" :key="quiz.id">
                    <td>{{ quiz.title }}</td>
                    <td>{{ quiz.time_duration }} minutes</td>
                    <td>{{ formatDateTime(quiz.start_date) }}</td>
                    <td>{{ formatDateTime(quiz.end_date) }}</td>
                    <td>
                      <span :class="getStatusBadgeClass(quiz)">{{ quiz.status }}</span>
                    </td>
                    <td>
                      <router-link :to="'/admin/quizzes/' + quiz.id + '/questions'" class="btn btn-info btn-sm me-2">
                        Manage Questions
                      </router-link>
                      <button class="btn btn-danger btn-sm" @click="deleteQuiz(quiz.id)">
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
  name: 'QuizzesPage',
  mixins: [userMixin],
  data() {
    return {
      chapterName: '',
      quizzes: [],
      newQuiz: {
        title: '',
        description: '',
        start_date: '',
        end_date: '',
        time_duration: 30,
        status: 'draft'
      },
      loading: false,
      error: null
    }
  },
  created() {
    this.fetchChapterDetails()
    this.fetchQuizzes()
  },
  methods: {
    formatDateTime(dateStr) {
      return new Date(dateStr).toLocaleString()
    },
    getStatusBadgeClass(quiz) {
      const classes = 'badge '
      if (quiz.is_active) return classes + 'bg-success'
      if (quiz.is_upcoming) return classes + 'bg-info'
      if (quiz.is_expired) return classes + 'bg-danger'
      return classes + 'bg-secondary'
    },
    async fetchChapterDetails() {
      try {
        const response = await fetch(`http://localhost:5000/chapters/${this.$route.params.chapterId}`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          const chapter = await response.json()
          this.chapterName = chapter.name
        }
      } catch (error) {
        console.error('Error:', error)
      }
    },
    async fetchQuizzes() {
      try {
        const response = await fetch(`http://localhost:5000/chapters/${this.$route.params.chapterId}/quizzes`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.quizzes = await response.json()
        }
      } catch (error) {
        this.error = 'Failed to fetch quizzes'
        console.error('Error:', error)
      }
    },
    async handleSubmit() {
      this.loading = true
      this.error = null
      try {
        // Format dates to ISO string without milliseconds
        const formData = {
          ...this.newQuiz,
          start_date: this.newQuiz.start_date ? new Date(this.newQuiz.start_date).toISOString().split('.')[0] : '',
          end_date: this.newQuiz.end_date ? new Date(this.newQuiz.end_date).toISOString().split('.')[0] : '',
          time_duration: parseInt(this.newQuiz.time_duration)
        }

        if (!formData.start_date || !formData.end_date) {
          this.error = 'Please select both start and end dates'
          this.loading = false
          return
        }

        const response = await fetch(`http://localhost:5000/chapters/${this.$route.params.chapterId}/quizzes`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(formData)
        })
        
        const data = await response.json()
        if (response.ok) {
          await this.fetchQuizzes()
          this.newQuiz = {
            title: '',
            description: '',
            start_date: '',
            end_date: '',
            time_duration: 30,
            status: 'draft'
          }
        } else {
          this.error = data.error || 'Failed to create quiz'
        }
      } catch (error) {
        this.error = 'Failed to add quiz'
        console.error('Error:', error)
      }
      this.loading = false
    },
    async deleteQuiz(id) {
      if (!confirm('Are you sure you want to delete this quiz?')) return
      
      try {
        const response = await fetch(`http://localhost:5000/quizzes/${id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        if (response.ok) {
          await this.fetchQuizzes()
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to delete quiz'
        console.error('Error:', error)
      }
    }
  }
}
</script>

<style scoped>
.badge {
  font-size: 0.9em;
  padding: 0.5em 0.8em;
}
</style> 