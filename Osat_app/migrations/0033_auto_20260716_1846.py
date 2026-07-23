from django.db import migrations
from django.contrib.auth.hashers import make_password

def seed_default_user(apps, schema_editor):
    # Retrieve the User model active in this project setup
    User = apps.get_model('auth', 'User')

    email = "ryaenmateu22@gmail.com"

    # Check if the user exists before creating to prevent duplicate errors
    if not User.objects.filter(email=email).exists():
        User.objects.create(
            username=email,
            email=email,
            password=make_password("Password1"),  # Hashes the password securely
            is_staff=True,
            is_superuser=True
        )

def rollback_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(email="ryaenmateu22@gmail.com").delete()

class Migration(migrations.Migration):

    dependencies = [
        # This tells Django to run your database structural migrations first
        ('Osat_app', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(seed_default_user, rollback_user),
    ]