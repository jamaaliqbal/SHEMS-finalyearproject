import { createRouter, createWebHistory } from "vue-router";

import EnergyData from "../components/EnergyData.vue";
import HomePage from "../pages/HomePage.vue";
import EnergyPage from "../pages/EnergyPage.vue";
import WeatherView from "../components/WeatherView.vue";
import AutomationsPage from "../pages/AutomationsPage.vue";
import SignupPage from "../pages/SignupPage.vue";
import LoginPage from "../pages/LoginPage.vue";
import CommunityPage from "../pages/CommunityPage.vue";


const router = createRouter({
    history: createWebHistory(),
    routes: [
        {   path: "/", name: "home", component: HomePage },
        {   path: "/energy", name: "energy", component: EnergyPage },
        {   path: "/energy-data", name: "energy-data", component: EnergyData },
        {   path: "/weather", name: "weather", component: WeatherView },
        {   path: "/automation", name: "automation", component: AutomationsPage },
        {   path: "/signup", name: "signup", component: SignupPage},
        {   path: "/login", name: "login", component: LoginPage},
        {   path: "/community", name: "community", component: CommunityPage},
    ]
})

export default router;