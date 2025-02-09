<template>
  <div>
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h3>{{ quiz.title }}</h3>
            <div class="timer" v-if="timeLeft">
              Time Left: {{ formatTime(timeLeft) }}
            </div>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="!started" class="text-center py-4">
              <h4>Quiz Instructions</h4>
              <p>Duration: {{ quiz.time_duration }} minutes</p>
              <p>Total Questions: {{ questions.length }}</p>
              <button class="btn btn-primary btn-lg" @click="startQuiz">
                Start Quiz
              </button>
            </div>
            <div v-else>
              <form @submit.prevent="submitQuiz">
                <div v-for="(question, index) in questions" :key="question.id" class="mb-4">
                  <div class="card">
                    <div class="card-body">
                      <h5 class="card-title">Question {{ index + 1 }}</h5>
                      <p class="card-text">{{ question.question_statement }}</p>
                      <div class="options">
                        <div class="form-check mb-2" v-for="n in 4" :key="n">
                          <input 
                            class="form-check-input" 
                            type="radio" 
                            :name="'question_' + question.id" 
                            :id="'option' + n + '_' + question.id"
                            :value="n"
                            v-model="answers[question.id]"
                          >
                          <label class="form-check-label" :for="'option' + n + '_' + question.id">
                            {{ question['option' + n] }}
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-primary btn-lg" :disabled="submitting">
                    {{ submitting ? 'Submitting...' : 'Submit Quiz' }}
                  </button>
                </div>
              </form>
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
  name: 'AttemptQuiz',
  mixins: [userMixin],
  data() {
    return {
      quiz: {},
      questions: [],
      answers: {},
      started: false,
      timeLeft: 0,
      timer: null,
      error: null,
      submitting: false
    }
  },
  created() {
    this.fetchQuizDetails()
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    },
    async fetchQuizDetails() {
      try {
        const response = await fetch(`http://localhost:5000/quizzes/${this.$route.params.quizId}/questions`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          const data = await response.json()
          this.questions = data
          this.quiz = {
            title: 'Quiz',  // This should come from API
            time_duration: 30  // This should come from API
          }
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to fetch quiz details'
        console.error('Error:', error)
      }
    },
    startQuiz() {
      this.started = true
      this.timeLeft = this.quiz.time_duration * 60
      this.timer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this.submitQuiz()
        }
      }, 1000)
    },
    async submitQuiz() {
      if (this.timer) {
        clearInterval(this.timer)
      }
      
      this.submitting = true
      try {
        const response = await fetch(`http://localhost:5000/quizzes/${this.$route.params.quizId}/attempt`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify({ answers: this.answers })
        })
        
        if (response.ok) {
          const result = await response.json()
          this.$router.push({
            path: '/my-scores',
            query: { message: `Quiz submitted successfully! Score: ${result.score}` }
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to submit quiz'
        console.error('Error:', error)
      }
      this.submitting = false
    }
  }
}
</script>

<style scoped>
.timer {
  font-size: 1.2rem;
  font-weight: bold;
  color: #dc3545;
}
</style> 