<template>
    <div class="weather-container">
        <h2>Weather in {{ city }}</h2>
        <div v-if="currentWeather" class="current-weather">
            <h3>Current Weather</h3>
            <div class="weather-card">
                <!-- <img :src="getWeatherIcon(currentWeather.weather[0].main)" alt="weather icon" class="weather-icon" /> -->
                <p><strong>Temperature:</strong> {{ currentWeather.main.temp }}°C</p>
                <p><strong>Condition:</strong> {{ currentWeather.weather[0].description }}</p>
            </div>
            
        </div>
        <div v-if="forecast.length">
            <h3>5-Day Forecast</h3>
            <div class="forecast-table">
                <div v-for="forecast in forecast" :key="forecast.dt" class="forecast-card">
                    <p><strong>Date: {{ new Date(forecast.dt * 1000).toLocaleDateString() }}</strong></p>
                    <img :src="getWeatherIcon(forecast.weather[0].main)" alt="weather icon" class="weather-icon" />
                    <p>Temperature: {{ forecast.main.temp }}°C</p>
                    <p>Condition: {{ forecast.weather[0].description }}</p>
                </div>
            </div>
        </div>
        <div class="input-group">
            <input v-model="city" placeholder="Enter city" class="city-input">
            <button @click="getWeather" class="btn btn-primary">Get Weather</button>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            city: "London",
            currentWeather: null,
            forecast: [],
            iconMap: []
        };
    },
    methods: {
        async getWeather() {
            try {
                const response = await axios.get(`http://127.0.0.1:8000/api/weather/?city=${this.city}`);
                console.log(response);
                console.log("Reponse data:", response.data)
                this.currentWeather = response.data.weather
                console.log("Current weather: " + this.currentWeather)
                this.forecast = response.data.forecast
                console.log("Forecast: " + this.forecast)
   
            } catch (error) {
                console.error("Error fetching weather data:", error);
            }
                
        },
        getWeatherIcon(icon) {
            // Map weather conditions to icons
            const iconMap = {
                "Clear": require("@/assets/icons/Clear.png"),
                "Clouds": require("@/assets/icons/Clouds.png"),
                "Rain": require("@/assets/icons/Rain.png"),
                "Snow": require("@/assets/icons/Snow.png"),
                "Mist": require("@/assets/icons/Mist.png"),
                "Fog": require("@/assets/icons/Fog.png"),
                "Thunderstorm": require("@/assets/icons/Thunderstorm.png"),
            }
            // return `http://openweathermap.org/img/wn/${icon}@2x.png`;
            return iconMap[icon] || require("@/assets/icons/Clear.png");
        }
    },
    mounted() {
        this.getWeather();
    }
}
</script>

<style scoped>
.weather-container {
  /* background-color: #f4f4f4; */
  padding: 20px;
  /* border-radius: 10px; */
  text-align: center;
}

.weather-card {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 20px;
}

.weather-icon {
    width: 50px;
    height: 50px;
}

.forecast-table {
    display: flex;
    justify-content: center;
    gap: 10px;
}

.forecast-card {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    width: 100px;
}

.input-group {
    margin-top: 20px;
}

.city-input {
    padding: 5px;
    margin-right: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
}
</style>