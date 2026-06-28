"""
Interview views.

POST /api/interviews                 -> company schedules an interview for
                                         a shortlisted application (also
                                         advances that application's status
                                         to "interview" — same business rule
                                         the frontend prototype encodes)
GET  /api/interviews/mine            -> student's own interviews
GET  /api/interviews/for-company     -> all interviews the company has scheduled
PUT  /api/interviews/{id}            -> edit details (PRD: "Edit Interview Details")
"""

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from students.permissions import IsStudent
from companies.permissions import IsCompany
from applications.models import Application
from .models import Interview
from .serializers import InterviewSerializer, ScheduleInterviewSerializer


class ScheduleInterviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def post(self, request):
        serializer = ScheduleInterviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Only allow scheduling for an application against one of this
        # company's own jobs — same ownership check pattern as
        # UpdateApplicationStatusView in applications/views.py.
        application = get_object_or_404(Application, pk=data["application_id"], job__company=request.user)

        if hasattr(application, "interview"):
            return Response({"error": "An interview is already scheduled for this application."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            interview = Interview.objects.create(
                application=application, date=data["date"], time=data["time"], venue=data["venue"],
            )
            application.status = "interview"
            application.save(update_fields=["status"])

        return Response(InterviewSerializer(interview).data, status=status.HTTP_201_CREATED)


class MyInterviewsView(generics.ListAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Interview.objects.filter(application__student=self.request.user).select_related(
            "application", "application__job", "application__job__company"
        )


class CompanyInterviewsView(generics.ListAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get_queryset(self):
        return Interview.objects.filter(application__job__company=self.request.user).select_related(
            "application", "application__student"
        )


class InterviewDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get_queryset(self):
        # A company can only ever edit interviews tied to its own jobs.
        return Interview.objects.filter(application__job__company=self.request.user)
