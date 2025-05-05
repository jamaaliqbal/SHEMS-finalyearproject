from datetime import datetime, timedelta, timezone
from .models import Device, PeakHour, AutomationRule
import requests
from requests.auth import HTTPBasicAuth
from energy import views

def is_peak_hour(api_key, product_code, tariff_code, threshold=25.0):
    try:
        url = f"https://api.octopus.energy/v1/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/"
        response = requests.get(url, auth=HTTPBasicAuth(api_key, ''))

        if response.status_code != 200:
            print(f"Failed to fetch prices: {response.status_code}")
            return False
        
        data = response.json()
        # print(f"DEBUG: Fetched data: {data}")
        now = datetime.now(timezone.utc)



        for entry in data.get("results", []):
            valid_from = datetime.fromisoformat(entry["valid_from"].replace("Z", "+00:00"))
            valid_to = datetime.fromisoformat(entry["valid_to"].replace("Z", "+00:00"))

            if valid_from <= now < valid_to:
                price = entry["value_inc_vat"]
                print(f"Current price: {price}p/kWh at {now}")
                return price >= threshold

        return False

    except Exception as e:
        print(f"Error during peak hour check: {e}")
        return False
    # return PeakHour.objects.filter(start__lte=now, end__gte=now).exists()

def get_cheapest_periods(api_key, product_code, tariff_code, slots=48):
    try:
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=24)

        period_from = start.isoformat(timespec='seconds').replace("+00:00", "Z")
        period_to = now.isoformat(timespec='seconds').replace("+00:00", "Z")

        url = (
            f"https://api.octopus.energy/v1/products/{product_code}/"
            f"electricity-tariffs/{tariff_code}/standard-unit-rates/"
            f"?period_from={period_from}&period_to={period_to}"
        )

        # print(f"DEBUG URL: {url}")
        # print(f"From: {period_from}")
        # print(f"To: {period_to}")
        response = requests.get(url, auth=HTTPBasicAuth(api_key, ''))
        # print(f"DEBUG: Response : {response}")

        if response.status_code != 200:
            print(f"Failed to fetch prices: {response.status_code}")
            return []
        
        data = response.json()
        # print(f"DEBUG: Fetched data: {data}")
        periods = data.get("results", [])

        sorted_periods = sorted(periods, key=lambda x: x["value_inc_vat"])
        cheapest_periods = sorted_periods[:slots]

        return cheapest_periods

    except Exception as e:
        print(f"Error during fetching cheapest periods: {e}")
        return []
    
def run_selected_devices_peak_periods():
    now = datetime.now(timezone.utc)
    now_time = now.time()
    now_day = now.strftime("%A")
    triggered_devices = set()
    print(f"DEBUG: views.active_automation: {views.active_automation}")
    for rule in views.active_automation:
        # Check if the current day is in the rule's days
        print(f"DEBUG: Current day: {now_day}, Rule day: {rule['days']}")
        if rule['days'] != now_day:
            continue
        # Check if the current time is within the rule's valid period
        start = datetime.fromisoformat(rule["valid_from"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(rule["valid_to"].replace("Z", "+00:00"))
        start_time = start.time()
        end_time = end.time()
        print(f"DEBUG: Start time: {start_time}, End time: {end_time}, Now time: {now_time}")
        if start_time <= now_time < end_time:
            triggered_devices.add(rule["device_id"])
            print("Turning on device:", rule["device_id"])
            turn_on_device(rule["device_id"])
        print(f"DEBUG: Device {rule['device_id']} is in the triggered devices set")
    print(f"DEBUG: Triggered devices: {triggered_devices}")
    #Turn off devices that are not in the triggered devices set
    for device in Device.objects.all():
        if device.id not in triggered_devices:
            turn_off_device(device.id)

def save_automation_rule(user, device_id, valid_from, valid_to, days, action):
    print(f"DEBUG: Saving automation rule for device {device_id} from {valid_from} to {valid_to} on {days} with action {action} for user {user}")

    valid_from_dt = datetime.fromisoformat(valid_from.replace('Z', '+00:00')).time()
    valid_to_dt = datetime.fromisoformat(valid_to.replace('Z', '+00:00')).time()

    device = Device.objects.get(id=device_id)
    rule = AutomationRule.objects.create(
        user=user,
        device=device,
        start_time=valid_from_dt,
        end_time=valid_to_dt,
        days_of_week=days,
        action=action
    )
    rule.save()
    print(f"Automation rule saved: {rule}")
    return rule
    
def get_automation_rules(user):
    print(f"DEBUG: Getting automation rules for user {user}")
    rules = AutomationRule.objects.filter(user=user)
    rules_list = []
    for rule in rules:
        rules_list.append({
            "id": rule.id,
            "device_id": rule.device.id,
            "device_name" : rule.device.name,
            "valid_from": rule.start_time.isoformat(),
            "valid_to": rule.end_time.isoformat(),
            "days": rule.days_of_week,
            "action": rule.action,
            "user_id": rule.user.id,
        })
    return rules_list

def delete_automation_rule(rule_id):
    print(f"DEBUG: Deleting automation rule with id {rule_id}")
    try:
        rule = AutomationRule.objects.get(id=rule_id)
        rule.delete()
        print(f"Automation rule deleted: {rule}")
    except AutomationRule.DoesNotExist:
        print(f"Automation rule with id {rule_id} does not exist")

def manage_device(device_id, api_key, product_code, tariff_code):
    device_status = check_device_status(device_id)
    if device_status is None:
        return
    
    cheapest = get_cheapest_periods(api_key, product_code, tariff_code)
    for period in cheapest:
        print(f"{period['valid_from']} to {period['valid_to']}: {period['value_inc_vat']}p/kWh")

    if is_peak_hour(api_key, product_code, tariff_code):
        if device_status:
            turn_off_device(device_id)

    else:
        if not device_status:
            turn_on_device(device_id)
        

def check_device_status(device_id):
    try:
        device = Device.objects.get(id=device_id)
        return device.status
    except Device.DoesNotExist:
        print(f"Device with id {device_id} does not exist")
        return None

def turn_on_device(device_id):
    try:
        device = Device.objects.get(id=device_id)
        if not device.status:
            device.status = True
            device.save()
            print(f"{device.name} turned ON")
    except Device.DoesNotExist:
        print(f"Device with id {device_id} does not exist")

def turn_off_device(device_id):
    try:
        device = Device.objects.get(id=device_id)
        if device.status:
            device.status = False
            device.save()
            print(f"{device.name} turned OFF")
    except Device.DoesNotExist:
        print(f"Device with id {device_id} does not exist")
            