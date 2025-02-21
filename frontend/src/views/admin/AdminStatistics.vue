<template>
  <div class="admin-statistics">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>
        <i class="fas fa-chart-line me-2"></i>
        Analytics Dashboard
      </h1>
      <button class="btn btn-primary" @click="fetchStatistics">
        <i class="fas fa-sync-alt me-2"></i>Refresh Data
      </button>
    </div>

    <!-- Overall Performance Metrics -->
    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card shadow-sm">
          <div class="card-body">
            <h6 class="text-muted mb-1">Total Users</h6>
            <h3 class="mb-0">{{ statistics?.total_users || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm">
          <div class="card-body">
            <h6 class="text-muted mb-1">Total Quizzes</h6>
            <h3 class="mb-0">{{ statistics?.total_quizzes || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm">
          <div class="card-body">
            <h6 class="text-muted mb-1">Total Questions</h6>
            <h3 class="mb-0">{{ statistics?.total_questions || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm">
          <div class="card-body">
            <h6 class="text-muted mb-1">Total Attempts</h6>
            <h3 class="mb-0">{{ statistics?.total_attempts || 0 }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="row g-4">
      <!-- Quiz Status Distribution -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title mb-3">Quiz Status Distribution</h5>
            <canvas id="quizStatusChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Subject Performance -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5 class="card-title mb-3">Subject Performance Overview</h5>
            <canvas id="subjectPerformanceChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Subject-wise Statistics Table -->
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title mb-3">Detailed Subject Statistics</h5>
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Average Score</th>
                    <th>Total Quizzes</th>
                    <th>Total Attempts</th>
                    <th>Performance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subject in statistics?.subjects_performance" :key="subject.name">
                    <td>{{ subject.name }}</td>
                    <td>{{ subject.average_score }}%</td>
                    <td>{{ subject.total_quizzes || 0 }}</td>
                    <td>{{ subject.total_attempts || 0 }}</td>
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
  name: 'AdminStatistics',
  mixins: [userMixin],
  data() {
    return {
      statistics: null,
      quizStatusChart: null,
      subjectPerformanceChart: null,
      error: null
    }
  },
  async created() {
    await this.fetchStatistics()
  },
  beforeUnmount() {
    if (this.quizStatusChart) {
      this.quizStatusChart.destroy()
    }
    if (this.subjectPerformanceChart) {
      this.subjectPerformanceChart.destroy()
    }
  },
  methods: {
    async fetchStatistics() {
      try {
        const response = await fetch('http://localhost:5000/admin/statistics', {
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

      // Quiz Status Chart
      const quizStatusCtx = document.getElementById('quizStatusChart')
      this.quizStatusChart = new Chart(quizStatusCtx, {
        type: 'doughnut',
        data: {
          labels: ['Active', 'Completed', 'Upcoming'],
          datasets: [{
            data: [
              this.statistics.active_quizzes,
              this.statistics.completed_quizzes,
              this.statistics.total_quizzes - (this.statistics.active_quizzes + this.statistics.completed_quizzes)
            ],
            backgroundColor: [
              'rgba(75, 192, 192, 0.8)',
              'rgba(54, 162, 235, 0.8)',
              'rgba(255, 206, 86, 0.8)'
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })

      // Subject Performance Chart
      const subjectPerformanceCtx = document.getElementById('subjectPerformanceChart')
      this.subjectPerformanceChart = new Chart(subjectPerformanceCtx, {
        type: 'bar',
        data: {
          labels: this.statistics.subjects_performance.map(s => s.name),
          datasets: [{
            label: 'Average Score (%)',
            data: this.statistics.subjects_performance.map(s => s.average_score),
            backgroundColor: 'rgba(75, 192, 192, 0.8)',
            borderColor: 'rgba(75, 192, 192, 1)',
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
.admin-statistics {
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