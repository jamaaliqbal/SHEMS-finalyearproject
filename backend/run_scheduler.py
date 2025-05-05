import os 
import time 
import schedule 
import django 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from energy.automation import manage_device, run_selected_devices_peak_periods

def scheduled_task():
   # print("Runnign scheduled device manager")
   # manage_device(
   #    device_id=1,
   #    product_code="AGILE-24-10-01",
   #    tariff_code="E-1R-AGILE-24-10-01-J")
   print("Running selected devices peak periods")
   run_selected_devices_peak_periods()

schedule.every(5).seconds.do(scheduled_task)

if __name__ == '__main__':
   print("Starting scheduler...")
   while True:
       schedule.run_pending()
       time.sleep(1)