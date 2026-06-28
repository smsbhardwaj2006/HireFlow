from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company.name", read_only=True)
    student_name = serializers.CharField(source="student.name", read_only=True)
    student_cgpa = serializers.DecimalField(source="student.cgpa", max_digits=4, decimal_places=2, read_only=True)
    student_branch = serializers.CharField(source="student.branch", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id", "student", "job", "status", "applied_date",
            "job_title", "company_name", "student_name", "student_cgpa", "student_branch",
        ]
        read_only_fields = ["id", "status", "applied_date"]


class ApplyToJobSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()


class UpdateApplicationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["review", "shortlisted", "interview", "selected", "rejected"])
