from rest_framework import serializers
from .models import Company


class CompanyRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Company
        fields = ["name", "email", "password", "website", "description"]

    def validate_email(self, value):
        if Company.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        company = Company(**validated_data, status="pending")
        company.set_password(password)
        company.save()
        return company


class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "email", "website", "description", "status", "date_joined"]
        read_only_fields = ["id", "email", "status", "date_joined"]
