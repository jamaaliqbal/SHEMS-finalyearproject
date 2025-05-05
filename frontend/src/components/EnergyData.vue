<template>
    <div class="container py-4">
        <h1 class="text-center text-primary mb-4">Smart Home Energy Dashboard</h1>
        <div class="alert alert-info text-center shadow-sm">
            <p class="mb-0">
                This dashboard provides a live overview of your electricity consumption and solar energy generation.
                Use it to monitor trends and make informed decisions about energy usage in your smart home.
            </p>
        </div>
        <div class="row">
            <!-- Energy Data Card -->
            <div class="col-md-6">
                <div class="card shadow-sm mb-4">
                    <div class="card-body">
                        <h4 class="card-title text-dark">Electricity Consumption</h4>
                        <!-- Tabs -->
                        <ul class="nav nav-tabs" id="consumptionTabs">
                            <li class="nav-item">
                                <a class="nav-link" :class="{ active: consumptionTab === 'table' }" @click="consumptionTab = 'table'">Table</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" :class="{ active: consumptionTab === 'chart' }" @click="consumptionTab = 'chart'">Chart</a>
                            </li>
                        </ul>
                        <!-- Group By Dropdown --> 
                        <label for="group-by">Group Consumption Data By:</label>
                        <select id="group-by" v-model="selectedGroupBy" class="form-control" @change="fetchConsumptionData">
                            <option v-for="option in groupOptions" :key="option.value" :value="option.value">
                                {{ option.text }}
                            </option>
                        </select>
                        <!-- Tab contents -->
                        <div v-if="consumptionTab === 'table'">
                            <!-- Bootstrap Table -->
                            <table class="table table-bordered table-striped mt-3">
                                <thead>
                                    <tr>
                                        <th>Start Time</th>
                                        <th>End Time</th>
                                        <th>Consumption (kWh)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(data, index) in paginatedData" :key="index">
                                        <td>{{ new Date(data.interval_start).toLocaleString('en-GB', { dateStyle: 'short', timeStyle: 'short' }) }}</td>
                                        <td>{{ new Date(data.interval_end).toLocaleString('en-GB', { dateStyle: 'short', timeStyle: 'short' }) }}</td>
                                        <td>{{ data.consumption }}</td>
                                    </tr>
                                </tbody>
                            </table>

                            <!-- Pagination -->
                            <div class="pagination-controls mt-3">
                                <button @click="prevPage('energyConsumption')" :disabled="currentPage === 1" class="btn btn-secondary">Previous</button>
                                <span class="mx-2">Page {{ currentPage }}</span>
                                <button @click="nextPage('energyConsumption')" :disabled="currentPage * pageSize >= consumptionData.length" class="btn btn-secondary">Next</button>
                            </div>
                        </div>
                        
                        <div v-if="consumptionTab === 'chart'" class="mt-3">
                            <canvas ref="energyChartCanvas"></canvas>
                        </div>

                        <!-- Prediction dropdown-->
                        <label for="prediction-period">Predict Energy Usage For:</label>
                        <select id="prediction-period" v-model="selectedPredictedPeriod" class="form-control">
                            <option value="hour">Next Hour</option>
                            <option value="day">Next Day</option>
                            <option value="week">Next 7 Days</option>
                        </select>

                        <button @click="fetchPrediction" class="btn btn-primary mt-3">Predict energy usage</button>
                        <!-- Prediction table for energy usgage -->
                        <div v-if="consumptionTab === 'table'">
                            <table v-if="predictedEnergy.length" class="table table-bordered table-striped mt-3">
                                <thead>
                                    <tr>
                                        <th>Hour</th>
                                        <th>Predicted Energy </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(data, index) in paginatedEnergyPredictions" :key="index">
                                        <td>Hour {{ (energyPredictionPage - 1) * pageSize + index + 1 }}</td>
                                        <td>{{ data }}</td>
                                    </tr>
                                </tbody>
                            </table>
                            <!-- Pagination for energy predictions -->
                            <div v-if="predictedEnergy.length" class="pagination-controls mt-3">
                                <button @click="prevPage('energyPredictions')" :disabled="energyPredictionPage === 1" class="btn btn-secondary">Previous</button>
                                <span class="mx-2">Page {{ energyPredictionPage }}</span>
                                <button @click="nextPage('energyPredictions')" :disabled="energyPredictionPage * pageSize >= predictedEnergy.length" class="btn btn-secondary">Next</button>
                            </div>
                        </div>
                        <!-- Chart for predicted energy usage -->
                        <div v-if="consumptionTab === 'chart'">
                            <canvas ref="chartCanvas"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Solar Energy Data -->
            <div v-if="solarEnergyData" class="col-md-6">
                <div class="card shadown-sm mb-4">
                    <div class="card-body">
                        <h4 class="card-title text-dark">Solar Energy Data</h4>
                        <p><strong>Current Solar Power:</strong> {{ solarEnergyData.acpower }}W</p>
                        <p><strong>Daily Yield:</strong> {{ solarEnergyData.yieldtoday }}kWh</p>
                        <p><strong>Battery Power Percentage:</strong> {{ solarEnergyData.soc }}%</p>
                        <p><strong>Total Yield</strong> {{ solarEnergyData.yieldtotal }}kWh</p>
                        <button @click="loadSolarData" class="btn btn-primary mt-3 me-2">Refresh data</button>
                        <button @click="fetchSolarPredictions" class="btn btn-primary mt-3">Predict Solar Power</button>
                        <!-- Tabs -->
                        <ul v-if="solarPredictions.length" class="nav nav-tabs" id="solarTabs">
                            <li class="nav-item">
                                <a class="nav-link" :class="{ active: solarTab === 'table' }" @click="solarTab = 'table'">Table</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" :class="{ active: solarTab === 'chart' }" @click="solarTab = 'chart'">Chart</a>
                            </li>
                        </ul>
                        <!-- Tab contents -->
                        <div v-if="solarTab === 'table'">
                            <!-- Prediction table for solar power -->
                            <table v-if="solarPredictions.length" class="table table-bordered table-striped mt-3">
                                <thead>
                                    <tr>
                                        <th>Hour</th>
                                        <th>Predicted Power (W)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="(data, index) in paginatedSolarPredictions" :key="index">
                                        <td>Hour {{ (solarPredictionPage - 1) * pageSize + index + 1 }}</td>
                                        <td>{{ data.toFixed(2) }} W</td>
                                    </tr>
                                </tbody>
                            </table>
                            <!-- Pagination for solar predictions -->
                            <div v-if="solarPredictions.length" class="pagination-controls mt-3">
                                <button @click="prevPage('solar')" :disabled="solarPredictionPage === 1" class="btn btn-secondary">Previous</button>
                                <span class="mx-2">Page {{ solarPredictionPage }}</span>
                                <button @click="nextPage('solar')" :disabled="solarPredictionPage * pageSize >= solarPredictions.length" class="btn btn-secondary">Next</button>
                            </div>
                        </div>
                        <!-- Chart for solar predictions-->
                        <div v-if="solarTab === 'chart'" class="mt-3">
                            <canvas ref="solarChartCanvas"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-12">
                <div class="card shadow-sm">
                    <div class="card-body text-center">
                        <WeatherView></WeatherView>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
import apiClient from '@/services/api';
import axios from 'axios'
import { onMounted, ref, computed, watch, nextTick} from 'vue'
import { Chart, registerables} from 'chart.js'
import WeatherView from './WeatherView.vue';

Chart.register(...registerables);

export default {
    components: {
        WeatherView
    },
    setup() {
        const energyData = ref([])
        const octopusData = ref([])
        const solarData = ref([])
        const solarPredictions = ref([])
        const weatherData = ref([])
        const chartCanvas = ref(null);
        const solarChartCanvas = ref(null);
        const energyChartCanvas = ref(null);
        const solarEnergyData = ref(null)
        let energyChartInstance = null
        let chartInstance = null
        let solarChartInstance = null
        const consumptionData = ref([])
        const currentPage = ref(1)
        const solarPredictionPage = ref(1)
        const energyPredictionPage = ref(1)
        const pageSize = 10
        const selectedGroupBy = ref("hour")
        const last7DaysEnergyData = ref([])
        const predictedEnergy = ref([])
        const selectedPredictedPeriod = ref("hour")
        const user = ref([])
        const consumptionTab = ref("table")
        const solarTab = ref("table")
        const groupOptions = ref([
            { value: "hour", text: "Hourly" },
            { value: "day", text: "Daily" },
            { value: "week", text: "Weekly" },
            { value: "month", text: "Monthly" }
        ])

        const fetchConsumptionData = () => {
            axios.get("http://127.0.0.1:8000/api/octopus-data/", {
                params: {
                    group_by: selectedGroupBy.value,
                    page_size: 200,
                    user: user.value,
                }
            }).then(response => {
                console.log("Consumption data:", response.data.results)
                consumptionData.value = response.data.results
                currentPage.value = 1

                last7DaysEnergyData.value = response.data.results.slice(-168)
                console.log("Last 7 days energy data: " + last7DaysEnergyData.value)
                updateEnergyConsumptionChart();
            }).catch(error => {
                console.error('Error fetching data:', error);
            })
        }

        // Paginated data computation
        const paginatedData = computed(() => {
            const start = (currentPage.value - 1) * pageSize;
            return consumptionData.value.slice(start, start + pageSize);
        });

        const paginatedSolarPredictions = computed(() => {
            const start = (solarPredictionPage.value - 1) * pageSize;
            return solarPredictions.value.slice(start, start + pageSize);
        });

        const paginatedEnergyPredictions = computed(() => {
            console.log("Energy predictions page" + energyPredictionPage.value)
            const start = (energyPredictionPage.value - 1) * pageSize;
            return predictedEnergy.value.slice(start, start + pageSize);
        });

        const nextPage = (type) => {
            if (type === 'energyConsumption') {
                if (currentPage.value * pageSize < consumptionData.value.length) {
                    currentPage.value++;
                }
            } else if (type === 'solar') {
                if (solarPredictionPage.value * pageSize < solarPredictions.value.length) {
                    solarPredictionPage.value++;
                }
            } else if (type === 'energyPredictions') {
                if (energyPredictionPage.value * pageSize < predictedEnergy.value.length) {
                    energyPredictionPage.value++;
                }
            }
            // if (currentPage.value * pageSize < consumptionData.value.length) {
            //     currentPage.value++;
            // }
        };

        const prevPage = (type) => {
            if (type === 'energyConsumption') {
                if (currentPage.value > 1) {
                    currentPage.value--;
                }
            } else if (type === 'solar') {
                if (solarPredictionPage.value > 1) {
                    solarPredictionPage.value--;
                }
            } else if (type === 'energyPredictions') {
                if (energyPredictionPage.value > 1) {
                    energyPredictionPage.value--;
                }
            }
            // if (currentPage.value > 1) {
            //     currentPage.value--;
            // }
        };

        const fetchEnergyData = () => {
            apiClient.get('energy-data/')
               .then(response => {
                    console.log("Energy Data:", response.data);
                    energyData.value = response.data;
                })
               .catch(error => {
                    console.error('Error fetching data:', error);
                });
        };

        const fetchSolarData = () => {
            apiClient.get('solar-data/')
               .then(response => {
                    console.log("Get Solar Data:", response.data);
                    solarData.value = response.data;
                })
               .catch(error => {
                    console.error('Error fetching data:', error);
                });
        };

        const loadSolarData = async () => {
            try {
                console.log("Current user solar data:", user);
                const response = await axios.get('http://127.0.0.1:8000/api/solax-data/', {
                    params: {
                        wifiSn: 'SV8RYX9GZU',
                        user: user.value,
                    }
                })
                console.log("Load Solar Data:", response.data);
                solarEnergyData.value = response.data.result;
                // updateChart();
            } catch(error) {
                console.error('Error fetching solar data:', error);
            };
        };

        // NOT CURRENTLY NEEDED AS FETCHCONSUMPTION METHOD DOES SAME THING 
        const loadOctopusData = () => {
            console.log("Current user octopus data:", user);
            axios.get("http://127.0.0.1:8000/api/octopus-data/")
            .then(response => {
                 console.log("Octopus Data:", response.data);
                 octopusData.value = response.data.results;
                 updateChart();
             }).catch((error) => {
                console.error('Error fetching octopus data:', error);
             });
        }

        const fetchWeatherData = () => {
            // apiClient.get('weather-data/')
            axios.get("http://127.0.0.1:8000/api/weather-data/")
               .then(response => {
                    console.log("Get Weather Data:", response.data);
                    weatherData.value = response.data;
                })
               .catch(error => {
                    console.error('Error fetching data:', error);
                });
        };

        const fetchPrediction = async () => {
            try {
                const consumptionHistoryEnergyData = ref([])
                consumptionHistoryEnergyData.value = last7DaysEnergyData.value.map(entry => entry.consumption)
                const hourHistoryEnergyData = ref([])
                hourHistoryEnergyData.value = last7DaysEnergyData.value.map(entry => new Date(entry.interval_start).getHours() / 23);
                const dayHistoryEnergyData = ref([])
                dayHistoryEnergyData.value = last7DaysEnergyData.value.map(entry => new Date(entry.interval_start).getDay() / 6);
                const monthHistoryEnergyData = ref([])
                monthHistoryEnergyData.value = last7DaysEnergyData.value.map(entry => (new Date(entry.interval_start).getMonth() + 1) / 12);
                console.log("Fetching prediction for period:", selectedPredictedPeriod.value);
                const response = await axios.post("http://127.0.0.1:5001/predict-energy", {
                    consumption_history: consumptionHistoryEnergyData.value,
                    hour: hourHistoryEnergyData.value,
                    day: dayHistoryEnergyData.value,
                    month: monthHistoryEnergyData.value,
                    prediction_period: selectedPredictedPeriod.value,
                });
                console.log("Predicted energy usage:", response.data.predicted_energy_usage);
                // predictedEnergy.value = response.data.predicted_energy_usage.map(value => value.toFixed(2) + " kWh");
                predictedEnergy.value = response.data.predicted_energy_usage.map(value => Math.max(0, value).toFixed(2) + " kWh");
                let predictions = predictedEnergy.value
                // Limit based on period
                if (selectedPredictedPeriod.value === 'hour') {
                    predictions = predictions.slice(0, 1);
                } else if (selectedPredictedPeriod.value === 'day') {
                    predictions = predictions.slice(0, 24);
                } // else keep full (week = 168)
                predictedEnergy.value = predictions
                energyPredictionPage.value = 1
                console.log("Predicted energy usage page value:", energyPredictionPage.value);
                updateEnergyPredictionsChart();
            } catch (error) {
                console.error('Error fetching prediction:', error);
                predictedEnergy.value = "Error fetching prediction";
            }
            
        }

        const fetchSolarPredictions = async () => { 
            const user = await getCurrentUser();
            console.log("Current user:", user);
            try {
                if (solarData.value.length < 48) { 
                    console.error('Not enough solar data to predict');
                    return;
                }

                const formattedSolarData = solarData.value.slice(-48).map(entry => ({
                    ac_power: entry.ac_power,
                    yield_today: entry.yield_today
                }))

                const formattedWeatherData = weatherData.value.slice(-48).map(entry => ({
                    temperature: entry.temperature,
                    humidity: entry.humidity,
                    wind_speed: entry.wind_speed,
                    clouds: entry.clouds
                }))

                const response = await axios.post("http://127.0.0.1:5001/predict-solar", {
                    solar_history: formattedSolarData, 
                    weather_history: formattedWeatherData
                })

                console.log("Predicted solar energy usage:", response.data.solar_prediction);
                // solarPredictions.value = response.data.solar_prediction
                solarPredictions.value = response.data.solar_prediction.map((val) => Math.max(0, val));
                solarPredictionPage.value = 1
                updateSolarChart();
            } catch (error) {
                console.error('Error fetching prediction:', error);
                // solarPredictions.value = "Error fetching prediction";
            }
        }

        const updateEnergyPredictionsChart = () => {
            console.log("Energy chart" + chartCanvas.value)
            if (!chartCanvas.value || predictedEnergy.value.length === 0) return;
            const ctx = chartCanvas.value.getContext("2d");
            if (chartInstance) chartInstance.destroy();
            chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                labels: predictedEnergy.value.map((_, i) => `Hour ${i + 1}`),
                datasets: [{
                    label: "Predicted Energy Usage",
                    data: predictedEnergy.value.map(val => parseFloat(val)),
                    borderColor: "#007bff",
                    fill: false
                }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } }
            });
        }

        const updateEnergyConsumptionChart = () => {
            console.log("Energy consumption chart" + energyChartCanvas.value)
            console.log("Energy consumption data" + consumptionData.value)
            if (!energyChartCanvas.value || consumptionData.value.length === 0) return;
            const ctx = energyChartCanvas.value.getContext("2d");
            if (energyChartInstance) energyChartInstance.destroy();
            energyChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: consumptionData.value.map((_, i) => `Hour ${i + 1}`),
                    datasets: [{
                        label: "Energy Consumption",
                        data: consumptionData.value.map(val => parseFloat(val.consumption)),
                        borderColor: "#007bff",
                        fill: false
                    }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } }
            });
        }

        const updateSolarChart = () => {
            console.log("Solar Char" + solarChartCanvas)
            if (!solarChartCanvas.value || solarPredictions.value.length === 0) return;
            const ctx = solarChartCanvas.value.getContext("2d");
            if (solarChartInstance) solarChartInstance.destroy();
            solarChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: solarPredictions.value.map((_, i) => `Hour ${i + 1}`),
                    datasets: [{
                        label: "Predicted Solar Power",
                        data: solarPredictions.value.map(val => parseFloat(val)),
                        borderColor: "#28a745",
                        fill: false
                    }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } }
            });
        }

        const getCurrentUser = async () => {
            const response = await apiClient.get("/api/current-user/");
            return response.data;
        }

        onMounted(async () => {
            // fetchEnergyData();
            // fetchSolarData();
            try {
                user.value = await getCurrentUser();
                // user.value = getUser.data;
                console.log("User data:", user.value);
                // console.log("Current user:", getUser);
                await loadSolarData();
                await fetchSolarData();
                // loadOctopusData();
                await fetchConsumptionData(); 
                fetchWeatherData();
            } catch (error) {
                console.error('Error fetching data:', error);
            }
            
        });

        watch(consumptionTab, async () => {
            if (consumptionTab.value === 'chart'){
                await nextTick();
                updateEnergyConsumptionChart();
                updateEnergyPredictionsChart();
            } 
        });

        watch(solarTab, async () => {
            if (solarTab.value === 'chart') {
                await nextTick();
                updateSolarChart()
            };
        });

        return {
            energyData,
            chartCanvas,
            solarChartCanvas,
            energyChartCanvas,
            solarEnergyData,
            loadSolarData,
            solarData,
            octopusData,
            consumptionData,
            currentPage,
            pageSize,
            energyPredictionPage,
            solarPredictionPage,
            selectedGroupBy,
            groupOptions,
            paginatedData,
            paginatedSolarPredictions,
            paginatedEnergyPredictions,
            // updateChart,
            nextPage,
            prevPage,
            fetchConsumptionData,
            WeatherView,
            last7DaysEnergyData,
            predictedEnergy,
            selectedPredictedPeriod,
            fetchPrediction,
            solarPredictions,
            fetchSolarPredictions,
            consumptionTab,
            solarTab,
        };
    }
};
</script>
