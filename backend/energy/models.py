from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    # dob = models.DateField(blank=True, null=True)
    octopus_api_key = models.CharField(max_length=100, blank=True, null=True)
    octopus_product_code = models.CharField(max_length=100, blank=True, null=True)
    octopus_tariff_code = models.CharField(max_length=100, blank=True, null=True)
    octopus_mpan = models.CharField(max_length=20, blank=True, null=True)
    octopus_meter_serial = models.CharField(max_length=50, blank=True, null=True)
    solax_api_key = models.CharField(max_length=100, blank=True, null=True)
    solax_serial_number = models.CharField(max_length=50, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    

class Device(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices', null=True, blank=True)
    name = models.CharField(max_length=100)
    # energy_usage = models.FloatField()
    status = models.BooleanField(default=False)

class EnergyData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    energy_consumed = models.FloatField()

class SolarInverterData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solar_inverter_data', null=True, blank=True)
    inverter_sn = models.CharField(max_length=50)
    wifi_sn = models.CharField(max_length=50)
    ac_power = models.FloatField(null=True)
    yield_today = models.FloatField(null=True)
    yield_total = models.FloatField(null=True)
    feedin_power = models.FloatField(null=True)
    feedin_energy = models.FloatField(null=True)
    consume_energy = models.FloatField(null=True)
    battery_power = models.FloatField(null=True)
    battery_soc = models.FloatField(null=True)
    pv1_power = models.FloatField(null=True)
    pv2_power = models.FloatField(null=True)
    inverter_status = models.CharField(max_length=10)
    upload_time = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_synthetic = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['inverter_sn', 'upload_time']),
        ]

class HourlyEnergyConsumption(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='energy_consumptions', null=True, blank=True)
    interval_start = models.DateTimeField()
    interval_end = models.DateTimeField()
    consumption = models.FloatField()
    mpan = models.CharField(max_length=20)
    meter_serial = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.interval_start} - {self.interval_end}: {self.consumption} kWh"
    
class YearlyEnergyConsumption(models.Model):
    year = models.IntegerField()
    total_consumption = models.FloatField()
    mpan = models.CharField(max_length=20)
    meter_serial = models.CharField(max_length=50) 

    def __str__(self):
        return f"Year {self.year}: {self.total_consumption} kWh"

class WeatherData(models.Model):
    date_time = models.DateTimeField()
    temperature = models.FloatField()
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    weather_description = models.CharField(max_length=255)
    clouds = models.IntegerField()

    def __str__(self):
        return f"Weather on {self.date_time}: {self.weather_description}"

class SyntheticSolarData(models.Model):
    upload_time = models.DateTimeField(null=True, blank=True)
    ac_power = models.FloatField()
    yield_today = models.FloatField()

class PeakHour(models.Model):
    start = models.TimeField()
    end = models.TimeField()

class AutomationRule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='automation_rules', null=True, blank=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    days_of_week = models.JSONField(default=list)  # e.g., ["Monday", "Wednesday"]
    action = models.CharField(max_length=10, choices=[('on', 'Turn On'), ('off', 'Turn Off')])

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rule for {self.device.name}: {self.action} from {self.start_time} to {self.end_time} on {', '.join(self.days_of_week)}"

class CommunityPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    message = models.TextField()
    automation_rules = models.ManyToManyField(AutomationRule)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.email} on {self.created_at}: {self.message[:20]}..."