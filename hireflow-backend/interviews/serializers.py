from rest_framework import serializers
from .models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="application.student.name", read_only=True)
    company_name = serializers.CharField(source="application.job.company.name", read_only=True)
    job_title = serializers.CharField(source="application.job.title", read_only=True)

    class Meta:
        model = Interview
        fields = ["id", "application", "student_name", "company_name", "job_title", "date", "time", "venue", "status", "created_at"]
        read_only_fields = ["id", "student_name", "company_name", "job_title", "created_at"]


class ScheduleInterviewSerializer(serializers.Serializer):
    application_id = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.TimeField()
    venue = serializers.CharField(max_length=255)
