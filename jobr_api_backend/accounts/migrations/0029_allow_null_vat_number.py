from django.db import migrations, models

def forwards_func(apps, schema_editor):
    Company = apps.get_model("accounts", "Company")
    # Update any existing records that have null vat_number to have an empty string
    Company.objects.filter(vat_number__isnull=True).update(vat_number='')

def reverse_func(apps, schema_editor):
    Company = apps.get_model("accounts", "Company")
    # Convert empty strings back to null (though this shouldn't be needed)
    Company.objects.filter(vat_number='').update(vat_number=None)

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0028_add_company_profile_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='vat_number',
            field=models.CharField(max_length=30, unique=True, null=True, blank=True),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]