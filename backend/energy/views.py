from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import AutomationRule, CustomUser, Device, EnergyData, SolarInverterData, HourlyEnergyConsumption, WeatherData, SyntheticSolarData, CommunityPost
from .serializers import DeviceSerializer, EnergyDataSerializer, SolarInverterDataSerializer, SyntheticSolarDataSerializer, UserSerializer, CommunityPostSerializer, AutomationRuleSerializer
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST, require_http_methods
from django.utils.timezone import now, timedelta
from django.views import View
from django.shortcuts import redirect
import json
import requests
from requests.auth import HTTPBasicAuth
from .weather_service import WeatherService
from energy import automation
from datetime import datetime, timezone
from energy import automation
from .backend import MyBackend as MyBackend
from .automation import save_automation_rule, get_automation_rules
import energy.views as views

# Create your views here.
  
@api_view(['GET'])
def device_list(request):
    devices = Device.objects.filter(user=request.user)
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)
    
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def add_device(request):
    user = request.data.get('user')
    user_id = user.get('id')
    CustomUser = get_user_model()
    try:
        user_instance = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = DeviceSerializer(data=request.data.get('name'))
    if serializer.is_valid():
        serializer.save(user=user_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_device(request, device_id):
    try:
        device = Device.objects.get(id=device_id, user=request.user)
    except Device.DoesNotExist:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DeviceSerializer(device, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_device(request, device_id):
    user = request.data.get('user')
    user_id = user.get('id')
    CustomUser = get_user_model()
    try:
        user_instance = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    try:
        device = Device.objects.get(id=device_id, user=user_instance)
        device.delete()
        return Response({"message": "Device deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Device.DoesNotExist:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

def toggle_device(request, device_id):
    try:
        device = Device.objects.get(id=device_id)
        if device.status:
            automation.turn_off_device(device_id)
        else:
            automation.turn_on_device(device_id)
        return JsonResponse({"success": True, "status": device.status})
    except Device.DoesNotExist:
        return JsonResponse({"error": "Device not found"}, status=404)

class EnergyDataViewSet(viewsets.ModelViewSet):
    queryset = EnergyData.objects.all()
    serializer_class = EnergyDataSerializer

class SolarDataViewSet(viewsets.ModelViewSet):
    queryset = SolarInverterData.objects.all() 
    serializer_class = SolarInverterDataSerializer

SOLAX_API_URL =settings.SOLAX_API_URL
# SOLAX_API_TOKEN = settings.SOLAX_API_TOKEN
# SOLAX_WIFI_SNS = settings.SOLAX_WIFI_SNS

# @login_required
@method_decorator(csrf_exempt, name='dispatch')
class ProxySolarDataView(View):
    def get(self, request):
        user_id = request.GET.get('user[id]')
        user = get_user(user_id)
        print(f"DEBUG: User from GET: {user}")
        print(f"DEBUG: User info from GET: {user.solax_api_key} {user.solax_serial_number}")
        print(f"DEBUG: request: {request.GET}")
        params = {
            "tokenId": user.solax_api_key,
            "sn": user.solax_serial_number,
            # "tokenId": SOLAX_API_TOKEN,
            # "sn": SOLAX_WIFI_SNS,
        }
        try:
            response = requests.get(SOLAX_API_URL, params=params)
            response_data = response.json()
            return JsonResponse(response_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get_real_time_data(request):
        print("GET")
        return JsonResponse({"error": "USE POST instead"}, status=405)

# Octopus energy API details  
OCTOPUS_API_URL = settings.OCTOPUS_API_URL
# OCTOPUS_API_KEY = settings.OCTOPUS_API_KEY
# OCTOPUS_MPAN = settings.OCTOPUS_MPAN 
# OCTOPUS_SERIAL = settings.OCTOPUS_SERIAL

@method_decorator(csrf_exempt, name='dispatch')
class ProxyOctopusDataView(View):
    def get(self, request):
        group_by = request.GET.get("group_by", "hour")
        user = get_user(request.GET.get('user[id]'))
        print(f"DEBUG:Octopus user: {user}")
        if user is None:
            return JsonResponse({'error': 'User not found'}, status=404)
        print(f"DEBUG:Octopus User mpan: {user.octopus_mpan}")
        url = f"{OCTOPUS_API_URL}/{user.octopus_mpan}/meters/{user.octopus_meter_serial}/consumption/"
        print(url)
        params = {
            "order_by": "-period",  
            "page_size": 200,
            "group_by": group_by
        }

        try:
            response = requests.get(url, auth=(user.octopus_api_key, ""), params=params)
            if response.status_code == 200:
                data = response.json()
                return JsonResponse(data, safe=False)
            else:
                return JsonResponse({'error': 'Failed to fetch data from Octopus API'}, status=response.status_code)
        except:
            return JsonResponse({'error': 'Failed to fetch data from Octopus API'}, status=500)
        
def weather_view(request):
    city = request.GET.get("city", "London")
    weather_service = WeatherService(city)
    combined_weather_data = weather_service.get_combined_data()
    return JsonResponse(combined_weather_data, safe=False)

def get_hourly_energy_data(request):
    energy_data = HourlyEnergyConsumption.objects.all().values()
    return JsonResponse(list(energy_data), safe=False)

def get_historical_solar_data(request):
    three_months_ago = now() - timedelta(days=90)
    data = SolarInverterData.objects.filter(upload_time__gte=three_months_ago).order_by('upload_time')

    response_data = list(data.values('upload_time', 'ac_power', 'yield_today', 'battery_power', 'battery_soc', 'pv1_power', 'pv2_power'))
    return JsonResponse(response_data, safe=False)

def get_historical_weather_data(request):
    data = WeatherData.objects.all()
    response_data = list(data.values('date_time', 'temperature', 'humidity', 'wind_speed', 'weather_description', 'clouds'))
    return JsonResponse(response_data, safe=False)

def get_synthetic_solar_data(request):
    data = SyntheticSolarData.objects.all().values()
    return JsonResponse(list(data), safe=False)

@api_view(['POST'])
def upload_solar_data(request):
    serializer = SolarInverterDataSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Synthetic data saved"}, status=201)
    return Response(serializer.errors, status=400)

class SyntheticSolarDataUploadView(APIView):
    """Handles the upload of synthetic solar data"""
    def post(self, request, *args, **kwargs):
        # Ensure request.data is a dictionary and extract "data" key if present
        data = request.data if isinstance(request.data, list) else request.data.get("data", [])

        # Ensure it's a list before passing to the serializer
        if not isinstance(data, list):
            return Response({"error": "Invalid format: Expected a list"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SyntheticSolarDataSerializer(data=data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Synthetic solar data uploaded successfully!"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def cheapest_energy_prices(request):
    # Get the API key and codes from the request headers
    api_key = request.query_params.get('api_key')
    product_code = request.query_params.get('product_code')
    tariff_code = request.query_params.get('tariff_code')

    if not all([api_key, product_code, tariff_code]):
        return Response({"error": "Missing required headers"}, status=status.HTTP_400_BAD_REQUEST)
    
    cheapest = automation.get_cheapest_periods(api_key, product_code, tariff_code)
    return Response(cheapest, status=status.HTTP_200_OK)

active_automation = [] #temp to hold rules

@api_view(['POST'])
@permission_classes([AllowAny])
def recieve_automation_rules(request):
    try:
        device_id = request.data.get('device_id')
        scheduled = request.data.get('scheduled', [])
        user_data = request.data.get('user')
        if not device_id or not scheduled:
            return Response({'error': 'Missing device_id or slots'}, status=status.HTTP_400_BAD_REQUEST)

        views.active_automation = []
        user = get_user(user_data['id'])
        for item in scheduled:
            day = item['day']
            valid_from = item['valid_from']
            valid_to = item['valid_to']
            start_time = datetime.fromisoformat(valid_from.replace('Z', '+00:00')).time()
            end_time = datetime.fromisoformat(valid_to.replace('Z', '+00:00')).time()

            # Check if the rule already exists
            try:
                existing_rules = AutomationRule.objects.filter(
                    user=user,
                    device__id=device_id,
                    start_time=start_time,
                    end_time=end_time,
                    action='on'  
                )
                existing = any(day in rule.days_of_week for rule in existing_rules)
            except Exception as e:
                raise e # Handle the case where the rule does not exist
            if existing:
                continue

            views.active_automation.append({
                'device_id': device_id,
                'days': day,
                'valid_from': valid_from,
                'valid_to': valid_to,
            })
            
            save_automation_rule(
                user=user,
                device_id=device_id,
                valid_from=valid_from,
                valid_to=valid_to,
                days=day,
                action='on'  # Assuming the action is to turn on the device
            )

        automation.run_selected_devices_peak_periods()
        return Response({'message': 'Automation rules received successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt    
def fetch_automation_rules(request):
    # This function should fetch the automation rules from the database or any other source
    rules = get_automation_rules(request.user)
    return JsonResponse(rules, status=status.HTTP_200_OK, safe=False)

@csrf_exempt
def delete_automation_rule(request, rule_id):
    automation.delete_automation_rule(rule_id)
    return JsonResponse({"message": "Rule deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        name = data.get('name')
        octopus_api_key = data.get('octopus_api_key')
        octopus_product_code = data.get('octopus_product_code')
        octopus_tariff_code = data.get('octopus_tariff_code')
        octopus_mpan = data.get('octopus_mpan')
        octopus_serial = data.get('octopus_serial')
        solax_api_key = data.get('solax_api_key')
        solax_serial_number = data.get('solax_serial_number')
        password = data.get('password')
        confirmPassword = data.get('confirmPassword')
        if password != confirmPassword:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)
        
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        user = User.objects.create_user( 
            email=email, 
            name=name,
            username=email,
            octopus_api_key=octopus_api_key,
            octopus_product_code=octopus_product_code,
            octopus_tariff_code=octopus_tariff_code,
            octopus_mpan=octopus_mpan,
            octopus_meter_serial=octopus_serial,
            solax_api_key=solax_api_key, 
            solax_serial_number=solax_serial_number,
            password=password
        )
        user.save()
        return JsonResponse({"message": "User created successfully"}, status=201)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        user = get_user_model()
        print(f"DEBUG: User model: {user}")
        print(f"DEBUG: Request body: {user.objects.all()}")
        print(f"DEBUG: Request user: {request.user}")
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        password = data.get('password')
        auth_backend = MyBackend()
        user = auth_backend.authenticate(request, username=email, password=password)
        # user = authenticate(request, email=email, password=password)
        print(f"DEBUG: User logged in : {user}")
        if user is not None:
            print(f"DEBUG: Session ID: {request.session.session_key}")
            user.backend = 'energy.backend.MyBackend'
            print(f"DEBUG: User backend: {getattr(user, 'backend', None)}")
            login(request, user)
            request.session['user_id'] = str(user.id)
            request.session.save()
            print(f"DEBUG: Session data: {request.session.items()}")
            print("Request cookies:", request.COOKIES)
            print("Session ID:", request.COOKIES.get('sessionid'))
            # return redirect('energy')
            return JsonResponse({"message": "Login successful"}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@require_POST
@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('login')
    # return JsonResponse({"message": "Logout successful"}, status=200)

@require_http_methods(["GET"])
@login_required
def current_user(request):
    user = request.user
    serializer = UserSerializer(user)
    return JsonResponse(serializer.data, safe=False)

def get_user(user_id):
    try:
        user = get_user_model().objects.get(id=user_id)
        return user
    except get_user_model().DoesNotExist:
        return None


@login_required
@csrf_exempt
@require_http_methods({"GET", "PUT"})
def user_profile(request):
    user = request.user
    if request.method == 'GET':
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "octopus_api_key": user.octopus_api_key,
            "octopus_product_code": user.octopus_product_code,
            "octopus_tariff_code": user.octopus_tariff_code,
            "octopus_mpan": user.octopus_mpan,
            "octopus_meter_serial": user.octopus_meter_serial,
            "solax_api_key": user.solax_api_key,
            "solax_serial_number": user.solax_serial_number
        }
        return JsonResponse(user_data, safe=False)
    elif request.method == 'PUT':
        data = json.loads(request.body.decode('utf-8'))
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.octopus_api_key = data.get('octopus_api_key', user.octopus_api_key)
        user.octopus_product_code = data.get('octopus_product_code', user.octopus_product_code)
        user.octopus_tariff_code = data.get('octopus_tariff_code', user.octopus_tariff_code)
        user.octopus_mpan = data.get('octopus_mpan', user.octopus_mpan)
        user.octopus_meter_serial = data.get('octopus_meter_serial', user.octopus_meter_serial)
        user.solax_api_key = data.get('solax_api_key', user.solax_api_key)
        user.solax_serial_number = data.get('solax_serial_number', user.solax_serial_number)
        user.save()
        return JsonResponse({"message": "User profile updated successfully"}, status=200)
    
@ensure_csrf_cookie
def csrf_cookie_view(request):
    return JsonResponse({'message': 'CSRF cookie set'})

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_community_posts(request):
    posts = CommunityPost.objects.select_related('user').prefetch_related('automation_rules').all().order_by('-created_at')
    serializer = CommunityPostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@csrf_exempt
def create_community_post(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        message = data.get('message')
        rule_ids = data.get('rule_ids', [])

        user = CustomUser.objects.get(id=user_id)
        post = CommunityPost.objects.create(user=user, message=message)
        post.automation_rules.set(rule_ids)

        return JsonResponse({"message": "Post created successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)