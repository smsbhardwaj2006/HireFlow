from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id", "company", "company_name", "title", "description", "location",
            "salary", "job_type", "min_cgpa", "eligible_branches", "deadline", "drive_date", "created_at",
        ]
        read_only_fields = ["id", "company_name", "created_at"]

    def validate_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Salary must be greater than zero.")
        return value

    def validate_eligible_branches(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Select at least one eligible branch.")
        return value
