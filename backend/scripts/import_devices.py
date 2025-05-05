import os 
import sys
import django
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from energy.models import Device

print("Django setup complete.")

def run():
    print("Importing devices from CSV...")
    with open('backup-data/energy_device.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print("CSV file opened successfully.")
        for row in reader:
            Device.objects.create(
                id=row['id'],
                name=row['name'],
                status=row['status'],
                energy_usage=row['energy_usage']
            )

    print("Devices imported successfully.")

