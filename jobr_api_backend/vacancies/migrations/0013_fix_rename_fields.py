from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('vacancies', '0012_auto_20250324_1509'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contracttype',
            old_name='contract_type',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='function',
            old_name='function',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='language',
            old_name='language',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='location',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='question',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='skill',
            old_name='skill',
            new_name='name',
        ),
    ]