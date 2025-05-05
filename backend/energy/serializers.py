from rest_framework import serializers
from .models import Device, EnergyData, SolarInverterData, SyntheticSolarData, CustomUser, CommunityPost, AutomationRule


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'name', 'status', 'user']

class EnergyDataSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    class Meta:
        model = EnergyData
        fields = ['id', 'device', 'device_name', 'timestamp', 'energy_consumed']

class SolarInverterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolarInverterData
        fields = '__all__'

class SyntheticSolarDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyntheticSolarData
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'octopus_api_key', 'octopus_meter_serial', 'octopus_mpan', 'octopus_product_code', 'octopus_tariff_code', 'solax_api_key', 'solax_serial_number']

class AutomationRuleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    class Meta:
        model = AutomationRule
        fields = ['id', 'user', 'device', 'action', 'start_time', 'end_time', 'days_of_week']

class CommunityPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    automation_rules = AutomationRuleSerializer(many=True, read_only=True)
    automation_rules_ids = serializers.ListField(write_only=True, child=serializers.IntegerField(), required=True)

    class Meta:
        model = CommunityPost
        fields = ['id', 'user', 'user_id', 'message', 'automation_rules', 'automation_rules_ids', 'created_at']
    
    def create(self, validated_data):
        automation_rules_data = validated_data.pop('automation_rules_ids')
        user_id = validated_data.pop('user_id')
        user = CustomUser.objects.get(id=user_id)
        print(f"DEBUG: Creating post with automation rules data: {automation_rules_data}")
        post = CommunityPost.objects.create(**validated_data)
        post.automation_rules.set(automation_rules_data)
        return post