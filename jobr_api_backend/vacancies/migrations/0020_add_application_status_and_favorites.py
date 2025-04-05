from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0033_employee_availability_date_and_more'),
        ('vacancies', '0019_function_sectors_manytomany'),
    ]

    operations = [
        migrations.AddField(
            model_name='applyvacancy',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('under_review', 'Under Review'),
                    ('accepted', 'Accepted'),
                    ('rejected', 'Rejected'),
                    ('withdrawn', 'Withdrawn')
                ],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='applyvacancy',
            name='applied_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applyvacancy',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='applyvacancy',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='FavoriteVacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_vacancies', to='accounts.employee')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='vacancies.vacancy')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('employee', 'vacancy')},
            },
        ),
        migrations.AlterModelOptions(
            name='applyvacancy',
            options={'ordering': ['-applied_at']},
        ),
    ]