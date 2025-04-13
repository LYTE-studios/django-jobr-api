from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0022_alter_sector_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacancyDateTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='date_times', to='vacancies.vacancy')),
            ],
            options={
                'ordering': ['date', 'start_time'],
            },
        ),
        migrations.RemoveField(
            model_name='vacancy',
            name='job_date',
        ),
    ]