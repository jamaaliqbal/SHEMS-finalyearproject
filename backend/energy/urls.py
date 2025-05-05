"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnergyDataViewSet, ProxySolarDataView, SolarDataViewSet, ProxyOctopusDataView, weather_view, get_hourly_energy_data, get_historical_solar_data, get_historical_weather_data, upload_solar_data, SyntheticSolarDataUploadView, get_synthetic_solar_data
from energy import views

router = DefaultRouter()
# router.register('devices', DeviceViewSet)
router.register('energy-data', EnergyDataViewSet)
router.register('solar-data', SolarDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('api/', include(router.urls)),
    path("api/solax-data/", ProxySolarDataView.as_view(), name="solax-data"),
    path("api/octopus-data/", ProxyOctopusDataView.as_view(), name="octopus-data"),
    path("api/weather/", weather_view, name="weather_api"),
    path("api/hourly-data/", get_hourly_energy_data, name='get_hourly_energy_data'),
    path("api/solar-data/", get_historical_solar_data, name='solar_data'),
    path("api/weather-data/", get_historical_weather_data, name='weather_data'),
    path("api/upload-solar-data/", upload_solar_data, name="upload_solar_data"),
    path('api/upload-synthetic-data/', SyntheticSolarDataUploadView.as_view(), name='upload_synthetic_data'),
    path('api/synthetic-solar-data/', get_synthetic_solar_data, name='synthetic_solar_data'),
    path("api/devices/", views.device_list, name="device_list"),
    path("api/devices/<int:device_id>/toggle/", views.toggle_device, name="toggle_device"),
    path("api/devices/create/", views.add_device, name="create_device"),
    path("api/devices/<int:device_id>/edit/", views.update_device, name="edit_device"),
    path("api/devices/<int:device_id>/delete/", views.delete_device, name="delete_device"),
    path("api/cheapest-energy-slots/", views.cheapest_energy_prices, name="cheapest_energy_prices"),
    path('api/save-automation/', views.recieve_automation_rules, name='receive_automation'),
    path('api/get-automation-rules/', views.fetch_automation_rules, name='get_automation_rules'),
    path('api/delete-automation-rule/<int:rule_id>/', views.delete_automation_rule, name='delete_automation_rules'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('api/current-user/', views.current_user, name='current_user'),
    path('api/profile/', views.user_profile, name='user_profile'),
    path('csrf-token/', views.csrf_cookie_view, name='csrf_token'),
    path('api/get-community-posts/', views.get_community_posts, name='community_posts'),
    path('api/create-community-post/', views.create_community_post, name='create_community_post'),
    # path('', views.login_view, name='login'),
]
