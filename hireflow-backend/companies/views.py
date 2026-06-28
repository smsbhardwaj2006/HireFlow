"""
Company auth + profile views.

POST /api/companies/register  -> create account (status starts "pending")
POST /api/companies/login     -> JWT tokens (role="company")
GET/PUT /api/companies/profile -> view/edit own profile
"""

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from config.tokens import issue_tokens_for
from officers.permissions import IsOfficer
from .models import Company
from .serializers import CompanyRegisterSerializer, CompanyLoginSerializer, CompanyProfileSerializer
from .permissions import IsCompany


class CompanyRegisterView(generics.CreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        tokens = issue_tokens_for(company, "company")
        return Response(
            {
                "message": "Registered. Your account is pending placement officer approval.",
                "user": CompanyProfileSerializer(company).data,
                **tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class CompanyLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CompanyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            company = Company.objects.get(email__iexact=email)
        except Company.DoesNotExist:
            return Response({"error": "No company account matches those credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not company.check_password(password):
            return Response({"error": "No company account matches those credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = issue_tokens_for(company, "company")
        return Response({"user": CompanyProfileSerializer(company).data, **tokens})


class CompanyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompany]

    def get_object(self):
        return self.request.user


# ──────────────────────────────────────────────────────────────────────────
# Officer-only: manage companies (PRD section 4 — Approve Company
# Registration, Edit Company Information, Remove Companies)
# ──────────────────────────────────────────────────────────────────────────

class AdminCompanyListView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOfficer]


class AdminCompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOfficer]


class AdminApproveCompanyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOfficer]

    def post(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        company.status = "approved"
        company.save(update_fields=["status"])
        return Response(CompanyProfileSerializer(company).data)

