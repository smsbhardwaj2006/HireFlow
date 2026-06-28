"""
Officer login + profile.

POST /api/officers/login      -> JWT tokens (role="officer")
GET  /api/officers/profile    -> view own profile

No officer self-registration endpoint — see models.py docstring and the
create_officer management command.
"""

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg

from config.tokens import issue_tokens_for
from students.models import Student
from companies.models import Company
from jobs.models import Job
from applications.models import Application
from .models import Officer
from .serializers import OfficerLoginSerializer, OfficerProfileSerializer
from .permissions import IsOfficer


class OfficerLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OfficerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            officer = Officer.objects.get(email__iexact=email)
        except Officer.DoesNotExist:
            return Response({"error": "No officer account matches those credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not officer.check_password(password):
            return Response({"error": "No officer account matches those credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = issue_tokens_for(officer, "officer")
        return Response({"user": OfficerProfileSerializer(officer).data, **tokens})


class OfficerProfileView(generics.RetrieveAPIView):
    serializer_class = OfficerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOfficer]

    def get_object(self):
        return self.request.user


class OfficerDashboardStatsView(APIView):
    """PRD: Officer dashboard displays Total Students, Registered
    Companies, Placement Drives, Placement Statistics, Recent Activities."""

    permission_classes = [permissions.IsAuthenticated, IsOfficer]

    def get(self, request):
        total_students = Student.objects.count()
        total_companies = Company.objects.count()
        selected_count = Application.objects.filter(status="selected").count()
        placement_rate = round((selected_count / total_students) * 100, 1) if total_students else 0

        return Response({
            "total_students": total_students,
            "total_companies": total_companies,
            "pending_companies": Company.objects.filter(status="pending").count(),
            "total_jobs": Job.objects.count(),
            "total_applications": Application.objects.count(),
            "students_selected": selected_count,
            "placement_rate": placement_rate,
        })


class OfficerReportsView(APIView):
    """PRD: Reports module — Student Reports, Company Reports, Placement
    Statistics, Department-wise Reports."""

    permission_classes = [permissions.IsAuthenticated, IsOfficer]

    def get(self, request):
        # Department-wise: group students by branch, compute placement rate per branch
        branches = Student.objects.values_list("branch", flat=True).distinct()
        department_report = []
        for branch in branches:
            branch_students = Student.objects.filter(branch=branch)
            total = branch_students.count()
            placed = Application.objects.filter(status="selected", student__branch=branch).count()
            department_report.append({
                "branch": branch,
                "total_students": total,
                "placed": placed,
                "placement_rate": round((placed / total) * 100, 1) if total else 0,
            })

        # Company-wise: jobs posted, applications received, candidates selected, per company
        company_report = []
        for company in Company.objects.all():
            company_jobs = Job.objects.filter(company=company)
            company_apps = Application.objects.filter(job__company=company)
            company_report.append({
                "company": company.name,
                "jobs_posted": company_jobs.count(),
                "applications_received": company_apps.count(),
                "selected": company_apps.filter(status="selected").count(),
            })

        selected_apps = Application.objects.filter(status="selected").select_related("job")
        avg_package = selected_apps.aggregate(Avg("job__salary"))["job__salary__avg"] or 0

        return Response({
            "department_report": department_report,
            "company_report": company_report,
            "average_package": round(float(avg_package), 2),
        })

