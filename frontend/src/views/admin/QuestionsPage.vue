<template>
  <div class="questions-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1">
          <i class="fas fa-question-circle me-2"></i>
          {{ quizTitle }}
        </h2>
        <p class="text-muted mb-0">Manage questions for this quiz</p>
      </div>
      <div class="d-flex gap-2">
        <router-link :to="'/admin/chapters/' + chapterId + '/quizzes'" class="btn btn-outline-secondary">
          <i class="fas fa-arrow-left me-2"></i>Back to Quizzes
        </router-link>
        <button class="btn btn-primary" @click="showAddForm = !showAddForm">
          <i class="fas" :class="showAddForm ? 'fa-minus' : 'fa-plus'"></i>
          {{ showAddForm ? 'Hide Form' : 'Add New Question' }}
        </button>
      </div>
    </div>

    <!-- Add Question Form -->
    <div class="row mb-4" v-if="showAddForm">
      <div class="col-md-8">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">
              <i class="fas fa-plus-circle me-2"></i>
              Add New Question
            </h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-4">
                <label for="question_statement" class="form-label">Question</label>
                <textarea 
                  class="form-control" 
                  id="question_statement" 
                  v-model="newQuestion.question_statement" 
                  rows="3" 
                  required
                  placeholder="Enter your question here"
                ></textarea>
              </div>
              
              <div class="options-container">
                <div v-for="n in 4" :key="n" class="option-item mb-3">
                  <label :for="'option' + n" class="form-label d-flex align-items-center">
                    <div class="option-radio me-2">
                      <input 
                        type="radio" 
                        :id="'correct_option' + n" 
                        name="correct_option" 
                        :value="n" 
                        v-model="newQuestion.correct_option"
                        class="form-check-input"
                      >
                    </div>
                    <span>Option {{ n }}</span>
                  </label>
                  <input 
                    type="text" 
                    class="form-control" 
                    :id="'option' + n" 
                    v-model="newQuestion['option' + n]" 
                    required
                    :placeholder="'Enter option ' + n"
                  >
                </div>
              </div>

              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-outline-secondary me-2" @click="showAddForm = false">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                  {{ loading ? 'Adding...' : 'Add Question' }}
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

    <!-- Questions List -->
    <div class="row g-4">
      <div v-if="loading && !questions.length" class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="!questions.length" class="col-12 text-center py-5">
        <div class="empty-state">
          <i class="fas fa-question-circle fa-3x mb-3 text-muted"></i>
          <h4>No Questions Yet</h4>
          <p class="text-muted">Start by adding your first question to this quiz.</p>
          <button class="btn btn-primary" @click="showAddForm = true">
            <i class="fas fa-plus me-2"></i>Add Question
          </button>
        </div>
      </div>
      <div v-else class="col-12">
        <div class="questions-list">
          <div v-for="(question, index) in questions" :key="question.id" class="question-card mb-4">
            <div class="card shadow-sm border-0">
              <div class="card-header bg-light d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Question {{ index + 1 }}</h5>
                <button class="btn btn-outline-danger btn-sm" @click="confirmDelete(question)">
                  <i class="fas fa-trash-alt me-1"></i>Delete
                </button>
              </div>
              <div class="card-body">
                <p class="question-text mb-4">{{ question.question_statement }}</p>
                <div class="options-grid">
                  <div v-for="n in 4" :key="n" 
                    class="option-box" 
                    :class="{ 'correct-option': question.correct_option === n }"
                  >
                    <div class="option-label">Option {{ n }}</div>
                    <div class="option-content">
                      {{ question['option' + n] }}
                      <i v-if="question.correct_option === n" class="fas fa-check-circle text-success ms-2"></i>
                    </div>
                  </div>
                </div>
              </div>
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
            <p>Are you sure you want to delete this question?</p>
            <div class="alert alert-warning">
              <i class="fas fa-exclamation-triangle me-2"></i>
              This action cannot be undone.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelDelete">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteQuestion">
              <i class="fas fa-trash-alt me-1"></i>
              Delete Question
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import userMixin from '../../mixins/userMixin'

export default {
  name: 'QuestionsPage',
  mixins: [userMixin],
  data() {
    return {
      quizTitle: '',
      chapterId: '',
      questions: [],
      newQuestion: {
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: 1
      },
      loading: false,
      error: null,
      showAddForm: false,
      selectedQuestion: null,
      showDeleteModal: false
    }
  },
  created() {
    this.fetchQuizDetails()
    this.fetchQuestions()
  },
  methods: {
    async fetchQuizDetails() {
      try {
        const response = await fetch(`http://localhost:5000/quizzes/${this.$route.params.quizId}`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          const quiz = await response.json()
          this.quizTitle = quiz.title
          this.chapterId = quiz.chapter_id
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = 'Failed to fetch quiz details'
      }
    },
    async fetchQuestions() {
      this.loading = true
      try {
        const response = await fetch(`http://localhost:5000/quizzes/${this.$route.params.quizId}/questions`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.questions = await response.json()
        }
      } catch (error) {
        this.error = 'Failed to fetch questions'
        console.error('Error:', error)
      }
      this.loading = false
    },
    async handleSubmit() {
      this.loading = true
      this.error = null
      try {
        const formData = {
          ...this.newQuestion,
          correct_option: parseInt(this.newQuestion.correct_option)
        }

        const response = await fetch(`http://localhost:5000/quizzes/${this.$route.params.quizId}/questions`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(formData)
        })
        
        const data = await response.json()
        if (response.ok) {
          await this.fetchQuestions()
          this.newQuestion = {
            question_statement: '',
            option1: '',
            option2: '',
            option3: '',
            option4: '',
            correct_option: 1
          }
          this.showAddForm = false
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Question added successfully',
            type: 'success'
          })
        } else {
          this.error = data.error || 'Failed to add question'
        }
      } catch (error) {
        this.error = 'Failed to add question'
        console.error('Error:', error)
      }
      this.loading = false
    },
    confirmDelete(question) {
      this.selectedQuestion = question
      this.showDeleteModal = true
    },
    cancelDelete() {
      this.selectedQuestion = null
      this.showDeleteModal = false
    },
    async deleteQuestion() {
      if (!this.selectedQuestion) return
      
      try {
        const response = await fetch(`http://localhost:5000/questions/${this.selectedQuestion.id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        if (response.ok) {
          await this.fetchQuestions()
          this.showDeleteModal = false
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Question deleted successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to delete question'
        console.error('Error:', error)
      }
      this.selectedQuestion = null
    }
  }
}
</script>

<style scoped>
.questions-page {
  animation: fadeIn 0.3s ease-in-out;
}

.question-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.question-text {
  font-size: 1.1rem;
  color: #2c3e50;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.option-box {
  padding: 1rem;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.option-box:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.option-box.correct-option {
  border-color: #198754;
  background-color: rgba(25, 135, 84, 0.1);
}

.option-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.option-content {
  font-weight: 500;
}

.options-container .option-item {
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s ease;
}

.options-container .option-item:hover {
  border-color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.option-radio {
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  padding: 3rem 1rem;
  color: #6c757d;
}

.empty-state i {
  opacity: 0.5;
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