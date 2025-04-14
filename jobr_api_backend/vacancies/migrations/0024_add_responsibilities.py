from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0023_add_vacancy_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='responsibilities',
            field=models.JSONField(blank=True, default=list, help_text='List of responsibilities for this vacancy'),
        ),
    ]