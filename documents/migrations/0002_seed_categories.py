from django.db import migrations

def seed_categories(apps, schema_editor):
    Category = apps.get_model('documents', 'Category')
    categories = [
        ('Aadhar', 'Government ID - Aadhar Card'),
        ('PAN', 'Permanent Account Number'),
        ('Passport', 'Travel Document'),
        ('Education', 'Degree and Marksheets'),
        ('Medical', 'Health reports and prescriptions'),
        ('Others', 'Miscellaneous documents'),
    ]
    for name, desc in categories:
        Category.objects.get_or_create(name=name, description=desc)

class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_categories),
    ]
