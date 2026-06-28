from django.urls import path
from .views import ApplyToJobView, MyApplicationsView, CompanyApplicationsView, UpdateApplicationStatusView

urlpatterns = [
    path("applications", ApplyToJobView.as_view(), name="apply-to-job"),
    path("applications/mine", MyApplicationsView.as_view(), name="my-applications"),
    path("applications/for-company", CompanyApplicationsView.as_view(), name="company-applications"),
    path("applications/<int:pk>/status", UpdateApplicationStatusView.as_view(), name="application-status"),
]
