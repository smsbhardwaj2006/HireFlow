from django.urls import path
from .views import ScheduleInterviewView, MyInterviewsView, CompanyInterviewsView, InterviewDetailView

urlpatterns = [
    path("interviews", ScheduleInterviewView.as_view(), name="schedule-interview"),
    path("interviews/mine", MyInterviewsView.as_view(), name="my-interviews"),
    path("interviews/for-company", CompanyInterviewsView.as_view(), name="company-interviews"),
    path("interviews/<int:pk>", InterviewDetailView.as_view(), name="interview-detail"),
]
