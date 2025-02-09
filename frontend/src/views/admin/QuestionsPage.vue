<template>
  <div>
    <h2>Manage Questions for {{ quizTitle }}</h2>
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h4>Add New Question</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="question_statement" class="form-label">Question</label>
                <textarea 
                  class="form-control" 
                  id="question_statement" 
                  v-model="newQuestion.question_statement" 
                  rows="3" 
                  required
                ></textarea>
              </div>
              <div class="mb-3">
                <label for="option1" class="form-label">Option 1</label>
                <input type="text" class="form-control" id="option1" v-model="newQuestion.option1" required>
              </div>
              <div class="mb-3">
                <label for="option2" class="form-label">Option 2</label>
                <input type="text" class="form-control" id="option2" v-model="newQuestion.option2" required>
              </div>
              <div class="mb-3">
                <label for="option3" class="form-label">Option 3</label>
                <input type="text" class="form-control" id="option3" v-model="newQuestion.option3" required>
              </div>
              <div class="mb-3">
                <label for="option4" class="form-label">Option 4</label>
                <input type="text" class="form-control" id="option4" v-model="newQuestion.option4" required>
              </div>
              <div class="mb-3">
                <label for="correct_option" class="form-label">Correct Option</label>
                <select class="form-select" id="correct_option" v-model="newQuestion.correct_option" required>
                  <option value="1">Option 1</option>
                  <option value="2">Option 2</option>
                  <option value="3">Option 3</option>
                  <option value="4">Option 4</option>
                </select>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Adding...' : 'Add Question' }}
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
            <h4>Question List</h4>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-for="question in questions" :key="question.id" class="card mb-3">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <h5 class="card-title">{{ question.question_statement }}</h5>
                  <button class="btn btn-danger btn-sm" @click="deleteQuestion(question.id)">Delete</button>
                </div>
                <div class="mt-3">
                  <div class="form-check mb-2" v-for="n in 4" :key="n">
                    <input 
                      class="form-check-input" 
                      type="radio" 
                      :name="'question_' + question.id" 
                      :id="'option' + n + '_' + question.id"
                      :checked="question.correct_option === n"
                      disabled
                    >
                    <label class="form-check-label" :for="'option' + n + '_' + question.id">
                      {{ question['option' + n] }}
                    </label>
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

export default {
  name: 'QuestionsPage',
  mixins: [userMixin],
  data() {
    return {
      quizTitle: '',
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
      error: null
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
        }
      } catch (error) {
        console.error('Error:', error)
      }
    },
    async fetchQuestions() {
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
        } else {
          this.error = data.error || 'Failed to add question'
        }
      } catch (error) {
        this.error = 'Failed to add question'
        console.error('Error:', error)
      }
      this.loading = false
    },
    async deleteQuestion(id) {
      if (!confirm('Are you sure you want to delete this question?')) return
      
      try {
        const response = await fetch(`http://localhost:5000/questions/${id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        if (response.ok) {
          await this.fetchQuestions()
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to delete question'
        console.error('Error:', error)
      }
    }
  }
}
</script>

<style scoped>
.form-check-input:checked {
  background-color: #198754;
  border-color: #198754;
}
</style> 