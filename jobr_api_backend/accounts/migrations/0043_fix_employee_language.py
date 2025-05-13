from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration is now a no-op since we fixed the issue in 0038_add_employee_language.
    """

    dependencies = [
        ('accounts', '0042_alter_company_sector'),
        ('vacancies', '0027_experienceschool_experiencecompany'),
    ]

    operations = [
        # No operations needed since we fixed the issue in the previous migration
    ]