from django.contrib.auth.models import User
from gerencia.models import Profile

# Try to get the supervisor user
try:
    supervisor = User.objects.get(username="supervisor")
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
