from django.db import migrations

def update_profile_relationships(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    Employee = apps.get_model('accounts', 'Employee')
    Employer = apps.get_model('accounts', 'Employer')
    Admin = apps.get_model('accounts', 'Admin')

    # Update employee relationships
    for user in CustomUser.objects.filter(role='employee'):
        if hasattr(user, 'employee_profile') and user.employee_profile:
            user.employee_profile.user = user
            user.employee_profile.save()

    # Update employer relationships
    for user in CustomUser.objects.filter(role='employer'):
        if hasattr(user, 'employer_profile') and user.employer_profile:
            user.employer_profile.user = user
            user.employer_profile.save()

    # Update admin relationships
    for user in CustomUser.objects.filter(role='admin'):
        if hasattr(user, 'admin_profile') and user.admin_profile:
            user.admin_profile.user = user
            user.admin_profile.save()

def reverse_profile_relationships(apps, schema_editor):
    Employee = apps.get_model('accounts', 'Employee')
    Employer = apps.get_model('accounts', 'Employer')
    Admin = apps.get_model('accounts', 'Admin')

    Employee.objects.all().update(user=None)
    Employer.objects.all().update(user=None)
    Admin.objects.all().update(user=None)

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_admin_user_employee_user_employer_user'),
    ]

    operations = [
        migrations.RunPython(
            update_profile_relationships,
            reverse_profile_relationships
        ),
    ]