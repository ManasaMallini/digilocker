import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser('admin@example.com', 'Admin@123', role='admin', is_verified=True)
    print("Admin user created: admin@example.com / Admin@123")
else:
    print("Admin user already exists.")
