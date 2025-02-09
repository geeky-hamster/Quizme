const API_URL = 'http://localhost:5000'
import { ref, watch } from 'vue'

export default {
    data() {
        return {
            user: null,
            isLoggedIn: ref(false),
            isAdmin: ref(false)
        }
    },
    created() {
        this.checkAuth()
        
        // Listen for auth state changes
        window.addEventListener('auth-state-changed', this.handleAuthStateChange)
        
        // Watch localStorage changes
        watch(() => localStorage.getItem('token'), () => {
            this.checkAuth()
        })
        watch(() => localStorage.getItem('userRole'), () => {
            this.checkAuth()
        })
    },
    beforeUnmount() {
        window.removeEventListener('auth-state-changed', this.handleAuthStateChange)
    },
    methods: {
        handleAuthStateChange(event) {
            this.isLoggedIn = event.detail.isLoggedIn
            this.isAdmin = event.detail.isAdmin
        },
        async checkAuth() {
            const token = localStorage.getItem('token')
            const userRole = localStorage.getItem('userRole')
            
            if (token) {
                try {
                    const response = await fetch(`${API_URL}/available-quizzes`, {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    })
                    
                    if (response.ok) {
                        this.isLoggedIn = true
                        this.isAdmin = userRole === 'admin'
                        
                        // Emit auth state change event
                        window.dispatchEvent(new CustomEvent('auth-state-changed', {
                            detail: { 
                                isLoggedIn: true, 
                                isAdmin: userRole === 'admin' 
                            }
                        }))
                    } else if (response.status === 401) {
                        this.handleLogout()
                    }
                } catch (error) {
                    console.error('Auth check failed:', error)
                }
            } else {
                this.isLoggedIn = false
                this.isAdmin = false
                if (this.$route && this.$route.meta.requiresAuth) {
                    this.$router.push('/login')
                }
            }
        },
        async login(username, password) {
            try {
                const response = await fetch(`${API_URL}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                })
                const data = await response.json()
                
                if (response.ok) {
                    localStorage.setItem('token', data.access_token)
                    localStorage.setItem('userRole', data.role)
                    
                    return { 
                        success: true,
                        role: data.role 
                    }
                } else {
                    return { 
                        success: false, 
                        error: data.error 
                    }
                }
            } catch (error) {
                console.error('Login failed:', error)
                return { 
                    success: false, 
                    error: 'Login failed. Please try again.' 
                }
            }
        },
        async register(userData) {
            try {
                const response = await fetch(`${API_URL}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                })
                const data = await response.json()
                if (response.ok) {
                    return { success: true }
                } else {
                    return { success: false, error: data.error }
                }
            } catch (error) {
                console.error('Registration failed:', error)
                return { success: false, error: 'Registration failed. Please try again.' }
            }
        },
        handleLogout() {
            localStorage.removeItem('token')
            localStorage.removeItem('userRole')
            this.user = null
            this.isLoggedIn = false
            this.isAdmin = false
            
            // Emit auth state change event
            window.dispatchEvent(new CustomEvent('auth-state-changed', {
                detail: { 
                    isLoggedIn: false, 
                    isAdmin: false 
                }
            }))
            
            if (this.$route && this.$route.meta.requiresAuth) {
                this.$router.push('/login')
            }
        },
        async makeAuthenticatedRequest(url, options = {}) {
            const token = localStorage.getItem('token')
            if (!token) {
                this.handleLogout()
                return null
            }

            try {
                const response = await fetch(url, {
                    ...options,
                    headers: {
                        ...options.headers,
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                })

                if (response.status === 401) {
                    this.handleLogout()
                    return null
                }

                return response
            } catch (error) {
                console.error('Request failed:', error)
                return null
            }
        },
        getAuthHeaders() {
            const token = localStorage.getItem('token')
            if (!token) {
                this.handleLogout()
                return {}
            }
            return {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }
    }
}
