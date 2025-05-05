import requests
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# API URLs
# SOLAR_DATA_API = "http://127.0.0.1:8000/api/solar-data/"
WEATHER_DATA_API = "http://127.0.0.1:8000/api/weather-data/"
SOLAR_UPLOAD_API = "http://127.0.0.1:8000/api/upload-synthetic-data/"  # Ensure your Django backend has this endpoint

# Solar Panel Parameters
MAX_SOLAR_POWER = 5000  # Maximum solar panel output in Watts (5kW system)
EFFICIENCY_LOSS_CLOUDS = 0.75  # Loss factor for full cloud cover
SUNRISE_HOUR = 6
SUNSET_HOUR = 20
LATITUDE = 51.32  # Approximate latitude for Coulsdon, UK

def fetch_weather_data():
    """Fetch weather data from the Django API"""
    response = requests.get(WEATHER_DATA_API)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

def solar_power_model(time, temp, clouds):
    """
    Estimate solar power generation based on:
    - Time of day (daylight hours)
    - Temperature (higher temps slightly reduce efficiency)
    - Cloud cover (reduces solar power)
    """
    hour = time.hour

    # Check if it's night time
    if hour < SUNRISE_HOUR or hour > SUNSET_HOUR:
        return 0  # No solar generation at night

    # Base solar generation as a function of time (parabolic peak at noon)
    peak_hour = (SUNSET_HOUR + SUNRISE_HOUR) / 2
    hour_factor = max(0, np.cos((hour - peak_hour) * np.pi / (SUNSET_HOUR - SUNRISE_HOUR)))

    # Adjust for cloud cover (100% clouds reduce output)
    cloud_factor = 1 - (clouds / 100) * EFFICIENCY_LOSS_CLOUDS

    # Adjust for temperature (small loss for high temperatures)
    temp_factor = 1 - (max(temp - 25, 0) * 0.005)  # Small loss above 25°C

    # Compute estimated power output
    estimated_power = MAX_SOLAR_POWER * hour_factor * cloud_factor * temp_factor
    return round(estimated_power, 2)

def generate_synthetic_solar_data():
    """Generate synthetic solar data based on weather conditions"""
    weather_data = fetch_weather_data()
    if weather_data.empty:
        print("No weather data available")
        return
    
    synthetic_solar_data = []
    
    for index, row in weather_data.iterrows():
        timestamp = datetime.strptime(row["date_time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
        temperature = row["temperature"]
        cloud_cover = row["clouds"]
        
        # Generate estimated solar power
        solar_power = solar_power_model(timestamp, temperature, cloud_cover)
        
        synthetic_solar_data.append({
            # "inverter_sn": "SYNTHETIC_001",
            # "wifi_sn": "SYNTHETIC_001",
            "ac_power": solar_power,  # Synthetic AC power
            "yield_today": round(solar_power * 0.8, 2),
            # "yield_total": round(solar_power * 10, 2),
            # "feedin_power": round(solar_power * 0.1, 2),
            # "consume_energy": round(solar_power * 0.5, 2),
            # "battery_soc": np.random.randint(20, 100),  # Random battery state of charge
            "upload_time": timestamp.isoformat(),
            # "is_synthetic": True
        })

    return synthetic_solar_data

def upload_synthetic_data(solar_data):
    """Upload the generated solar data to the Django API"""
    payload = {"data": solar_data}
    response = requests.post(SOLAR_UPLOAD_API, json=payload)
    if response.status_code == 201:
        print("Synthetic solar data uploaded successfully!")
    else:
        print(f"Failed to upload data: {response.status_code} - {response.text}")

if __name__ == "__main__":
    synthetic_data = generate_synthetic_solar_data()
    if synthetic_data:
        upload_synthetic_data(synthetic_data)
