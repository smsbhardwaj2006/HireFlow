"""
Seeds demo data mirroring hireflow-frontend/js/data.js, so both halves of
the project describe the same companies/jobs even though they aren't wired
together yet.

Run with: python manage.py seed_demo_data

Creates the same three demo login accounts the frontend's login pages are
pre-filled with:
  Student:  ananya@college.edu / demo1234
  Company:  hr@nexora.com / demo1234
  Officer:  officer@college.edu / demo1234
"""

from django.core.management.base import BaseCommand
from students.models import Student
from companies.models import Company
from officers.models import Officer
from jobs.models import Job


class Command(BaseCommand):
    help = "Seeds demo students, companies, jobs, and an officer account."

    def handle(self, *args, **options):
        # Officer
        if not Officer.objects.filter(email="officer@college.edu").exists():
            Officer.objects.create_officer(email="officer@college.edu", name="Placement Officer", password="demo1234")
            self.stdout.write(self.style.SUCCESS("Created officer: officer@college.edu / demo1234"))

        # Companies
        companies_data = [
            {"name": "Nexora Technologies", "email": "hr@nexora.com", "website": "https://nexora.com",
             "description": "Enterprise SaaS company building workflow automation tools.", "status": "approved"},
            {"name": "BrightPath Analytics", "email": "hr@brightpath.com", "website": "https://brightpath.com",
             "description": "Data analytics and BI consulting firm.", "status": "approved"},
            {"name": "Verdant Systems", "email": "hr@verdant.com", "website": "https://verdant.io",
             "description": "Cloud infrastructure and DevOps tooling startup.", "status": "approved"},
            {"name": "Quanta Robotics", "email": "hr@quanta.com", "website": "https://quantarobotics.com",
             "description": "Industrial automation and robotics hardware.", "status": "pending"},
        ]
        companies = {}
        for c in companies_data:
            company, created = Company.objects.get_or_create(
                email=c["email"],
                defaults={"name": c["name"], "website": c["website"], "description": c["description"], "status": c["status"]},
            )
            if created:
                company.set_password("demo1234")
                company.save()
                self.stdout.write(self.style.SUCCESS(f"Created company: {c['email']} / demo1234"))
            companies[c["name"]] = company

        # Demo student
        if not Student.objects.filter(email="ananya@college.edu").exists():
            student = Student(
                name="Ananya Verma", email="ananya@college.edu", phone="9876543210",
                branch="CSE", course="B.Tech", cgpa=8.4, skills=["Python", "Django", "SQL", "React"],
            )
            student.set_password("demo1234")
            student.save()
            self.stdout.write(self.style.SUCCESS("Created student: ananya@college.edu / demo1234"))

        # A couple more students so reports/department stats have something to show
        extra_students = [
            {"name": "Rohan Iyer", "email": "rohan@college.edu", "branch": "IT", "cgpa": 7.2},
            {"name": "Meera Pillai", "email": "meera@college.edu", "branch": "ECE", "cgpa": 8.9},
        ]
        for s in extra_students:
            if not Student.objects.filter(email=s["email"]).exists():
                student = Student(name=s["name"], email=s["email"], branch=s["branch"], course="B.Tech", cgpa=s["cgpa"])
                student.set_password("demo1234")
                student.save()

        # Jobs
        jobs_data = [
            {"company": "Nexora Technologies", "title": "Software Engineer Trainee", "location": "Bangalore",
             "salary": 650000, "job_type": "full_time", "min_cgpa": 7.0, "eligible_branches": ["CSE", "IT"],
             "deadline": "2026-07-15", "description": "Work on backend services for our workflow automation platform."},
            {"company": "BrightPath Analytics", "title": "Data Analyst", "location": "Pune",
             "salary": 580000, "job_type": "full_time", "min_cgpa": 6.5, "eligible_branches": ["CSE", "IT", "ECE"],
             "deadline": "2026-07-10", "description": "Analyze client datasets and build dashboards using SQL and Python."},
            {"company": "Verdant Systems", "title": "Cloud Engineer Intern", "location": "Remote",
             "salary": 35000, "job_type": "internship", "min_cgpa": 7.5, "eligible_branches": ["CSE", "IT"],
             "deadline": "2026-07-20", "description": "6-month internship on Kubernetes-based deployment tooling."},
        ]
        for j in jobs_data:
            company = companies.get(j["company"])
            if company and not Job.objects.filter(title=j["title"], company=company).exists():
                Job.objects.create(
                    company=company, title=j["title"], location=j["location"], salary=j["salary"],
                    job_type=j["job_type"], min_cgpa=j["min_cgpa"], eligible_branches=j["eligible_branches"],
                    deadline=j["deadline"], description=j["description"],
                )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
