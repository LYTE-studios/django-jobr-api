from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('vacancies', '0019_function_sectors_manytomany'),
        ('accounts', '0037_add_employee_gallery'),
    ]

    operations = [
        # Create through model
        migrations.CreateModel(
            name='EmployeeLanguage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mastery', models.CharField(
                    choices=[
                        ('beginner', 'Beginner'),
                        ('intermediate', 'Intermediate'),
                        ('advanced', 'Advanced'),
                        ('native', 'Native')
                    ],
                    default='beginner',
                    max_length=20
                )),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='accounts.employee'
                )),
                ('language', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='vacancies.language'
                )),
            ],
            options={
                'verbose_name': 'Employee Language',
                'verbose_name_plural': 'Employee Languages',
                'ordering': ['id'],
            },
        ),
        
        # Add unique constraint
        migrations.AddConstraint(
            model_name='employeelanguage',
            constraint=models.UniqueConstraint(
                fields=['employee', 'language'],
                name='unique_employee_language'
            ),
        ),
        
        # Add language field
        migrations.AddField(
            model_name='employee',
            name='language',
            field=models.ManyToManyField(
                blank=True,
                through='accounts.EmployeeLanguage',
                to='vacancies.language',
                related_name='employees'
            ),
        ),
    ]