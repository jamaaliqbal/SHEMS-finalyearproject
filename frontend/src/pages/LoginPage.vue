<template>
    <div class="d-flex justify-content-center align-items-center bg-light">
        <div class="card">
            <h2 class="card-title">Login</h2>
            <form @submit.prevent="login">
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="text" id="email" v-model="email" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" id="password" v-model="password" class="form-control" required>
                </div>
                <button id="submit-button" type="submit" class="btn btn-primary">Login</button>
                <p v-if="error" class="error-message">{{ error }}</p>
            </form>
            <div class="signup-link">
                <p>Don't have an account? <router-link to="/signup">Sign Up</router-link></p>
            </div>
        </div>
    </div>
    
</template>

<script lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../services/api';
import { useRouter } from 'vue-router';

export default {
    name: 'LoginPage',
    setup() {
        const email = ref('');
        const password = ref('');
        const router = useRouter();
        const error = ref('')

        const fetchCsrfToken = async () => {
            try {
                await apiClient.get('/csrf-token/');
                console.log('CSRF token fetched successfully');
            } catch (error) {
                console.error('Error fetching CSRF token:', error);
            }
        }

        const login = async () => {
            try{
                await apiClient.post('/accounts/login/', {
                    email: email.value,
                    password: password.value
                });
                router.push('/energy'); // Redirect to home page after successful login
            } catch (err) {
                console.error('Login failed:', err);
                alert('Login failed. Please check your credentials.');
                error.value = "'Invalid credentials'"
            }
        }

        onMounted(() => {
            fetchCsrfToken(); // Fetch CSRF token when the component is mounted
        });
        return { email, password, login };
    }
}



</script>

<style scoped>
.card {
    width: 100%;
    max-width: 400px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.card-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}
.btn-primary {
    width: 100%;
}
.signup-link {
    text-align: center;
    margin-top: 15px;
}
</style>
