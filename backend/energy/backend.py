from django.contrib.auth.backends import BaseBackend
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from energy.models import CustomUser as User


class MyBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                user.backend = 'energy.backend.MyBackend'
                return user
            else:
                return None
        except User.DoesNotExist:
            
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def signup(self, username, email, password):
        exist = User.objects.filter(email__iexact=email).exists()
        if exist:
            return JsonResponse({"error": "Email already in use"}, status=400)
        
        new_user = User.objects.create_user(username=username, email=email, password=password)
        new_user.save()
        return new_user
