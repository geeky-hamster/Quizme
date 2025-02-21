<template>
  <div class="user-dashboard">
    <div class="row mb-4">
      <div class="col-12">
        <h2 class="dashboard-title">
          <i class="fas fa-tachometer-alt me-2"></i>Student Dashboard
        </h2>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="card stat-card bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-subtitle mb-2">Available Quizzes</h6>
                <h2 class="card-title mb-0">{{ stats.availableQuizzes }}</h2>
              </div>
              <i class="fas fa-clipboard-list fa-2x"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card stat-card bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-subtitle mb-2">Completed Quizzes</h6>
                <h2 class="card-title mb-0">{{ stats.completedQuizzes }}</h2>
              </div>
              <i class="fas fa-check-circle fa-2x"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card stat-card bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-subtitle mb-2">Average Score</h6>
                <h2 class="card-title mb-0">{{ stats.averageScore }}%</h2>
              </div>
              <i class="fas fa-chart-line fa-2x"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Available Quizzes -->
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="fas fa-clock me-2"></i>Available Quizzes
            </h5>
            <router-link to="/quizzes" class="btn btn-primary btn-sm">
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="availableQuizzes.length === 0" class="text-center text-muted py-3">
              No quizzes available at the moment
            </div>
            <div v-else class="quiz-list">
              <div v-for="quiz in availableQuizzes" :key="quiz.id" class="quiz-item">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-1">{{ quiz.title }}</h6>
                    <small class="text-muted">
                      {{ quiz.subject }} - {{ quiz.chapter }}
                    </small>
                  </div>
                  <router-link :to="'/quizzes/' + quiz.id + '/attempt'" class="btn btn-outline-primary btn-sm">
                    Start Quiz
                  </router-link>
                </div>
                <div class="quiz-details mt-2">
                  <span class="badge bg-info me-2">
                    <i class="fas fa-clock me-1"></i>{{ quiz.time_duration }} mins
                  </span>
                  <span class="badge bg-secondary me-2">
                    <i class="fas fa-question-circle me-1"></i>{{ quiz.total_questions }} questions
                  </span>
                  <small class="text-muted">
                    Available until {{ formatDate(quiz.end_date) }}
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Scores -->
      <div class="col-md-4">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="fas fa-trophy me-2"></i>Recent Scores
            </h5>
            <router-link to="/my-scores" class="btn btn-primary btn-sm">
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="recentScores.length === 0" class="text-center text-muted py-3">
              No quiz attempts yet
            </div>
            <div v-else class="score-list">
              <div v-for="score in recentScores" :key="score.id" class="score-item">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <div>
                    <h6 class="mb-1">{{ score.subject }}</h6>
                    <small class="text-muted">{{ score.chapter }}</small>
                  </div>
                  <div class="score-badge" :class="getScoreBadgeClass(score.percentage)">
                    {{ score.percentage }}%
                  </div>
                </div>
                <div class="progress" style="height: 5px;">
                  <div class="progress-bar" :class="getProgressBarClass(score.percentage)"
                       :style="{ width: score.percentage + '%' }">
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import userMixin from '../../mixins/userMixin'
import { formatDateTime, formatQuizDateTime } from '@/utils/dateUtils'

export default {
  name: 'UserDashboard',
  mixins: [userMixin],
  data() {
    return {
      stats: {
        availableQuizzes: 0,
        completedQuizzes: 0,
        averageScore: 0
      },
      availableQuizzes: [],
      recentScores: []
    }
  },
  async created() {
    await this.fetchDashboardData()
  },
  methods: {
    async fetchDashboardData() {
      try {
        // Fetch available quizzes
        const quizzesResponse = await this.makeAuthenticatedRequest('http://localhost:5000/available-quizzes')
        if (quizzesResponse && quizzesResponse.ok) {
          this.availableQuizzes = await quizzesResponse.json()
          this.stats.availableQuizzes = this.availableQuizzes.length
        }

        // Fetch scores
        const scoresResponse = await this.makeAuthenticatedRequest('http://localhost:5000/my-scores')
        if (scoresResponse && scoresResponse.ok) {
          this.recentScores = await scoresResponse.json()
          this.stats.completedQuizzes = this.recentScores.length
          
          // Calculate average score
          if (this.recentScores.length > 0) {
            const totalPercentage = this.recentScores.reduce((sum, score) => sum + score.percentage, 0)
            this.stats.averageScore = Math.round(totalPercentage / this.recentScores.length)
          }
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    },
    formatDate(dateStr) {
      return formatDateTime(dateStr)
    },
    formatQuizDate(dateStr) {
      return formatQuizDateTime(dateStr)
    },
    getScoreBadgeClass(percentage) {
      if (percentage >= 80) return 'score-badge-excellent'
      if (percentage >= 60) return 'score-badge-good'
      if (percentage >= 40) return 'score-badge-fair'
      return 'score-badge-poor'
    },
    getProgressBarClass(percentage) {
      if (percentage >= 80) return 'bg-success'
      if (percentage >= 60) return 'bg-info'
      if (percentage >= 40) return 'bg-warning'
      return 'bg-danger'
    }
  }
}
</script>

<style scoped>
.user-dashboard {
  animation: fadeIn 0.5s ease-in-out;
}

.dashboard-title {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.stat-card {
  transition: transform 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.quiz-list {
  max-height: 400px;
  overflow-y: auto;
}

.quiz-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.quiz-item:last-child {
  border-bottom: none;
}

.quiz-details {
  font-size: 0.9rem;
}

.score-list {
  max-height: 400px;
  overflow-y: auto;
}

.score-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.score-item:last-child {
  border-bottom: none;
}

.score-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 1rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.score-badge-excellent {
  background-color: #d4edda;
  color: #155724;
}

.score-badge-good {
  background-color: #d1ecf1;
  color: #0c5460;
}

.score-badge-fair {
  background-color: #fff3cd;
  color: #856404;
}

.score-badge-poor {
  background-color: #f8d7da;
  color: #721c24;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 