"""
Script to create Profile objects for existing users
"""
import django
import os
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roar_crm.settings')
django.setup()

from django.contrib.auth.models import User
from gerencia.models import Profile

# Get all users
users = User.objects.all()
print(f"Found {len(users)} users")

# Create profiles for users who don't have one
created_count = 0
for user in users:
    try:
        # Check if user already has a profile
        profile = user.profile
        print(f"User {user.username} already has a profile: {profile}")
    except:
        # Create profile based on user.is_staff
        if user.is_staff:
            role = 'admin'
        else:
            role = 'vendedor'  # Default role
            
        # Create profile
        profile = Profile(
            user=user,
            role=role,
            date_updated=datetime.datetime.now()
        )
        profile.save()
        created_count += 1
        print(f"Created profile for {user.username} with role: {role}")

print(f"Created {created_count} new profiles")

# Create supervisor user if it doesn't exist
try:
    supervisor = User.objects.get(username='supervisor')
    print("Supervisor user already exists")
    
    # Update to supervisor role
    supervisor.profile.role = 'supervisor'
    supervisor.profile.save()
    print("Updated supervisor role")
    
except User.DoesNotExist:
    # Create supervisor user
    supervisor = User.objects.create_user(
        username='supervisor',
        email='supervisor@example.com',
        password='senha123',
        first_name='Super',
        last_name='Visor',
        is_staff=False
    )
    
    # Get or create profile
    try:
        profile = supervisor.profile
    except:
        profile = Profile(
            user=supervisor,
            role='supervisor',
            date_updated=datetime.datetime.now()
        )
        profile.save()
        
    profile.role = 'supervisor'
    profile.save()
    print("Created supervisor user")

print("Done!")
