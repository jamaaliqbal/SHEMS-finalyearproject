from django.core.management.base import BaseCommand
from energy.data_collector import WeatherDataCollector
import time
import logging

class Command(BaseCommand):
    help = 'Fetch and save weather data from a third-party API'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collector = WeatherDataCollector()
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting weather data collection'))
        
        try:
            self.stdout.write(self.style.SUCCESS("Fetching current weather data..."))
            self.collector.fetch_weather_data(days=365)
            self.stdout.write(self.style.SUCCESS("Successfully collected past weather data."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
            self.logger.error(f"An error occurred: {str(e)}")

    # time.sleep(3600)  # Run every hour