<template>
  <div class="user-statistics">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>
        <i class="fas fa-chart-line me-2"></i>
        My Performance Analytics
      </h1>
      <button class="btn btn-primary" @click="fetchStatistics">
        <i class="fas fa-sync-alt me-2"></i>Refresh Data
      </button>
    </div>

    <!-- Overall Performance Metrics -->
    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="card shadow-sm bg-primary text-white">
          <div class="card-body">
            <h6 class="mb-1">Total Attempts</h6>
            <h3 class="mb-0">{{ statistics?.total_attempts || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm bg-success text-white">
          <div class="card-body">
            <h6 class="mb-1">Average Score</h6>
            <h3 class="mb-0">{{ statistics?.average_score || 0 }}%</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm bg-info text-white">
          <div class="card-body">
            <h6 class="mb-1">Subjects Attempted</h6>
            <h3 class="mb-0">{{ subjectsAttempted }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="row g-4">
      <!-- Subject Performance Chart -->
      <div class="col-md-8 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title mb-3">Performance by Subject</h5>
            <canvas id="subjectPerformanceChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Recent Performance Trend -->
      <div class="col-md-4 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title mb-3">Recent Performance Trend</h5>
            <canvas id="performanceTrendChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Detailed Performance Table -->
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title mb-3">Subject-wise Performance Details</h5>
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Attempts</th>
                    <th>Average Score</th>
                    <th>Best Score</th>
                    <th>Progress</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subject in statistics?.subjects_performance" :key="subject.name">
                    <td>{{ subject.name }}</td>
                    <td>{{ subject.attempts }}</td>
                    <td>{{ subject.average_score }}%</td>
                    <td>{{ subject.best_score || subject.average_score }}%</td>
                    <td>
                      <div class="progress" style="height: 8px;">
                        <div class="progress-bar" 
                             :class="getPerformanceClass(subject.average_score)"
                             :style="{ width: subject.average_score + '%' }">
                        </div>
                      </div>
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
import userMixin from '@/mixins/userMixin'
import { formatDateTime } from '@/utils/dateUtils'

export default {
  name: 'UserStatistics',
  mixins: [userMixin],
  data() {
    return {
      statistics: null,
      subjectPerformanceChart: null,
      performanceTrendChart: null,
      error: null
    }
  },
  computed: {
    subjectsAttempted() {
      if (!this.statistics?.subjects_performance) return 0
      return this.statistics.subjects_performance.filter(s => s.attempts > 0).length
    }
  },
  async created() {
    await this.fetchStatistics()
  },
  beforeUnmount() {
    if (this.subjectPerformanceChart) {
      this.subjectPerformanceChart.destroy()
    }
    if (this.performanceTrendChart) {
      this.performanceTrendChart.destroy()
    }
  },
  methods: {
    async fetchStatistics() {
      try {
        const response = await fetch('http://localhost:5000/user/statistics', {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.statistics = await response.json()
          this.initializeCharts()
        }
      } catch (error) {
        console.error('Failed to fetch statistics:', error)
        this.error = 'Failed to load statistics'
      }
    },
    initializeCharts() {
      if (!this.statistics) return

      // Subject Performance Chart
      const subjectCtx = document.getElementById('subjectPerformanceChart')
      this.subjectPerformanceChart = new Chart(subjectCtx, {
        type: 'bar',
        data: {
          labels: this.statistics.subjects_performance.map(s => s.name),
          datasets: [{
            label: 'Average Score (%)',
            data: this.statistics.subjects_performance.map(s => s.average_score),
            backgroundColor: 'rgba(75, 192, 192, 0.8)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }, {
            label: 'Attempts',
            data: this.statistics.subjects_performance.map(s => s.attempts),
            backgroundColor: 'rgba(54, 162, 235, 0.8)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      })

      // Performance Trend Chart
      const trendCtx = document.getElementById('performanceTrendChart')
      this.performanceTrendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
          labels: this.statistics.performance_trend.map(p => p.date),
          datasets: [{
            label: 'Score (%)',
            data: this.statistics.performance_trend.map(p => p.score),
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      })
    },
    getPerformanceClass(score) {
      if (score >= 80) return 'bg-success'
      if (score >= 60) return 'bg-info'
      if (score >= 40) return 'bg-warning'
      return 'bg-danger'
    },
    formatDate(dateStr) {
      return formatDateTime(dateStr)
    }
  }
}
</script>

<style scoped>
.user-statistics {
  animation: fadeIn 0.5s ease-in-out;
}

.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.progress {
  border-radius: 1rem;
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