"""
Application views.

POST /api/applications              -> student applies to a job
GET  /api/applications/mine         -> student's own applications
GET  /api/applications/for-company  -> all applications across the
                                        logged-in company's jobs
PUT  /api/applications/{id}/status  -> company advances/rejects an application
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from students.permissions import IsStudent
from companies.permissions import IsCompany
from jobs.models import Job
from .models import Application
from .serializers import ApplicationSerializer, ApplyToJobSerializer, UpdateApplicationStatusSerializer


class ApplyToJobView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request):
        serializer = ApplyToJobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = get_object_or_404(Job, id=serializer.validated_data["job_id"])
        student = request.user

        if not job.is_eligible_for(student):
            return Response(
                {"error": "You don't meet the eligibility criteria for this job."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Application.objects.filter(student=student, job=job).exists():
            return Response({"error": "You've already applied to this job."}, status=status.HTTP_400_BAD_REQUEST)
        if not student.resume:
            return Response({"error": "Upload your resume before applying."}, status=status.HTTP_400_BAD_REQUEST)

        application = Application.objects.create(student=student, job=job)
        return Response(ApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user).select_related("job", "job__company")


class CompanyApplicationsView(generics.ListAPIView):
    """All applications across every job posted by the logged-in company —
    PRD: 'Companies can: View Applicants'."""

    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get_queryset(self):
        return Application.objects.filter(job__company=self.request.user).select_related("student", "job")


class UpdateApplicationStatusView(APIView):
    """Company shortlists/advances/rejects a candidate. Only the company
    that owns the job can update its applications — never another
    company's, enforced by the get_object_or_404 filter below rather than
    trusting an application_id alone."""

    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def put(self, request, pk):
        application = get_object_or_404(Application, pk=pk, job__company=request.user)
        serializer = UpdateApplicationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application.status = serializer.validated_data["status"]
        application.save(update_fields=["status"])
        return Response(ApplicationSerializer(application).data)
