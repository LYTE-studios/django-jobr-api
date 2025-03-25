from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0010_remove_skill_function_remove_skill_weight_and_more'),
    ]

    operations = [
        # Only keep Vacancy-related changes
        migrations.AddField(
            model_name='vacancy',
            name='title',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vacancy',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
