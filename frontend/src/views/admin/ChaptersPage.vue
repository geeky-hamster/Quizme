<template>
  <div class="chapters-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1">
          <i class="fas fa-book-open me-2"></i>
          {{ subjectName }}
        </h2>
        <p class="text-muted mb-0">Manage chapters for this subject</p>
      </div>
      <div class="d-flex gap-2">
        <router-link to="/admin/subjects" class="btn btn-outline-secondary">
          <i class="fas fa-arrow-left me-2"></i>Back to Subjects
        </router-link>
        <button class="btn btn-primary" @click="showAddForm = !showAddForm">
          <i class="fas" :class="showAddForm ? 'fa-minus' : 'fa-plus'"></i>
          {{ showAddForm ? 'Hide Form' : 'Add New Chapter' }}
        </button>
      </div>
    </div>

    <!-- Add Chapter Form -->
    <div class="row mb-4" v-if="showAddForm">
      <div class="col-md-8">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">
              <i class="fas fa-plus-circle me-2"></i>
              Add New Chapter
            </h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="name" class="form-label">Chapter Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="name" 
                  v-model="newChapter.name" 
                  required
                  placeholder="Enter chapter name"
                >
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="description" 
                  v-model="newChapter.description" 
                  rows="3"
                  placeholder="Enter chapter description"
                ></textarea>
              </div>
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-outline-secondary me-2" @click="showAddForm = false">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                  {{ loading ? 'Adding...' : 'Add Chapter' }}
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

    <!-- Chapters Grid -->
    <div class="row g-4">
      <div v-if="loading && !chapters.length" class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="!chapters.length" class="col-12 text-center py-5">
        <div class="empty-state">
          <i class="fas fa-book fa-3x mb-3 text-muted"></i>
          <h4>No Chapters Yet</h4>
          <p class="text-muted">Start by adding your first chapter to this subject.</p>
          <button class="btn btn-primary" @click="showAddForm = true">
            <i class="fas fa-plus me-2"></i>Add Chapter
          </button>
        </div>
      </div>
      <div v-for="chapter in chapters" :key="chapter.id" class="col-md-6 col-lg-4">
        <div class="card h-100 chapter-card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h5 class="card-title mb-1">{{ chapter.name }}</h5>
              <div class="dropdown">
                <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li>
                    <router-link :to="'/admin/chapters/' + chapter.id + '/quizzes'" class="dropdown-item">
                      <i class="fas fa-tasks me-2"></i>Manage Quizzes
                    </router-link>
                  </li>
                  <li>
                    <button class="dropdown-item" @click="editChapter(chapter)">
                      <i class="fas fa-edit me-2"></i>Edit
                    </button>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <button class="dropdown-item text-danger" @click="confirmDelete(chapter)">
                      <i class="fas fa-trash-alt me-2"></i>Delete
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            <p class="card-text text-muted">
              {{ chapter.description || 'No description available' }}
            </p>
            <div class="mt-3">
              <router-link :to="'/admin/chapters/' + chapter.id + '/quizzes'" class="btn btn-outline-primary btn-sm">
                <i class="fas fa-tasks me-1"></i>
                Manage Quizzes
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
            Are you sure you want to delete the chapter "{{ selectedChapter?.name }}"?
            This action cannot be undone and will delete all associated quizzes.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelDelete">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteChapter">
              <i class="fas fa-trash-alt me-1"></i>
              Delete Chapter
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Chapter Modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show"></div>
    <div v-if="showEditModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Chapter</h5>
            <button type="button" class="btn-close" @click="cancelEdit"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateChapter">
              <div class="mb-3">
                <label for="edit-name" class="form-label">Chapter Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="edit-name" 
                  v-model="editingChapter.name" 
                  required
                >
              </div>
              <div class="mb-3">
                <label for="edit-description" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="edit-description" 
                  v-model="editingChapter.description" 
                  rows="3"
                ></textarea>
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

export default {
  name: 'ChaptersPage',
  mixins: [userMixin],
  data() {
    return {
      subjectName: '',
      chapters: [],
      newChapter: {
        name: '',
        description: ''
      },
      loading: false,
      error: null,
      showAddForm: false,
      selectedChapter: null,
      showDeleteModal: false,
      showEditModal: false,
      editingChapter: null,
    }
  },
  created() {
    this.fetchSubjectDetails()
    this.fetchChapters()
  },
  methods: {
    async fetchSubjectDetails() {
      try {
        const response = await fetch(`http://localhost:5000/subjects/${this.$route.params.subjectId}`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          const subject = await response.json()
          this.subjectName = subject.name
        }
      } catch (error) {
        console.error('Error:', error)
        this.error = 'Failed to fetch subject details'
      }
    },
    async fetchChapters() {
      this.loading = true
      try {
        const response = await fetch(`http://localhost:5000/subjects/${this.$route.params.subjectId}/chapters`, {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.chapters = await response.json()
        }
      } catch (error) {
        this.error = 'Failed to fetch chapters'
        console.error('Error:', error)
      }
      this.loading = false
    },
    async handleSubmit() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch(`http://localhost:5000/subjects/${this.$route.params.subjectId}/chapters`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(this.newChapter)
        })
        
        if (response.ok) {
          await this.fetchChapters()
          this.newChapter.name = ''
          this.newChapter.description = ''
          this.showAddForm = false
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Chapter added successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to add chapter'
        console.error('Error:', error)
      }
      this.loading = false
    },
    confirmDelete(chapter) {
      this.selectedChapter = chapter
      this.showDeleteModal = true
    },
    cancelDelete() {
      this.selectedChapter = null
      this.showDeleteModal = false
    },
    async deleteChapter() {
      if (!this.selectedChapter) return
      
      try {
        const response = await fetch(`http://localhost:5000/chapters/${this.selectedChapter.id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        if (response.ok) {
          await this.fetchChapters()
          this.showDeleteModal = false
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Chapter deleted successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to delete chapter'
        console.error('Error:', error)
      }
      this.selectedChapter = null
    },
    editChapter(chapter) {
      this.editingChapter = { ...chapter }
      this.showEditModal = true
    },
    cancelEdit() {
      this.editingChapter = null
      this.showEditModal = false
    },
    async updateChapter() {
      if (!this.editingChapter) return
      
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch(`http://localhost:5000/chapters/${this.editingChapter.id}`, {
          method: 'PUT',
          headers: this.getAuthHeaders(),
          body: JSON.stringify({
            name: this.editingChapter.name,
            description: this.editingChapter.description
          })
        })
        
        if (response.ok) {
          await this.fetchChapters()
          this.showEditModal = false
          this.editingChapter = null
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Chapter updated successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to update chapter'
        console.error('Error:', error)
      }
      this.loading = false
    }
  }
}
</script>

<style scoped>
.chapters-page {
  animation: fadeIn 0.3s ease-in-out;
}

.chapter-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.chapter-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
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