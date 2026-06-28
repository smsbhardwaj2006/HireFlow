from rest_framework import serializers
from .models import Officer


class OfficerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class OfficerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officer
        fields = ["id", "name", "email", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]
