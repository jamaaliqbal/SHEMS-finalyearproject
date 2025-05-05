import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
// import BootstrapVueNext from 'bootstrap-vue-next';

import 'bootstrap/dist/css/bootstrap.min.css';
import "bootstrap-vue/dist/bootstrap-vue.css";
import 'bootstrap';

// createApp(App).mount('#app')

const app = createApp(App);
app.use(router);
// app.use(BootstrapVueNext);
app.mount("#app")

