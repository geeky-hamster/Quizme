<script setup lang="ts">

</script>

<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <router-link class="navbar-brand" to="/">Quiz Master</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item" v-if="isLoggedIn && isAdmin">
                        <router-link class="nav-link" to="/admin/subjects">Manage Subjects</router-link>
                    </li>
                    <li class="nav-item" v-if="isLoggedIn && !isAdmin">
                        <router-link class="nav-link" to="/quizzes">Available Quizzes</router-link>
                    </li>
                    <li class="nav-item" v-if="isLoggedIn && !isAdmin">
                        <router-link class="nav-link" to="/my-scores">My Scores</router-link>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <template v-if="!isLoggedIn">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/login">Login</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/register">Register</router-link>
                        </li>
                    </template>
                    <li class="nav-item" v-else>
                        <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<script>
import userMixin from '../mixins/userMixin'

export default {
    name: 'NavBar',
    mixins: [userMixin]
}
</script>

<style scoped>
.navbar-nav .router-link-active {
    font-weight: bold;
}
</style>