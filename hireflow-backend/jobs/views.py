"""
Job views.

GET  /api/jobs                  -> list (students see only approved-company
                                    jobs; ?eligible_only=true filters to jobs
                                    the logged-in student actually qualifies for)
GET  /api/jobs/{id}             -> detail
POST /api/jobs                  -> create (company only, own company)
PUT/DELETE /api/jobs/{id}       -> update/delete (company only, own job)
GET  /api/companies/{id}/jobs   -> all jobs for one company (company dashboard)
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from companies.permissions import IsCompany
from students.permissions import IsStudent
from .models import Job
from .serializers import JobSerializer


class IsCompanyOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and getattr(request.user, "auth_role", None) == "company")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.company_id == request.user.id


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsCompanyOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["job_type", "company"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        qs = Job.objects.select_related("company").filter(company__status="approved")

        role = getattr(self.request.user, "auth_role", None)
        if role == "student" and self.request.query_params.get("eligible_only") == "true":
            student = self.request.user
            qs = [job for job in qs if job.is_eligible_for(student)]
            return qs  # list, not queryset — fine for DRF serialization either way

        return qs

    def perform_create(self, serializer):
        # Companies can only ever create jobs under their own company id —
        # never an arbitrary company_id passed in the request body.
        serializer.save(company=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.select_related("company").all()
    serializer_class = JobSerializer
    permission_classes = [IsCompanyOwnerOrReadOnly]


class CompanyJobListView(generics.ListAPIView):
    """A company's own jobs, including ones not yet visible to students
    (e.g. while the company itself is still pending approval)."""

    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get_queryset(self):
        return Job.objects.filter(company=self.request.user)
