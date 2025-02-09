<template>
  <div>
    <h2>My Quiz Scores</h2>
    <div class="row">
      <div class="col-12">
        <div v-if="$route.query.message" class="alert alert-success">
          {{ $route.query.message }}
        </div>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        
        <div class="card">
          <div class="card-header">
            <h4>Score History</h4>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Chapter</th>
                    <th>Date</th>
                    <th>Score</th>
                    <th>Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="score in scores" :key="score.id">
                    <td>{{ score.subject }}</td>
                    <td>{{ score.chapter }}</td>
                    <td>{{ formatDateTime(score.attempt_time) }}</td>
                    <td>{{ score.score }}</td>
                    <td>
                      <div class="progress">
                        <div 
                          class="progress-bar" 
                          role="progressbar" 
                          :style="{ width: score.percentage + '%' }"
                          :class="getProgressBarClass(score.percentage)"
                        >
                          {{ score.percentage }}%
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="scores.length === 0" class="text-center py-5">
              <h4>No quiz attempts yet</h4>
              <p class="text-muted">Take some quizzes to see your scores here!</p>
              <router-link to="/quizzes" class="btn btn-primary">
                View Available Quizzes
              </router-link>
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
  name: 'MyScores',
  mixins: [userMixin],
  data() {
    return {
      scores: [],
      error: null
    }
  },
  created() {
    this.fetchScores()
  },
  methods: {
    formatDateTime(dateStr) {
      return new Date(dateStr).toLocaleString()
    },
    getProgressBarClass(percentage) {
      if (percentage >= 80) return 'bg-success'
      if (percentage >= 60) return 'bg-info'
      if (percentage >= 40) return 'bg-warning'
      return 'bg-danger'
    },
    async fetchScores() {
      try {
        const response = await fetch('http://localhost:5000/my-scores', {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.scores = await response.json()
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to fetch scores'
        console.error('Error:', error)
      }
    }
  }
}
</script>

<style scoped>
.progress {
  height: 25px;
}
.progress-bar {
  line-height: 25px;
  font-weight: bold;
}
</style> 