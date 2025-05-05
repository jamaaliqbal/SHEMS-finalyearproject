from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime
from energy.data_collector import DataCollectorService
import requests
import time
import logging

class Command(BaseCommand):
    help = 'Fetch and save energy consumption data from a third-party API'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = settings.SOLAX_API_TOKEN
        self.api_url = settings.SOLAX_API_URL
        self.collector = DataCollectorService()
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        wifi_sns = settings.SOLAX_WIFI_SNS

        self.stdout.write(
            self.style.SUCCESS('Starting Solax data collection')
        )

        while True:
            for wifi_sn in wifi_sns:
                try:
                    data = self.collector.collect_data(wifi_sn)
                    if data:
                        self.stdout.write(
                            self.style.SUCCESS(f'Successfully collected data for {wifi_sn}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to collect data for {wifi_sn}. Response: {data}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'An error occurred while collecting data for {wifi_sn}: {str(e)}')
                    )
                    self.logger.error(f'An error occurred while collecting data for {wifi_sn}: {str(e)}')
            time.sleep(3600)  # Sleep for 60 seconds before fetching data again