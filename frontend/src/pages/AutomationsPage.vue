<template>
    <NavBar/>
    <div class="container py-4">
        <h1 class="text-center text-primary mb-3">Automations</h1>
        <div class="alert alert-info text-center shadow-sm">
            <p class="mb-0">
                This page allows you to control and schedule when your home devices are turned on based on the cheapest electricity prices.
                <br />Create devices, set automation rules, and manage their activation status.
            </p>
        </div>
        <!--Device Form-->
        <div class="card shadow-sm mb-4">
            <div class="card-body">
                <h4 class="card-title">{{ editingDeviceId ? 'Edit Device' :'Add New Device' }}</h4>
                <div class="input-group mb-3">
                    <input v-model="newDevice.name" placeholder="Device Name" required/>
                    <button class="btn btn-primary" @click="saveDevice()">{{ editingDeviceId ? 'Update' : 'Add' }}</button>
                    <button v-if="editingDeviceId" class="btn btn-secondary" @click="cancelEdit()">Cancel</button>
                </div>
            </div>
        </div>
        <!--Device List-->
        <div v-if="devices.length">
            <div v-for="device in devices" :key="device.id" class="card shadow-sm mb-4">
                <div class="card-body">
                    <h5 class="card-title">{{  device.name }}</h5>
                    <!-- <div class="device-actions">
                        <button @click="deleteDevice(device.id)">Delete</button>
                    </div>
                    <p>Status: <strong>{{  device.status ? 'ON' : 'OFF' }}</strong></p>
                    <button @click="toggleDevice(device.id)">Toggle</button> -->
                    <div class="mb-0">
                        <strong>Status:</strong> {{ device.status ? 'ON' : 'OFF' }}
                    </div>
                    <button class="btn btn-outline-secondary btn-sm me-2" @click="toggleDevice(device.id)">Toggle</button>
                    <button class="btn btn-danger btn-sm" @click="deleteDevice(device.id)">Delete</button>
                    <!-- Saved rules-->
                    <div class="mt-3">
                        <h6>Current Rules</h6>
                        <div v-for="rule in savedRules.filter(r => r.device_id === device.id)" :key="rule.id" class="mb-2">
                            <p>
                                <strong>{{ rule.days }}</strong> between <strong>{{ rule.valid_from }} - {{ rule.valid_to }}</strong>
                                <button class="btn btn-sm btn-outline-danger ms-2" @click="deleteRule(rule.id)">Delete</button>
                            </p>
                        </div>
                    </div>
                    <!-- Cheapest energy prices table-->
                    <table class="table table-bordered table-striped table-hover mt-3">
                        <thead>
                            <tr>
                                <th>Day / Time</th>
                                <th v-for="day in daysofWeek" :key="day">{{ day }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(slot, index) in cheapestEnergyPrices" :key="index">
                                <td>{{ formatSlot(slot.valid_from, slot.valid_to) }}</td>
                                <td v-for="day in daysofWeek" :key="day + slot.valid_from">
                                    <label class="d-flex align-items-center gap-1">
                                        <input type="checkbox" 
                                        :checked="automationSelections[device.id]?.scheduled.some(entry => {
                                            const startTime = new Date(slot.valid_from).toTimeString().split(' ')[0];
                                            const endTime = new Date(slot.valid_to).toTimeString().split(' ')[0];
                                            return entry.day === day && entry.slot === `${startTime}|${endTime}`;
                                        })" @change="toggleAutomationSelections(device.id, slot.valid_from + '|' + slot.valid_to, day)">
                                        {{  slot.value_inc_vat.toFixed(2) }} p/kWh
                                    </label>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    <button class="btn btn-success mt-2" @click="saveAutomation(device.id)">Save Automation</button>
                </div>
                
            </div> 
        </div>
        <div v-else class="alert alert-warning mt-4 text-center">
            <p>No devices available.</p>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import NavBar from '../components/NavBar.vue';
import { getDevices, toggleDeviceStatus, getCheapestEnergyPrices} from "../services/api";
import apiClient from '../services/api';
import { start } from "@popperjs/core";

interface Device {
  id: number;
  name: string;
  status: boolean;
}

export default defineComponent({
    name: "AutomationPage",
    components: {
        NavBar,
    },
    data() {
        return {
            devices: [] as Device[],
            cheapestEnergyPrices: [] as any[],
            daysofWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            apiKey: null as any,
            productCode: null as any,
            tariffCode: null as any,
            automationSelections: {} as Record<number, { scheduled: { day: string; slot: string }[] }>,
            user: null as any,
            savedRules: [] as any[],
            newDevice: {
                name: '',
            },
            editingDeviceId: null as number | null,
            showDeviceForm: false,
        };
    },
    methods: {
        async fetchDevices(): Promise<void>{
            this.devices = await getDevices();
            console.log("Fetched devices:", this.devices);
            for (const device of this.devices) {
                if (!this.automationSelections[device.id]) {
                    this.automationSelections[device.id] = {
                        scheduled: [],
                    };
                }
            }
        },
        async toggleDevice(deviceId: number): Promise<void>{
            await toggleDeviceStatus(deviceId);
            this.fetchDevices();

            
        },
        async fetchCheapestEnergyPrices(){
            console.log("Fetching cheapest energy prices with API key:", this.apiKey, "Product code:", this.productCode, "Tariff code:", this.tariffCode);
            this.cheapestEnergyPrices = await getCheapestEnergyPrices(this.apiKey, this.productCode, this.tariffCode);
        },
        formatSlot(start: string, end: string): string {
            const startDate = new Date(start);
            const endDate = new Date(end);
            return `${startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        },
        async toggleAutomationSelections(deviceId: number, slot: string, day: string){
            const deviceSelection = this.automationSelections[deviceId];

            const index = deviceSelection.scheduled.findIndex((entry) => entry.day === day && entry.slot === slot);
            if (index === -1){
                deviceSelection.scheduled.push({ day, slot });
            } else {
                deviceSelection.scheduled.splice(index, 1);
            }

            console.log("Updated automation selections for device", deviceId, ":", deviceSelection);
            console.log("Updated automation selections for device", deviceId, ":", this.automationSelections);
        },
        async saveAutomation(deviceId: number){
            const today = new Date().toISOString().split("T")[0];
            const scheduled = this.automationSelections[deviceId].scheduled.map(entry => {
                const [start, end] = entry.slot.split("|");
                
                let valid_from = start;
                let valid_to = end;

                if (!valid_from.includes("T")) {
                    valid_from = `${today}T${valid_from}Z`;
                }
                if (!valid_to.includes("T")) {
                    valid_to = `${today}T${valid_to}Z`;
                }

                return {
                    day: entry.day,
                    valid_from, valid_to
                }
            })
            console.log("Saving automation for device", deviceId, "with selected data:", scheduled);

            const payload = {
                device_id: deviceId,
                scheduled: scheduled,
                user: this.user
            };

            console.log("Payload to save:", payload);

            try {
                const response = await fetch("http://127.0.0.1:8000/api/save-automation/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
                        
                 if (response.ok) {
                    console.log("Automation saved successfully!");
                 } else{
                    console.error("Error saving automation:", response.statusText);
                 }
            } catch (error) {
                console.error("Error saving automation:", error);
            }
            this.fetchDevices();
            this.fetchAutomationRules();
        },
        async getCurrentUser() {
            const response = await apiClient.get("/api/current-user/");
            return response.data;
        },
        async fetchAutomationRules() {
            const response = await apiClient.get("/api/get-automation-rules/");
            console.log("Automation rules:", response.data);
            this.savedRules = response.data;
            for (const device of this.devices) {
                const deviceId = device.id;
                const rules = response.data.filter((rule: any) => rule.device_id === deviceId);
                if (rules.length > 0) {
                    this.automationSelections[deviceId].scheduled = rules.map((rule: any) => ({
                        day: rule.days,
                        slot: rule.valid_from + "|" + rule.valid_to,
                    }));
                } else {
                    this.automationSelections[deviceId].scheduled = [];
                }
            }
            console.log("Updated automation selections after fetching rules:", this.automationSelections);
            return response.data;
        },
        async deleteRule(ruleId: number) {
            try {
                const response = await apiClient.delete(`/api/delete-automation-rule/${ruleId}/`);
                if (response.status === 204) {
                    console.log("Rule deleted successfully!");
                    
                    this.fetchAutomationRules(); // Refresh the rules after deletion
                } else {
                    console.error("Error deleting rule:", response.statusText);
                }
            } catch (error) {
                console.error("Error deleting rule:", error);
            }
        },
        async saveDevice() {
            const csrfToken = this.getCookie("csrftoken") || "";  // Ensure it is a string
            console.log("CSRF Token:", csrfToken);
            if (this.editingDeviceId) {
                // Update existing device
                await apiClient.put(`/api/devices/${this.editingDeviceId}/`, this.newDevice);
            } else {
                // Create new device
                console.log("Creating new device:", this.newDevice);
                
                await fetch("http://127.0.0.1:8000/api/devices/create/",  {
                    method: "POST",
                    headers: {
                        // "X-CSRFToken": csrfToken,
                        "Content-Type": "application/json",
                    },
                    // credentials: "include", // Important for session auth
                    body: JSON.stringify({
                        name : this.newDevice,
                        user : this.user
                    }),
                    
                });

            }
            this.fetchDevices()
            this.resetDeviceForm();
        },
        startEditDevice(device: Device) {
            this.editingDeviceId = device.id;
            this.newDevice.name = device.name;
            this.showDeviceForm = true;
        },

        cancelEdit() {
            this.resetDeviceForm();
        },

        resetDeviceForm() {
            this.editingDeviceId = null;
            this.newDevice.name = '';
            this.showDeviceForm = false;
        },
        async deleteDevice(deviceId: number) {
            try {
                if (confirm("Are you sure you want to delete this device?")) {
                    await fetch (`http://127.0.0.1:8000/api/devices/${deviceId}/delete/`, {
                        method: "DELETE",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            user : this.user
                        }),
                    });
                    this.fetchDevices();
                }
            } catch (error) {
                console.error("Error deleting device:", error);
            }
        },

        getCookie(name: string): string | null {
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
        },

    },
    mounted() {
        this.getCurrentUser().then((user) => {
            this.user = user;
            this.apiKey = user.octopus_api_key;
            this.productCode = user.octopus_product_code;
            this.tariffCode = user.octopus_tariff_code;
            console.log("User data:", user);
            console.log("API Key:", this.apiKey);
            
            this.fetchDevices();
            this.fetchCheapestEnergyPrices();
            this.fetchAutomationRules();
            fetch("http://127.0.0.1:8000/csrf-token/", {
                credentials: "include"
            });
        }).catch((error) => {
            console.error("Error fetching user data:", error);
        });
    }
});
</script>

<style scoped>
/* .device-card {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 12px;
} */
/* .device-slots, .device-days {
  margin-top: 1rem;
}
.price-slot, .day-checkbox {
  margin: 0.5rem 0;
} */
/* button {
  margin-top: 1rem;
} */
.card-title {
  font-size: 1.25rem;
}
.table td,
.table th {
  vertical-align: middle;
  text-align: center;
}
</style>