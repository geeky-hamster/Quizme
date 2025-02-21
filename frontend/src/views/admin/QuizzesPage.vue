<template>
  <div class="quizzes-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1">
          <i class="fas fa-tasks me-2"></i>
          {{ chapterName }}
        </h2>
        <p class="text-muted mb-0">Manage quizzes for this chapter</p>
      </div>
      <div class="d-flex gap-2">
        <router-link :to="'/admin/subjects/' + subjectId + '/chapters'" class="btn btn-outline-secondary">
          <i class="fas fa-arrow-left me-2"></i>Back to Chapters
        </router-link>
        <button class="btn btn-primary" @click="showAddForm = !showAddForm">
          <i class="fas" :class="showAddForm ? 'fa-minus' : 'fa-plus'"></i>
          {{ showAddForm ? 'Hide Form' : 'Add New Quiz' }}
        </button>
      </div>
    </div>

    <!-- Add Quiz Form -->
    <div class="row mb-4" v-if="showAddForm">
      <div class="col-md-8">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">
              <i class="fas fa-plus-circle me-2"></i>
              Add New Quiz
            </h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="row">
                <div class="col-md-12 mb-3">
                  <label for="title" class="form-label">Quiz Title</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="title" 
                    v-model="newQuiz.title" 
                    required
                    placeholder="Enter quiz title"
                  >
                </div>
                <div class="col-md-12 mb-3">
                  <label for="description" class="form-label">Description</label>
                  <textarea 
                    class="form-control" 
                    id="description" 
                    v-model="newQuiz.description" 
                    rows="3"
                    placeholder="Enter quiz description"
                  ></textarea>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="start_date" class="form-label">Start Date & Time</label>
                  <input 
                    type="datetime-local" 
                    class="form-control" 
                    id="start_date" 
                    v-model="newQuiz.start_date" 
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="end_date" class="form-label">End Date & Time</label>
                  <input 
                    type="datetime-local" 
                    class="form-control" 
                    id="end_date" 
                    v-model="newQuiz.end_date" 
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="time_duration" class="form-label">Duration (minutes)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="time_duration" 
                    v-model="newQuiz.time_duration" 
                    required 
                    min="1"
                    placeholder="Enter duration in minutes"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="status" class="form-label">Status</label>
                  <select class="form-select" id="status" v-model="newQuiz.status" required>
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                  </select>
                </div>
              </div>
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-outline-secondary me-2" @click="showAddForm = false">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                  {{ loading ? 'Adding...' : 'Add Quiz' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Quizzes Grid -->
    <div class="row g-4">
      <div v-if="loading && !quizzes.length" class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="!quizzes.length" class="col-12 text-center py-5">
        <div class="empty-state">
          <i class="fas fa-tasks fa-3x mb-3 text-muted"></i>
          <h4>No Quizzes Yet</h4>
          <p class="text-muted">Start by adding your first quiz to this chapter.</p>
          <button class="btn btn-primary" @click="showAddForm = true">
            <i class="fas fa-plus me-2"></i>Add Quiz
          </button>
        </div>
      </div>
      <div v-for="quiz in quizzes" :key="quiz.id" class="col-md-6 col-lg-4">
        <div class="card h-100 quiz-card" :class="getQuizStatusClass(quiz)">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h5 class="card-title mb-1">{{ quiz.title }}</h5>
              <div class="dropdown">
                <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li>
                    <router-link :to="'/admin/quizzes/' + quiz.id + '/questions'" class="dropdown-item">
                      <i class="fas fa-question-circle me-2"></i>Manage Questions
                    </router-link>
                  </li>
                  <li>
                    <button class="dropdown-item" @click="editQuiz(quiz)">
                      <i class="fas fa-edit me-2"></i>Edit
                    </button>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <button class="dropdown-item text-danger" @click="confirmDelete(quiz)">
                      <i class="fas fa-trash-alt me-2"></i>Delete
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            <p class="card-text text-muted mb-3">
              {{ quiz.description || 'No description available' }}
            </p>
            <div class="quiz-details">
              <div class="mb-2">
                <i class="fas fa-clock me-2"></i>
                <span>{{ quiz.time_duration }} minutes</span>
              </div>
              <div class="mb-2">
                <i class="fas fa-calendar-alt me-2"></i>
                <span>{{ formatDateTime(quiz.start_date) }} - {{ formatDateTime(quiz.end_date) }}</span>
              </div>
              <div class="mb-3">
                <span :class="getStatusBadgeClass(quiz)">{{ getStatusText(quiz) }}</span>
              </div>
            </div>
            <div class="mt-3">
              <router-link :to="'/admin/quizzes/' + quiz.id + '/questions'" class="btn btn-outline-primary btn-sm w-100">
                <i class="fas fa-question-circle me-1"></i>
                Manage Questions
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-backdrop fade show"></div>
    <div v-if="showDeleteModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" @click="cancelDelete"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete the quiz "{{ selectedQuiz?.title }}"?
            This action cannot be undone and will delete all associated questions and scores.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelDelete">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteQuiz">
              <i class="fas fa-trash-alt me-1"></i>
              Delete Quiz
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Quiz Modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show"></div>
    <div v-if="showEditModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Quiz</h5>
            <button type="button" class="btn-close" @click="cancelEdit"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateQuiz">
              <div class="row">
                <div class="col-md-12 mb-3">
                  <label for="edit-title" class="form-label">Quiz Title</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="edit-title" 
                    v-model="editingQuiz.title" 
                    required
                  >
                </div>
                <div class="col-md-12 mb-3">
                  <label for="edit-description" class="form-label">Description</label>
                  <textarea 
                    class="form-control" 
                    id="edit-description" 
                    v-model="editingQuiz.description" 
                    rows="3"
                  ></textarea>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="edit-start_date" class="form-label">Start Date & Time</label>
                  <input 
                    type="datetime-local" 
                    class="form-control" 
                    id="edit-start_date" 
                    v-model="editingQuiz.start_date" 
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="edit-end_date" class="form-label">End Date & Time</label>
                  <input 
                    type="datetime-local" 
                    class="form-control" 
                    id="edit-end_date" 
                    v-model="editingQuiz.end_date" 
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="edit-time_duration" class="form-label">Duration (minutes)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="edit-time_duration" 
                    v-model="editingQuiz.time_duration" 
                    required 
                    min="1"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="edit-status" class="form-label">Status</label>
                  <select class="form-select" id="edit-status" v-model="editingQuiz.status" required>
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                  </select>
                </div>
              </div>
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" @click="cancelEdit">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                  {{ loading ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import userMixin from '../../mixins/userMixin'
import { formatQuizDateTime } from '@/utils/dateUtils'

export default {
  name: 'QuizzesPage',
  mixins: [userMixin],
  data() {
    return {
      chapterName: '',
      subjectId: '',
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
      error: null,
      showAddForm: false,
      selectedQuiz: null,
      showDeleteModal: false,
      showEditModal: false,
      editingQuiz: null
    }
  },
  created() {
    this.fetchChapterDetails()
    this.fetchQuizzes()
  },
  methods: {
    formatDateTime(dateStr) {
      return formatQuizDateTime(dateStr)
    },
    getQuizStatusClass(quiz) {
      if (quiz.is_active) return 'border-success'
      if (quiz.is_upcoming) return 'border-info'
      if (quiz.is_expired) return 'border-danger'
      return 'border-secondary'
    },
    getStatusBadgeClass(quiz) {
      const baseClass = 'badge rounded-pill'
      if (quiz.is_active) return `${baseClass} bg-success`
      if (quiz.is_upcoming) return `${baseClass} bg-info`
      if (quiz.is_expired) return `${baseClass} bg-danger`
      return `${baseClass} bg-secondary`
    },
    getStatusText(quiz) {
      if (quiz.is_active) return 'Active'
      if (quiz.is_upcoming) return 'Upcoming'
      if (quiz.is_expired) return 'Expired'
      return quiz.status.charAt(0).toUpperCase() + quiz.status.slice(1)
    },
    async fetchChapterDetails() {
      try {
        const response = await fetch(`http://localhost:5000/chapters/${this.$route.params.chapterId}`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          const chapter = await response.json()
          this.chapterName = chapter.name
          this.subjectId = chapter.subject_id
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = 'Failed to fetch chapter details'
      }
    },
    async fetchQuizzes() {
      this.loading = true
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
      this.loading = false
    },
    async handleSubmit() {
      this.loading = true
      this.error = null
      try {
        // Convert local dates to UTC
        const startDate = new Date(this.newQuiz.start_date)
        const endDate = new Date(this.newQuiz.end_date)
        
        // Add timezone offset to convert to UTC
        const startUTC = new Date(startDate.getTime() + startDate.getTimezoneOffset() * 60000)
        const endUTC = new Date(endDate.getTime() + endDate.getTimezoneOffset() * 60000)
        
        const formData = {
          ...this.newQuiz,
          start_date: startUTC.toISOString(),
          end_date: endUTC.toISOString(),
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
          this.showAddForm = false
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Quiz added successfully',
            type: 'success'
          })
        } else {
          this.error = data.error || 'Failed to create quiz'
        }
      } catch (error) {
        this.error = 'Failed to add quiz'
        console.error('Error:', error)
      }
      this.loading = false
    },
    confirmDelete(quiz) {
      this.selectedQuiz = quiz
      this.showDeleteModal = true
    },
    cancelDelete() {
      this.selectedQuiz = null
      this.showDeleteModal = false
    },
    async deleteQuiz() {
      if (!this.selectedQuiz) return
      
      try {
        const response = await fetch(`http://localhost:5000/quizzes/${this.selectedQuiz.id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        if (response.ok) {
          await this.fetchQuizzes()
          this.showDeleteModal = false
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Quiz deleted successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to delete quiz'
        console.error('Error:', error)
      }
      this.selectedQuiz = null
    },
    editQuiz(quiz) {
      const start = new Date(quiz.start_date)
      const end = new Date(quiz.end_date)
      
      // Convert UTC to local time
      const startLocal = new Date(start.getTime() - start.getTimezoneOffset() * 60000)
      const endLocal = new Date(end.getTime() - end.getTimezoneOffset() * 60000)
      
      // Format for datetime-local input
      const formatForInput = (date) => {
        return date.toISOString().slice(0, 16)
      }
      
      this.editingQuiz = {
        ...quiz,
        start_date: formatForInput(startLocal),
        end_date: formatForInput(endLocal),
        time_duration: parseInt(quiz.time_duration) // Ensure time_duration is a number
      }
      this.showEditModal = true
    },
    cancelEdit() {
      this.editingQuiz = null
      this.showEditModal = false
    },
    async updateQuiz() {
      if (!this.editingQuiz) return
      
      this.loading = true
      this.error = null
      
      try {
        // Convert local dates back to UTC
        const startDate = new Date(this.editingQuiz.start_date)
        const endDate = new Date(this.editingQuiz.end_date)
        
        // Add timezone offset to convert to UTC
        const startUTC = new Date(startDate.getTime() + startDate.getTimezoneOffset() * 60000)
        const endUTC = new Date(endDate.getTime() + endDate.getTimezoneOffset() * 60000)
        
        // Ensure time_duration is a valid positive number
        const timeDuration = parseInt(this.editingQuiz.time_duration)
        if (isNaN(timeDuration) || timeDuration <= 0) {
          this.error = 'Time duration must be a positive number'
          this.loading = false
          return
        }
        
        const formData = {
          ...this.editingQuiz,
          start_date: startUTC.toISOString(),
          end_date: endUTC.toISOString(),
          time_duration: timeDuration
        }

        const response = await fetch(`http://localhost:5000/quizzes/${this.editingQuiz.id}`, {
          method: 'PUT',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(formData)
        })
        
        if (response.ok) {
          await this.fetchQuizzes()
          this.showEditModal = false
          this.editingQuiz = null
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Quiz updated successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to update quiz'
        console.error('Error:', error)
      }
      this.loading = false
    }
  }
}
</script>

<style scoped>
.quizzes-page {
  animation: fadeIn 0.3s ease-in-out;
}

.quiz-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border-width: 2px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.quiz-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.quiz-details {
  font-size: 0.9rem;
  color: #6c757d;
}

.empty-state {
  padding: 3rem 1rem;
  color: #6c757d;
}

.empty-state i {
  opacity: 0.5;
}

.dropdown-menu {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  border: none;
}

.dropdown-item {
  padding: 0.5rem 1rem;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.1);
}

.dropdown-item.text-danger:hover {
  background-color: rgba(var(--bs-danger-rgb), 0.1);
}

.badge {
  padding: 0.5em 1em;
  font-weight: 500;
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

/* Modal animations */
.modal.fade.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-backdrop.fade.show {
  opacity: 0.5;
}

.modal-content {
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style> 