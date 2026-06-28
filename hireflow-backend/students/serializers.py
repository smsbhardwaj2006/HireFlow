from rest_framework import serializers
from .models import Student


class StudentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Student
        fields = ["name", "email", "password", "phone", "branch", "course", "cgpa"]

    def validate_email(self, value):
        if Student.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        student = Student(**validated_data)
        student.set_password(password)
        student.save()
        return student


class StudentLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class StudentProfileSerializer(serializers.ModelSerializer):
    profile_completion = serializers.IntegerField(read_only=True)

    class Meta:
        model = Student
        fields = ["id", "name", "email", "phone", "branch", "course", "cgpa", "skills", "resume", "profile_completion", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]
