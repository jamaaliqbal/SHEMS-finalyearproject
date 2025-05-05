<template>
    <div class="d-flex justify-content-center align-items-center bg-light">
        <div class="card">
            <h2 class="card-title">Sign Up</h2>
            <form @submit.prevent="signup">
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="name" class="form-label">Name</label>
                            <input type="text" id="name" v-model="name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" id="email" v-model="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" id="password" v-model="password" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="confirmPassword" class="form-label">Confirm Password</label>
                            <input type="password" id="confirmPassword" v-model="confirmPassword" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="octopusApiKey" class="form-label">Octopus API Key</label>
                            <input type="text" id="octopusApiKey" v-model="octopusApiKey" class="form-control" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label for="octopusProductCode" class="form-label">Octopus Product Code</label>
                            <input type="text" id="octopusProductCode" v-model="octopusProductCode" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="octopusTariffCode" class="form-label">Octopus Tariff Code</label>
                            <input type="text" id="octopusTariffCode" v-model="octopusTariffCode" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="octopusMpan" class="form-label"> Octopus MPAN</label>
                            <input type="text" id="octopusMpan" v-model="octopusMpan" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="octopusSerial" class="form-label">Octopus Serial</label>
                            <input type="text" id="octopusSerial" v-model="octopusSerial" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="solaxApiKey" class="form-label">Solax API Key</label>
                            <input type="text" id="solaxApiKey" v-model="solaxApiKey" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label for="solaxSerial" class="form-label">Solax Serial</label>
                            <input type="text" id="solaxSerial" v-model="solaxSerial" class="form-control" required>
                        </div>
                    </div>
                </div>
                <button id="submit-button" type="submit" class="btn btn-primary">Sign Up</button>
                <p v-if="error" class="error-message">{{ error }}</p>
            </form>
            <div class="login-link">
                <p>Already have an account? <router-link to="/login">Login</router-link></p>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { ref } from 'vue';
import apiClient from '../services/api';
import { useRouter } from 'vue-router';

export default {
    name: 'SignupPage',
    setup() {
        const name = ref('');
        const email = ref('');
        const password = ref('');
        const confirmPassword = ref('');
        const octopusApiKey = ref('');
        const octopusProductCode = ref('');
        const octopusTariffCode = ref('');
        const octopusMpan = ref('');
        const octopusSerial = ref('');
        const solaxApiKey = ref('');
        const solaxSerial = ref('');
        const error = ref('');
        const router = useRouter();

        const signup = async () => {
            if (password.value !== confirmPassword.value) {
                alert("Passwords do not match!");
                error.value = 'Passwords do not match';
                return;
            }

            try {
                await apiClient.post('/accounts/signup/', {
                    name: name.value,
                    email: email.value,
                    password: password.value,
                    confirmPassword: confirmPassword.value,
                    octopus_api_key: octopusApiKey.value,
                    octopus_product_code: octopusProductCode.value,
                    octopus_tariff_code: octopusTariffCode.value,
                    octopus_mpan: octopusMpan.value,
                    octopus_serial: octopusSerial.value,
                    solax_api_key: solaxApiKey.value,
                    solax_serial_number: solaxSerial.value
                })
                router.push('/login'); // Redirect to login page after successful signup
            } catch (err) {
                console.error('Signup failed:', err);
                error.value = 'Signup failed. Please check your credentials.'
            }
        }

        return { name, email, password, confirmPassword, octopusApiKey, octopusProductCode, octopusTariffCode, octopusMpan, octopusSerial, solaxApiKey, solaxSerial, error, signup };
    }
}

</script>

<style scoped>
.card {
    width: 100%;
    max-width: 600px;
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
.login-link {
    text-align: center;
    margin-top: 15px;
}
</style>