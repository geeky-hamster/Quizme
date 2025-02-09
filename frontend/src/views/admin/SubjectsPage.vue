<template>
  <div class="subjects-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-book me-2"></i>
        Manage Subjects
      </h2>
      <button class="btn btn-primary" @click="showAddForm = !showAddForm">
        <i class="fas" :class="showAddForm ? 'fa-minus' : 'fa-plus'"></i>
        {{ showAddForm ? 'Hide Form' : 'Add New Subject' }}
      </button>
    </div>

    <!-- Add Subject Form -->
    <div class="row mb-4" v-if="showAddForm">
      <div class="col-md-8">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">
              <i class="fas fa-plus-circle me-2"></i>
              Add New Subject
            </h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="name" class="form-label">Subject Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="name" 
                  v-model="newSubject.name" 
                  required
                  placeholder="Enter subject name"
                >
              </div>
              <div class="mb-3">
                <label for="description" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="description" 
                  v-model="newSubject.description" 
                  rows="3"
                  placeholder="Enter subject description"
                ></textarea>
              </div>
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-outline-secondary me-2" @click="showAddForm = false">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                  {{ loading ? 'Adding...' : 'Add Subject' }}
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

    <!-- Subjects List -->
    <div class="row">
      <div class="col-12">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <h4 class="mb-0">
                <i class="fas fa-list me-2"></i>
                Subject List
              </h4>
              <div class="input-group" style="width: 300px;">
                <span class="input-group-text">
                  <i class="fas fa-search"></i>
                </span>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="searchQuery" 
                  placeholder="Search subjects..."
                >
              </div>
            </div>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loading && !subjects.length">
                    <td colspan="3" class="text-center py-4">
                      <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-else-if="!filteredSubjects.length">
                    <td colspan="3" class="text-center py-4 text-muted">
                      <i class="fas fa-inbox fa-2x mb-2"></i>
                      <p class="mb-0">No subjects found</p>
                    </td>
                  </tr>
                  <tr v-for="subject in filteredSubjects" :key="subject.id" class="subject-row">
                    <td>
                      <span class="fw-medium">{{ subject.name }}</span>
                    </td>
                    <td>
                      <p class="text-muted mb-0">{{ subject.description || 'No description available' }}</p>
                    </td>
                    <td>
                      <div class="btn-group">
                        <router-link 
                          :to="'/admin/subjects/' + subject.id + '/chapters'" 
                          class="btn btn-outline-primary btn-sm"
                          title="Manage Chapters"
                        >
                          <i class="fas fa-book-open me-1"></i>
                          Chapters
                        </router-link>
                        <button 
                          class="btn btn-outline-secondary btn-sm"
                          @click="editSubject(subject)"
                          title="Edit Subject"
                        >
                          <i class="fas fa-edit"></i>
                        </button>
                        <button 
                          class="btn btn-outline-danger btn-sm" 
                          @click="confirmDelete(subject)"
                          title="Delete Subject"
                        >
                          <i class="fas fa-trash-alt"></i>
                        </button>
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
            Are you sure you want to delete the subject "{{ selectedSubject?.name }}"?
            This action cannot be undone.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelDelete">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteSubject">
              <i class="fas fa-trash-alt me-1"></i>
              Delete Subject
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Subject Modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show"></div>
    <div v-if="showEditModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Subject</h5>
            <button type="button" class="btn-close" @click="cancelEdit"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateSubject">
              <div class="mb-3">
                <label for="edit-name" class="form-label">Subject Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="edit-name" 
                  v-model="editingSubject.name" 
                  required
                >
              </div>
              <div class="mb-3">
                <label for="edit-description" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="edit-description" 
                  v-model="editingSubject.description" 
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
  name: 'SubjectsPage',
  mixins: [userMixin],
  data() {
    return {
      subjects: [],
      newSubject: {
        name: '',
        description: ''
      },
      loading: false,
      error: null,
      showAddForm: false,
      searchQuery: '',
      selectedSubject: null,
      showDeleteModal: false,
      showEditModal: false,
      editingSubject: null
    }
  },
  computed: {
    filteredSubjects() {
      if (!this.searchQuery) return this.subjects
      const query = this.searchQuery.toLowerCase()
      return this.subjects.filter(subject => 
        subject.name.toLowerCase().includes(query) ||
        (subject.description && subject.description.toLowerCase().includes(query))
      )
    }
  },
  mounted() {
    this.fetchSubjects()
  },
  methods: {
    async fetchSubjects() {
      this.loading = true
      try {
        const response = await fetch('http://localhost:5000/subjects', {
          headers: this.getAuthHeaders()
        })
        if (response.ok) {
          this.subjects = await response.json()
        }
      } catch (error) {
        this.error = 'Failed to fetch subjects'
        console.error('Error:', error)
      }
      this.loading = false
    },
    async handleSubmit() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('http://localhost:5000/subjects', {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(this.newSubject)
        })
        
        if (response.ok) {
          await this.fetchSubjects()
          this.newSubject.name = ''
          this.newSubject.description = ''
          this.showAddForm = false
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Subject added successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to add subject'
        console.error('Error:', error)
      }
      this.loading = false
    },
    confirmDelete(subject) {
      this.selectedSubject = subject
      this.showDeleteModal = true
    },
    cancelDelete() {
      this.selectedSubject = null
      this.showDeleteModal = false
    },
    async deleteSubject() {
      if (!this.selectedSubject) return
      
      try {
        const response = await fetch(`http://localhost:5000/subjects/${this.selectedSubject.id}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        })
        
        if (response.ok) {
          await this.fetchSubjects()
          this.showDeleteModal = false
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Subject deleted successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to delete subject'
        console.error('Error:', error)
      }
      this.selectedSubject = null
    },
    editSubject(subject) {
      this.editingSubject = { ...subject }
      this.showEditModal = true
    },
    cancelEdit() {
      this.editingSubject = null
      this.showEditModal = false
    },
    async updateSubject() {
      if (!this.editingSubject) return
      
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch(`http://localhost:5000/subjects/${this.editingSubject.id}`, {
          method: 'PUT',
          headers: this.getAuthHeaders(),
          body: JSON.stringify({
            name: this.editingSubject.name,
            description: this.editingSubject.description
          })
        })
        
        if (response.ok) {
          await this.fetchSubjects()
          this.showEditModal = false
          this.editingSubject = null
          // Show success toast
          this.$root.$emit('show-toast', {
            message: 'Subject updated successfully',
            type: 'success'
          })
        } else {
          const data = await response.json()
          this.error = data.error
        }
      } catch (error) {
        this.error = 'Failed to update subject'
        console.error('Error:', error)
      }
      this.loading = false
    }
  }
}
</script>

<style scoped>
.subjects-page {
  animation: fadeIn 0.3s ease-in-out;
}

.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.subject-row {
  transition: background-color 0.2s ease;
}

.subject-row:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.btn-group .btn {
  transition: all 0.2s ease;
}

.btn-group .btn:hover {
  transform: translateY(-1px);
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

/* Custom scrollbar for table */
.table-responsive {
  scrollbar-width: thin;
  scrollbar-color: var(--bs-primary) #f8f9fa;
}

.table-responsive::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-responsive::-webkit-scrollbar-track {
  background: #f8f9fa;
  border-radius: 4px;
}

.table-responsive::-webkit-scrollbar-thumb {
  background-color: var(--bs-primary);
  border-radius: 4px;
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