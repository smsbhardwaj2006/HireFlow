"""
Creates an Officer account interactively. Run after migrating:
  python manage.py create_officer

Officers aren't self-registered through the API (see models.py docstring),
so this is the equivalent of createsuperuser for this specific role.
"""

import getpass
from django.core.management.base import BaseCommand, CommandError
from officers.models import Officer


class Command(BaseCommand):
    help = "Creates a new Officer account."

    def handle(self, *args, **options):
        name = input("Full name: ").strip()
        email = input("Email: ").strip()

        if Officer.objects.filter(email__iexact=email).exists():
            raise CommandError(f"An officer with email '{email}' already exists.")

        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Password (again): ")

        if password != password_confirm:
            raise CommandError("Passwords didn't match.")
        if len(password) < 6:
            raise CommandError("Password must be at least 6 characters.")

        Officer.objects.create_officer(email=email, name=name, password=password)
        self.stdout.write(self.style.SUCCESS(f"Officer account created for {email}."))
