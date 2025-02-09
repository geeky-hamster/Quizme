<template>
  <div>
    <h2>Available Quizzes</h2>
    <div class="row">
      <div class="col-12">
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div class="row">
          <div class="col-md-4 mb-4" v-for="quiz in quizzes" :key="quiz.id">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ quiz.title }}</h5>
                <p class="card-text">
                  <strong>Subject:</strong> {{ quiz.subject }}<br>
                  <strong>Chapter:</strong> {{ quiz.chapter }}<br>
                  <strong>Duration:</strong> {{ quiz.time_duration }} minutes<br>
                  <strong>Questions:</strong> {{ quiz.total_questions }}
                </p>
                <div class="small text-muted mb-3">
                  Available from {{ formatDateTime(quiz.start_date) }}<br>
                  until {{ formatDateTime(quiz.end_date) }}
                </div>
                <div class="d-grid">
                  <router-link 
                    :to="'/quizzes/' + quiz.id + '/attempt'" 
                    class="btn btn-primary"
                  >
                    Start Quiz
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="quizzes.length === 0" class="text-center py-5">
          <h4>No quizzes available at the moment.</h4>
          <p class="text-muted">Check back later for new quizzes!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import userMixin from '../../mixins/userMixin'

export default {
  name: 'AvailableQuizzes',
  mixins: [userMixin],
  data() {
    return {
      quizzes: [],
      error: null
    }
  },
  created() {
    this.fetchQuizzes()
  },
  methods: {
    formatDateTime(dateStr) {
      return new Date(dateStr).toLocaleString()
    },
    async fetchQuizzes() {
      try {
        const response = await fetch('http://localhost:5000/available-quizzes', {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.quizzes = await response.json()
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to fetch available quizzes'
        console.error('Error:', error)
      }
    }
  }
}
</script> 