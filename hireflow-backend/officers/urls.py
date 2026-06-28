from django.urls import path
from .views import OfficerLoginView, OfficerProfileView, OfficerDashboardStatsView, OfficerReportsView

urlpatterns = [
    path("officers/login", OfficerLoginView.as_view(), name="officer-login"),
    path("officers/profile", OfficerProfileView.as_view(), name="officer-profile"),
    path("officers/dashboard-stats", OfficerDashboardStatsView.as_view(), name="officer-dashboard-stats"),
    path("officers/reports", OfficerReportsView.as_view(), name="officer-reports"),
]
