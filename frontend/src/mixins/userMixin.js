const API_URL = 'http://localhost:5000'

export default {
    data() {
        return {
            user: null,
            isLoggedIn: false,
            isAdmin: false
        }
    },
    created() {
        this.checkAuth()
    },
    methods: {
        async checkAuth() {
            const token = localStorage.getItem('token')
            const userRole = localStorage.getItem('userRole')
            if (token) {
                try {
                    // Validate token by making a request
                    const response = await fetch(`${API_URL}/available-quizzes`, {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    })
                    
                    if (response.ok) {
                        this.isLoggedIn = true
                        this.isAdmin = userRole === 'admin'
                        // Redirect if on login/register page
                        if (this.$route && (this.$route.path === '/login' || this.$route.path === '/register')) {
                            this.$router.push(this.isAdmin ? '/admin/subjects' : '/quizzes')
                        }
                    } else if (response.status === 401) {
                        // Token is invalid or expired
                        this.handleLogout()
                    }
                } catch (error) {
                    console.error('Auth check failed:', error)
                }
            } else if (this.$route && this.$route.meta.requiresAuth) {
                this.$router.push('/login')
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
                    this.isLoggedIn = true
                    this.isAdmin = data.role === 'admin'
                    return { success: true }
                } else {
                    return { success: false, error: data.error }
                }
            } catch (error) {
                console.error('Login failed:', error)
                return { success: false, error: 'Login failed. Please try again.' }
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
