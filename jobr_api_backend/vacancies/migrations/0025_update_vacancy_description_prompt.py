from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0024_add_responsibilities'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vacancydescription',
            old_name='question',
            new_name='prompt',
        ),
        migrations.AlterField(
            model_name='vacancydescription',
            name='prompt',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='vacancies.joblistingprompt'),
        ),
    ]