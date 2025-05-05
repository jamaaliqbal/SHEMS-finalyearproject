import requests
from django.conf import settings

class WeatherService:
    def __init__(self, city="London"):
        self.city = city
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_URL
        self.forecast_url = settings.WEATHER_FORECAST_API_URL

    def get_weather_data(self):
        params = {
            "q": self.city,
            "appid": self.api_key,
            "units": "metric"  
        }
        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": "Failed to get weather data"}
        
    def get_forecast_data(self):
        params = {
            "q": self.city,
            "appid": self.api_key,
            "units": "metric",
            "cnt": 40
        }
        response = requests.get(self.forecast_url, params=params)

        if response.status_code == 200:
            data = response.json()

            #Group data by day 
            daily_forecast = {}
            for entry in data.get("list", []):
                date = entry["dt_txt"].split(" ")[0]
                if date not in daily_forecast:
                    daily_forecast[date] = entry
            return list(daily_forecast.values())
        else:
            return {"error": "Failed to get forecast data"}
        
    def get_combined_data(self):
        weather_data = self.get_weather_data()
        forecast_data = self.get_forecast_data()

        return {
            "weather": weather_data,
            "forecast": forecast_data
        }