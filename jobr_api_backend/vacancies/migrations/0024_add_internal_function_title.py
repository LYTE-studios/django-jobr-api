from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0023_add_vacancy_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='internal_function_title',
            field=models.CharField(max_length=255, null=True, blank=True, help_text='Internal title used for the function'),
        ),
    ]