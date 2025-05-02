from django.db import migrations, models
import django.db.models.deletion

def preserve_language_relationships(apps, schema_editor):
    Employee = apps.get_model('accounts', 'Employee')
    EmployeeLanguage = apps.get_model('accounts', 'EmployeeLanguage')
    
    # Store existing relationships
    for employee in Employee.objects.all():
        for language in employee.language.all():
            EmployeeLanguage.objects.create(
                employee=employee,
                language=language,
                mastery='beginner'  # Default value
            )

class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0019_function_sectors_manytomany'),
        ('accounts', '0037_add_employee_gallery'),
    ]

    operations = [
        # First create the through model
        migrations.CreateModel(
            name='EmployeeLanguage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mastery', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('native', 'Native')], default='beginner', max_length=20)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.employee')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vacancies.language')),
            ],
            options={
                'verbose_name': 'Employee Language',
                'verbose_name_plural': 'Employee Languages',
                'ordering': ['id'],
                'unique_together': {('employee', 'language')},
            },
        ),
        # Run the data migration
        migrations.RunPython(preserve_language_relationships),
        # Then update the language field to use the through model
        migrations.AlterField(
            model_name='employee',
            name='language',
            field=models.ManyToManyField(blank=True, through='accounts.EmployeeLanguage', to='vacancies.language'),
        ),
    ]