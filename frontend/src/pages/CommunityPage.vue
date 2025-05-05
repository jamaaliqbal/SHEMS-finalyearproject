<template>
    <NavBar/>
    <div class="container py-4">
        <h1 class="text-center text-primary mb-4">Community Page</h1>
        <div class="alert alert-info text-center shadow-sm">
            <p class="mb-0">
                This is the community page, where you can post your energy saving strategies and automation rules for others to see.
                <br>Feel free to share your posts and have a look at what others are doing as well
            </p>
        </div>
        <!-- Submit post card-->
        <div class="card shadow-sm mb-4">
            <div class="card-body">
                <h4 class="card-title">Submit a Post</h4>
                <div class="mb-3">
                    <label for="postMessage" class="form-label">Strategy Message</label>
                    <textarea v-model="message" placeholder="Describe your strategy here..."></textarea>
                </div>
                
                <h5>Select Automation Rules to Share:</h5>
                <div class="form-check" v-for="rule in userAutomationRules" :key="rule.id" >
                    <input class="form-check-input" type="checkbox" :value="rule.id" v-model="selectedRuleIds"/>
                    <label class="form-check-label" :for="'rule-'+ rule.id">
                        <strong>{{ rule.device_name }}</strong> : {{ Array.isArray(rule.days) ? rule.days.join(', ') : rule.days }} - {{ rule.valid_from }} to {{ rule.valid_to }}
                    </label>
                </div>
                <button @click="submitPost" class="btn btn-primary mt-3">Submit Post</button>
            </div>
        </div>
        <!-- Community feed card-->
        <div class="card shadow-sm">
            <div class="card-body">
                <h4 class="card-title">Community Feed</h4>
                <div v-if="communityPosts.length === 0" class="text-muted">No Posts yet</div>
                <div v-else>
                    <div v-for="post in communityPosts" :key="post.id" class="border rounded p-3 mb-3 bg-light">
                        <div class="d-flex justify-content-between">
                            <strong>{{ post.user.name }}</strong> - 
                            <small class="text-muted">{{ new Date(post.created_at).toLocaleString('en-GB', { dateStyle: 'short', timeStyle: 'short' }) }}</small>
                        </div>
                        <p class="mt-2">{{ post.message }}</p>
                        <div v-if="post.automation_rules.length">
                            <p><strong>Shared Automation Rules:</strong></p>
                            <ul class="mb-0">
                                <li v-for="rule in post.automation_rules" :key="rule.id">
                                    <strong>{{ rule.device.name }}</strong> : {{ Array.isArray(rule.days_of_week) ? rule.days_of_week.join(', ') : rule.days_of_week }} - {{ rule.start_time }} to {{ rule.end_time }}
                                </li>
                            </ul>
                        </div>
                    </div> 
                </div>
                
            </div>
        </div>    
    </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import NavBar from '../components/NavBar.vue';
import apiClient from '../services/api';

const user = ref<any>(null);
const message = ref<string>('');
const selectedRuleIds = ref<number[]>([]);
const userAutomationRules = ref<any[]>([]);
const communityPosts = ref<any[]>([]);

const loadCommunityPosts = async () => {
    const response = (await apiClient.get("/api/get-community-posts/")).data;
    communityPosts.value = response;
    console.log(communityPosts.value);
};

const submitPost = async () => {
    const payload = {
        user_id: user.value.id,
        message: message.value,
        rule_ids: selectedRuleIds.value
    };
    // await apiClient.post("/api/create-community-post/", payload);
    await fetch("http://127.0.0.1:8000/api/create-community-post/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken") || ""  // Ensure it is a string
        },
        credentials: "include", // Important for session auth
        body: JSON.stringify(payload),
    });
    message.value = '';
    selectedRuleIds.value = [];
    loadCommunityPosts();
};

function getCookie(name: string): string | null {
  let cookieValue: string | null = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

onMounted(async () => {
    // await apiClient.get("/csrf-cookie/");
    user.value = (await apiClient.get("/api/current-user/")).data;
    console.log(user.value);
    const automationRules = (await apiClient.get("/api/get-automation-rules/")).data;
    console.log(automationRules);
    userAutomationRules.value = (await apiClient.get("/api/get-automation-rules/")).data.filter((rule: any) => rule.user_id === user.value.id);
    console.log(userAutomationRules.value);
    loadCommunityPosts();
});
</script>

<style scoped>
textarea {
  width: 100%;
  height: 100px;
  margin-bottom: 1rem;
  resize: vertical;
  min-height: 100px;
}
</style>