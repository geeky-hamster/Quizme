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
                    <th>Quiz Title</th>
                    <th>Date</th>
                    <th>Score</th>
                    <th>Performance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="score in scores" :key="score.id">
                    <td>{{ score.subject }}</td>
                    <td>{{ score.chapter }}</td>
                    <td>{{ score.quiz_title }}</td>
                    <td>{{ formatDateTime(score.attempt_time) }}</td>
                    <td>
                      <span class="badge" :class="getScoreBadgeClass(score.percentage)">
                        {{ score.percentage }}%
                      </span>
                      <small class="text-muted ms-2">({{ score.score }})</small>
                    </td>
                    <td>
                      <div class="progress" style="height: 20px;">
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
import { formatDateTime } from '@/utils/dateUtils'

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
      return formatDateTime(dateStr)
    },
    getScoreBadgeClass(percentage) {
      if (percentage >= 90) return 'bg-success'
      if (percentage >= 75) return 'bg-info'
      if (percentage >= 60) return 'bg-warning'
      return 'bg-danger'
    },
    getProgressBarClass(percentage) {
      if (percentage >= 90) return 'bg-success'
      if (percentage >= 75) return 'bg-info'
      if (percentage >= 60) return 'bg-warning'
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
  height: 20px;
  border-radius: 10px;
  background-color: #f0f0f0;
}

.progress-bar {
  line-height: 20px;
  font-weight: bold;
  font-size: 0.85rem;
  transition: width 0.6s ease;
}

.badge {
  font-size: 0.9rem;
  padding: 0.4em 0.6em;
}

.table > :not(caption) > * > * {
  padding: 1rem;
  vertical-align: middle;
}

.table th {
  font-weight: 600;
  background-color: #f8f9fa;
}

.table tr:hover {
  background-color: rgba(0, 0, 0, 0.02);
}
</style> 