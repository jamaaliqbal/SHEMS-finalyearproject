from django.core.management.base import BaseCommand
from django.conf import settings
from energy.data_collector import ElectricityDataCollector
import time
import logging

class Command(BaseCommand):
    help = 'Fetch and save electricity consumption data from Octopus API'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collector = ElectricityDataCollector()
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting electricity data collection')
        )

        # while True:
        try:
            # self.stdout.write(self.style.SUCCESS("Fetching hourly electricity data..."))
            # self.collector.fetch_hourly_data()
            # self.stdout.write(self.style.SUCCESS("Successfully stored hourly electricity data."))

            self.stdout.write(self.style.SUCCESS("Calculating yearly consumption..."))
            self.collector.calculate_yearly_consumption()
            self.stdout.write(self.style.SUCCESS("Successfully stored yearly electricity data."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
            self.logger.error(f"An error occurred: {str(e)}")

        # time.sleep(3600)  # Run every hour
        pass
