<template>
  <div class="admin-dashboard">
    <h1 class="mb-4">
      <i class="fas fa-tachometer-alt me-2"></i>
      Admin Dashboard
    </h1>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show mb-4" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Stats Cards Row -->
    <div class="row g-4 mb-4">
      <div class="col-md-3" v-for="(stat, key) in stats" :key="key">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="stat-icon me-3" :class="getIconColorClass(key)">
                <i :class="statIcons[key]"></i>
              </div>
              <div>
                <h3 class="card-title h5 mb-0">{{ statTitles[key] }}</h3>
                <p class="card-text display-6 mb-0">{{ stat }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions and Recent Activity Row -->
    <div class="row g-4">
      <!-- Quick Actions -->
      <div class="col-md-6">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <h5 class="card-title mb-3">
              <i class="fas fa-bolt me-2"></i>Quick Actions
            </h5>
            <div class="d-grid gap-2">
              <router-link to="/admin/subjects" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>Add New Subject
              </router-link>
              <router-link 
                v-if="latestSubject"
                :to="'/admin/subjects/' + latestSubject.id + '/chapters'" 
                class="btn btn-outline-primary">
                <i class="fas fa-edit me-2"></i>Manage Latest Subject: {{ latestSubject.name }}
              </router-link>
              <router-link 
                v-if="latestChapter"
                :to="'/admin/chapters/' + latestChapter.id + '/quizzes'" 
                class="btn btn-outline-primary">
                <i class="fas fa-book me-2"></i>Manage Latest Chapter: {{ latestChapter.name }}
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="col-md-6">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="card-title mb-0">
                <i class="fas fa-history me-2"></i>Recent Activity
              </h5>
              <button class="btn btn-sm btn-outline-primary" @click="fetchDashboardData">
                <i class="fas fa-sync-alt me-1"></i>Refresh
              </button>
            </div>
            <div class="activity-list">
              <div v-if="recentActivity.length === 0" class="text-center text-muted py-3">
                No recent activity
              </div>
              <div v-for="activity in recentActivity" :key="activity.id" class="activity-item mb-3">
                <div class="d-flex align-items-center">
                  <div class="activity-icon me-3">
                    <i :class="activity.icon"></i>
                  </div>
                  <div class="activity-content">
                    <p class="mb-1">{{ activity.text }}</p>
                    <small class="text-muted">{{ formatDate(activity.timestamp) }}</small>
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
import userMixin from '@/mixins/userMixin'
import { formatTimeAgo } from '@/utils/dateUtils'
const API_URL = 'http://localhost:5000'

export default {
  name: 'AdminDashboard',
  mixins: [userMixin],
  data() {
    return {
      stats: {
        subjects: 0,
        chapters: 0,
        activeQuizzes: 0,
        users: 0
      },
      statTitles: {
        subjects: 'Total Subjects',
        chapters: 'Total Chapters',
        activeQuizzes: 'Active Quizzes',
        users: 'Total Users'
      },
      statIcons: {
        subjects: 'fas fa-book',
        chapters: 'fas fa-bookmark',
        activeQuizzes: 'fas fa-tasks',
        users: 'fas fa-users'
      },
      latestSubject: null,
      latestChapter: null,
      recentActivity: [],
      refreshInterval: null,
      error: null
    }
  },
  async created() {
    await this.fetchDashboardData()
    this.refreshInterval = setInterval(this.fetchDashboardData, 30000)
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    async fetchDashboardData() {
      try {
        const response = await fetch(`${API_URL}/admin/dashboard-stats`, {
          method: 'GET',
          headers: this.getAuthHeaders(),
          credentials: 'include',
          mode: 'cors'
        })
        
        if (response.ok) {
          const data = await response.json()
          this.stats = data.stats
          this.latestSubject = data.latestSubject
          this.latestChapter = data.latestChapter
          this.recentActivity = data.recentActivity
          this.error = null
        } else {
          const errorData = await response.json()
          this.error = errorData.error || 'Failed to fetch dashboard data'
          console.error('Dashboard error:', this.error)
        }
      } catch (error) {
        this.error = 'Failed to connect to the server'
        console.error('Failed to fetch dashboard data:', error)
      }
    },
    formatDate(timestamp) {
      return formatTimeAgo(timestamp)
    },
    getIconColorClass(key) {
      const colorClasses = {
        subjects: 'text-primary',
        chapters: 'text-success',
        activeQuizzes: 'text-warning',
        users: 'text-info'
      }
      return colorClasses[key] || 'text-primary'
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  animation: fadeIn 0.5s ease-in-out;
}

.stat-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
}

.activity-icon {
  font-size: 1.2rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: rgba(var(--bs-success-rgb), 0.1);
}

.activity-item {
  padding: 1rem;
  border-radius: 0.5rem;
  transition: background-color 0.3s ease;
}

.activity-item:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.05);
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

.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
</style> 