from django.contrib import admin
from .models import Device, EnergyData, SolarInverterData, HourlyEnergyConsumption, YearlyEnergyConsumption, WeatherData, SyntheticSolarData, PeakHour, CustomUser, AutomationRule, CommunityPost

# Register your models here.
admin.site.register(Device)
admin.site.register(EnergyData)
admin.site.register(YearlyEnergyConsumption)
admin.site.register(PeakHour)
admin.site.register(CustomUser)
admin.site.register(AutomationRule)
admin.site.register(CommunityPost)
# admin.site.register(SyntheticSolarData)

class SolarInverterDataAdmin(admin.ModelAdmin):
    list_display = ("upload_time", "inverter_sn", "wifi_sn", "ac_power", "yield_today", "yield_total", "feedin_power", "consume_energy", "battery_soc")
    list_filter = ("upload_time", "inverter_sn")
    search_fields = ("inverter_sn", "wifi_sn")
    date_hierarchy = "upload_time"

    def formatted_upload_time(self, obj):
        return obj.upload_time.strftime("%Y-%m-%d %H:%M")

    formatted_upload_time.short_description = "Upload Time"

# admin.site.unregister(SolarInverterData)  
admin.site.register(SolarInverterData, SolarInverterDataAdmin)

class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ("formatted_date_time", "temperature", "humidity", "wind_speed", "weather_description", "clouds")  
    list_filter = ("date_time", "weather_description")  
    search_fields = ("date_time", "weather_description")  
    date_hierarchy = "date_time"

    def formatted_date_time(self, obj):
        return obj.date_time.strftime("%Y-%m-%d %H:%M")

    formatted_date_time.short_description = "Date & Time"

admin.site.register(WeatherData, WeatherDataAdmin)

class HourlyEnergyConsumptionAdmin(admin.ModelAdmin):
    list_display = ("interval_start", "interval_end", "consumption")  # Shows selected columns
    list_filter = ("interval_start",)  # Enables filtering by start date
    search_fields = ("interval_start", "interval_end")  # Allows searching by date
    date_hierarchy = "interval_start" # Enables date navigation at the top

    def formatted_interval_start(self, obj):
        return obj.interval_start.strftime("%Y-%m-%d %H:%M")

    def formatted_interval_end(self, obj):
        return obj.interval_end.strftime("%Y-%m-%d %H:%M")
    
    formatted_interval_start.short_description = "Start Time"
    formatted_interval_end.short_description = "End Time"

admin.site.register(HourlyEnergyConsumption, HourlyEnergyConsumptionAdmin)

class SyntheticSolarDataAdmin(admin.ModelAdmin):
    list_display = ("formatted_upload_time", "ac_power", "yield_today")  # Customize displayed columns
    list_filter = ("upload_time",)  # Add filtering options for better navigation
    search_fields = ("upload_time",)  # Enable search by upload time
    date_hierarchy = "upload_time"  # Add date navigation at the top

    def formatted_upload_time(self, obj):
        """Format upload time for better readability"""
        return obj.upload_time.strftime("%Y-%m-%d %H:%M")  # Display in YYYY-MM-DD HH:MM format
    
    formatted_upload_time.short_description = "Upload Time" 

admin.site.register(SyntheticSolarData, SyntheticSolarDataAdmin)