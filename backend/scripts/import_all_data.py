import os 
import sys
import django
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from energy.models import EnergyData, SolarInverterData, SyntheticSolarData, HourlyEnergyConsumption, YearlyEnergyConsumption, WeatherData

def import_energy_data():
    with open('backup-data/energy_energydata.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            EnergyData.objects.create(
                id=row['id'],
                device_id=row['device_id'],
                timestamp=row['timestamp'],
                energy_consumed=row['energy_consumed']
            )
    print("Energy data imported successfully.")

def import_hourly_energy_consumption():
    with open('backup-data/energy_hourlyenergyconsumption.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            HourlyEnergyConsumption.objects.create(
                id=row['id'],
                interval_start=row['interval_start'],
                interval_end=row['interval_end'],
                consumption=row['consumption'],
                mpan=row['mpan'],
                meter_serial=row['meter_serial']
            )
    print("Hourly energy consumption data imported successfully.")

def import_yearly_energy_consumption():
    with open('backup-data/energy_yearlyenergyconsumption.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            YearlyEnergyConsumption.objects.create(
                id=row['id'],
                year=row['year'],
                total_consumption=row['total_consumption'],
                mpan=row['mpan'],
                meter_serial=row['meter_serial']
            )
    print("Yearly energy consumption data imported successfully.")

def import_solar_inverter_data():
    with open('backup-data/energy_solarinverterdata.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            SolarInverterData.objects.create(
                id=row['id'],
                timestamp=row['timestamp'],
                inverter_sn=row['inverter_sn'],
                wifi_sn=row['wifi_sn'],
                ac_power=row['ac_power'],
                yield_today=row['yield_today'],
                yield_total=row['yield_total'],
                feedin_power=row['feedin_power'],
                feedin_energy=row['feedin_energy'],
                consume_energy=row['consume_energy'],
                battery_power=row['battery_power'],
                battery_soc=row['battery_soc'],
                pv1_power=row['pv1_power'],
                pv2_power=row['pv2_power'],
                inverter_status=row['inverter_status'],
                upload_time=row['upload_time'],
                is_synthetic=row['is_synthetic']
            )
    print("Solar inverter data imported successfully.")

def import_synthetic_solar_data():
    with open('backup-data/energy_syntheticsolardata.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            SyntheticSolarData.objects.create(
                id=row['id'],    
                upload_time=row['upload_time'],
                ac_power=row['ac_power'],
                yield_today=row['yield_today'],
            )
    print("Synthetic solar data imported successfully.")

def import_weather():
    with open('backup-data/energy_weatherdata.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            WeatherData.objects.create(
                id=row['id'],
                date_time=row['date_time'],
                temperature=row['temperature'],
                clouds=row['clouds'],
                wind_speed=row['wind_speed'],
                weather_description=row['weather_description'],
                humidity=row['humidity'],
               
            )
    print("Weather data imported successfully.")

# import_energy_data()
# import_hourly_energy_consumption()
# import_yearly_energy_consumption()
# import_solar_inverter_data()
import_synthetic_solar_data()
import_weather()

# if __name__ == "__main__":
#     run()