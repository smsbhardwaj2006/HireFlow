from django.urls import path
from .views import (
    CompanyRegisterView, CompanyLoginView, CompanyProfileView,
    AdminCompanyListView, AdminCompanyDetailView, AdminApproveCompanyView,
)

urlpatterns = [
    path("companies/register", CompanyRegisterView.as_view(), name="company-register"),
    path("companies/login", CompanyLoginView.as_view(), name="company-login"),
    path("companies/profile", CompanyProfileView.as_view(), name="company-profile"),

    # Officer-only management
    path("admin/companies", AdminCompanyListView.as_view(), name="admin-company-list"),
    path("admin/companies/<int:pk>", AdminCompanyDetailView.as_view(), name="admin-company-detail"),
    path("admin/companies/<int:pk>/approve", AdminApproveCompanyView.as_view(), name="admin-company-approve"),
]
