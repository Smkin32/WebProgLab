import os

os.environ.setdefault('DJANGO_SUPERUSER_USERNAME', 'admin')
os.environ.setdefault('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
os.environ.setdefault('DJANGO_SUPERUSER_PASSWORD', 'admin123')

os.system("pip install -r requirements.txt")
os.system("python manage.py migrate")
os.system("python manage.py collectstatic --noinput")
os.system("python manage.py createsuperuser --noinput")
