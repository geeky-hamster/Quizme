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
                this.isLoggedIn = true
                this.isAdmin = userRole === 'admin'
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
        logout() {
            localStorage.removeItem('token')
            localStorage.removeItem('userRole')
            this.user = null
            this.isLoggedIn = false
            this.isAdmin = false
            this.$router.push('/login')
        },
        getAuthHeaders() {
            const token = localStorage.getItem('token')
            return {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }
    }
}
