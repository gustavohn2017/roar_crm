"""
Utility functions for ROAR CRM system
"""
import os
import django
import datetime

def setup_django():
    """Set up Django environment if not already done"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roar_crm.settings')
    django.setup()

def create_or_update_profiles():
    """
    Create Profile objects for all existing users that don't have one
    Updates existing profiles if needed
    """
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
    return created_count

def ensure_supervisor_exists():
    """
    Ensure a supervisor user exists in the system
    Creates one if it doesn't exist, updates existing one if needed
    """
    from django.contrib.auth.models import User
    from gerencia.models import Profile
    
    # Try to get the supervisor user
    try:
        supervisor = User.objects.get(username='supervisor')
        print("Supervisor user already exists")
        
        # Update to supervisor role if needed
        if hasattr(supervisor, "profile"):
            if supervisor.profile.role != "supervisor":
                supervisor.profile.role = "supervisor"
                supervisor.profile.save()
                print("Profile updated to supervisor")
        else:
            profile = Profile.objects.create(user=supervisor, role="supervisor")
            print("Profile created for supervisor")
            
    except User.DoesNotExist:
        # Create the supervisor user
        supervisor = User.objects.create_user(
            username="supervisor",
            email="supervisor@example.com",
            password="senha123",
            first_name="Super",
            last_name="Visor",
            is_staff=False
        )
        
        # Set profile as supervisor
        profile = supervisor.profile
        profile.role = "supervisor"
        profile.save()
        print("Supervisor user created successfully")

    print("Username:", supervisor.username)
    print("Password: senha123")
    print("Role:", supervisor.profile.get_role_display())
    return supervisor
