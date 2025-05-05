from datetime import datetime, timedelta
import json
import requests
from django.conf import settings
from django.test import RequestFactory
from django.db.models import Sum
from dateutil import parser

from django.http import JsonResponse
from .views import ProxySolarDataView, ProxyOctopusDataView
from .models import SolarInverterData, HourlyEnergyConsumption, YearlyEnergyConsumption, WeatherData

class DataCollectorService:
    def __init__(self):
        self.api_service = ProxySolarDataView()

    def collect_data(self, wifi_sn):
        """Collect data from API and store in database"""
        print(f"DEBUG: Fetching data for wifi_sn: {wifi_sn}")
        data = self.api_service.get(wifi_sn)
        print(f"DEBUG: Received data: {data}")
        print(f"DEBUG: Checking if data is valid: {data.get}")

        if isinstance(data, JsonResponse):
            data = json.loads(data.content)

        if data is None:
            print(f"DEBUG: Data is None for wifi_sn: {wifi_sn}")
            return None
        
        if not isinstance(data, dict) or 'success' not in data:
            print(f"DEBUG: 'success' key not found in API response. Full response: {data}")
            return None
        
        print(f"DEBUG: data.get('success') value: {data.get('success')}")

        if data and data.get('success'):
            result = data['result']
            print(f"DEBUG: Result: {result}")

            inverter_data = SolarInverterData(
                inverter_sn=result.get('inverterSN'),
                wifi_sn=result.get('sn'),
                ac_power=result.get('acpower'),
                yield_today=result.get('yieldtoday'),
                yield_total=result.get('yieldtotal'),
                feedin_power=result.get('feedinpower'),
                feedin_energy=result.get('feedinenergy'),
                consume_energy=result.get('consumeenergy'),
                battery_power=result.get('batPower'),
                battery_soc=result.get('soc'),
                pv1_power=result.get('powerdc1'),
                pv2_power=result.get('powerdc2'),
                inverter_status=result.get('inverterStatus'),
                upload_time=datetime.strptime(
                    result.get('uploadTime'), 
                    '%Y-%m-%d %H:%M:%S'
                )
            )

            inverter_data.save()
            print(f"DEBUG: Data saved to database: {inverter_data}")
            return inverter_data
        print(f"DEBUG: Data save failed for wifi_sn: {wifi_sn}")
        return None

class ElectricityDataCollector:
    def __init__(self):
        self.api_url = settings.OCTOPUS_API_URL
        self.api_key = settings.OCTOPUS_API_KEY
        self.mpan = settings.OCTOPUS_MPAN
        self.serial = settings.OCTOPUS_SERIAL
        # self.factory = RequestFactory()

    def fetch_hourly_data(self):
        url = f"{self.api_url}/{self.mpan}/meters/{self.serial}/consumption/"
        params = {
            "order_by": "-period",
            "page_size": 10000,
            "group_by": "hour"
        }
        print(f"DEBUG: Fetching data for url: {url}")

        all_data = []
        page = 1

        while True:
            response = requests.get(url, params={**params, "page": page}, auth=(self.api_key, ""))
            data = response.json()
            print(f"DEBUG:data : {data}")
            if "results" in data:
                all_data.extend(data["results"])
                print(f"DEBUG: Fetched {len(data['results'])} entries")
            else:
                break

            if not data.get("next"):
                break
            page += 1
        if response.status_code == 200:
            print("Hourly electricity data fetched successfully")
            self.store_hourly_data(all_data)
        else:
            print(f"Failed to fetch hourly data. Status code: {response.status_code}")
            

    def store_hourly_data(self, data):
        print(f"DEBUG: Storing {len(data)} hourly entries")
        for entry in data:
            interval_start = parser.parse(entry["interval_start"])
            interval_end = parser.parse(entry["interval_end"])
            consumption = entry["consumption"]

            HourlyEnergyConsumption.objects.update_or_create(
                interval_start=interval_start,
                interval_end=interval_end,
                defaults={"consumption": consumption},
                mpan = self.mpan,
                meter_serial = self.serial
            )
        print("Hourly electricity data saved")

    def calculate_yearly_consumption(self):
        print("DEBUG: Calculating yearly consumption")
        yearly_data = (
            HourlyEnergyConsumption.objects
            .values("interval_start__year").annotate(total_consumption=Sum("consumption"))
        )
        print(f"Fetching yearly data for: {yearly_data}" )
        for entry in yearly_data:
            year = entry["interval_start__year"]
            total_consumption = entry["total_consumption"]

            YearlyEnergyConsumption.objects.update_or_create(
                year=year,
                defaults={"total_consumption": total_consumption},
                mpan = self.mpan,
                meter_serial = self.serial
            )
        print("Yearly electricity consumption saved")

class WeatherDataCollector:
    def __init__(self):
        self.api_url = "http://history.openweathermap.org/data/2.5/history/city"
        self.api_key = settings.WEATHER_API_KEY
        self.lat = settings.WEATHER_LATITUDE
        self.lon = settings.WEATHER_LONGITUDE

    def fetch_weather_data(self, days=365):
        """Fetch and store weather data for the past given days"""
        for day in range(days):
            end_timestamp = int((datetime.utcnow() - timedelta(days=day)).timestamp())
            start_timestamp = end_timestamp - 86400  # One day in seconds

            url = f"{self.api_url}?lat={self.lat}&lon={self.lon}&type=hour&start={start_timestamp}&end={end_timestamp}&appid={self.api_key}&units=metric"
            print(f"DEBUG: fetching weather data from {datetime.utcfromtimestamp(start_timestamp)} to {datetime.utcfromtimestamp(end_timestamp)}")

            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch weather data for {datetime.utcfromtimestamp(start_timestamp)}")
                return None

            data = response.json()
            print(f"DEBUG: Received weather data: {data}")
            if "list" not in data or not data:
                print(f"No weather data found: {data}")
                return None

            self.store_weather_data(data["list"])
            print(f"Weather data saved for {datetime.utcfromtimestamp(start_timestamp)}")

    def store_weather_data(self, data_list):
        """Store weather data in the database"""
        print(f"DEBUG: Storing {len(data_list)} weather entries")
        for entry in data_list:
            # dt = parser.parse(entry["dt_txt"])
            # temperature = entry["main"]["temp"] - 273.15  # Convert Kelvin to Celsius
            # weather_description = entry["weather"][0]["description"]
            timestamp = datetime.utcfromtimestamp(entry["dt"])
            temp = entry["main"]["temp"]
            humidity = entry["main"]["humidity"]
            wind_speed = entry["wind"]["speed"]
            weather_desc = entry["weather"][0]["description"]
            clouds = entry.get("clouds", {}).get("all", 0)

            WeatherData.objects.update_or_create(
                date_time=timestamp,
                defaults={
                    "temperature": temp,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "weather_description": weather_desc,
                    "clouds": clouds
                }
            )
        print("Weather data saved")



