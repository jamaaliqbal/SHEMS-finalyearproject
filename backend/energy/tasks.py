from celery import shared_task
from energy.data_collector import DataCollectorService
from django.conf import settings

@shared_task
def collect_solar_data():
    """Collect solar data from third-party API and store in database"""
    collector = DataCollectorService()
    wifi_sns = settings.SOLAX_WIFI_SNS

    for wifi_sn in wifi_sns:
        data = collector.collect_data(wifi_sn)
        if data:
            print(f"Data collected and stored for {wifi_sn}")
        else:
            print(f"Failed to collect data for {wifi_sn}")