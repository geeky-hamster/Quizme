<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import userMixin from '@/mixins/userMixin'

export default {
    name: 'NavBar',
    mixins: [userMixin],
    setup() {
        const router = useRouter()
        const isLoggedIn = ref(false)
        const isAdmin = ref(false)

        const handleAuthStateChange = (event) => {
            isLoggedIn.value = event.detail.isLoggedIn
            isAdmin.value = event.detail.isAdmin
        }

        onMounted(() => {
            window.addEventListener('auth-state-changed', handleAuthStateChange)
            // Initial check
            const token = localStorage.getItem('token')
            const userRole = localStorage.getItem('userRole')
            if (token) {
                isLoggedIn.value = true
                isAdmin.value = userRole === 'admin'
            }
        })

        onBeforeUnmount(() => {
            window.removeEventListener('auth-state-changed', handleAuthStateChange)
        })

        const handleLogout = () => {
            localStorage.removeItem('token')
            localStorage.removeItem('userRole')
            isLoggedIn.value = false
            isAdmin.value = false
            router.push('/login')
        }

        return {
            isLoggedIn,
            isAdmin,
            handleLogout
        }
    }
}
</script>

<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <router-link class="navbar-brand d-flex align-items-center" to="/">
                <i class="fas fa-graduation-cap me-2"></i>
                Quiz Master
            </router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <template v-if="isLoggedIn && isAdmin">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin/dashboard">
                                <i class="fas fa-tachometer-alt me-1"></i> Dashboard
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin/statistics">
                                <i class="fas fa-chart-line me-1"></i> Analytics
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin/subjects">
                                <i class="fas fa-book me-1"></i> Manage Subjects
                            </router-link>
                        </li>
                    </template>
                    <template v-if="isLoggedIn && !isAdmin">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/dashboard">
                                <i class="fas fa-tachometer-alt me-1"></i> Dashboard
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/user/statistics">
                                <i class="fas fa-chart-line me-1"></i> My Performance
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/quizzes">
                                <i class="fas fa-tasks me-1"></i> Available Quizzes
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/my-scores">
                                <i class="fas fa-chart-bar me-1"></i> My Scores
                            </router-link>
                        </li>
                    </template>
                </ul>
                <ul class="navbar-nav">
                    <template v-if="!isLoggedIn">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/login">
                                <i class="fas fa-sign-in-alt me-1"></i> Login
                            </router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/register">
                                <i class="fas fa-user-plus me-1"></i> Register
                            </router-link>
                        </li>
                    </template>
                    <li class="nav-item" v-else>
                        <a class="nav-link" href="#" @click.prevent="handleLogout">
                            <i class="fas fa-sign-out-alt me-1"></i> Logout
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.navbar {
    padding: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: 600;
}

.nav-link {
    font-weight: 500;
    padding: 0.5rem 1rem;
    transition: all 0.3s ease;
}

.nav-link:hover {
    transform: translateY(-1px);
}

.router-link-active {
    font-weight: 600;
    position: relative;
}

.router-link-active::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 1rem;
    right: 1rem;
    height: 2px;
    background-color: currentColor;
    border-radius: 2px;
}
</style>