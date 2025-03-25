from django.db import migrations, models

def copy_field_data(apps, schema_editor):
    ContractType = apps.get_model('vacancies', 'ContractType')
    Function = apps.get_model('vacancies', 'Function')
    Language = apps.get_model('vacancies', 'Language')
    Location = apps.get_model('vacancies', 'Location')
    Question = apps.get_model('vacancies', 'Question')
    Skill = apps.get_model('vacancies', 'Skill')

    # Copy data for each model
    for model in [ContractType, Function, Language, Location, Question, Skill]:
        for obj in model.objects.all():
            if hasattr(obj, 'contract_type'):
                obj.name = obj.contract_type
            elif hasattr(obj, 'function'):
                obj.name = obj.function
            elif hasattr(obj, 'language'):
                obj.name = obj.language
            elif hasattr(obj, 'location'):
                obj.name = obj.location
            elif hasattr(obj, 'question'):
                obj.name = obj.question
            elif hasattr(obj, 'skill'):
                obj.name = obj.skill
            obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0010_remove_skill_function_remove_skill_weight_and_more'),
    ]

    operations = [
        # Add new fields
        migrations.AddField(
            model_name='contracttype',
            name='name_new',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='function',
            name='name_new',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='name_new',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='name_new',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='name_new',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='skill',
            name='name_new',
            field=models.CharField(max_length=255, null=True),
        ),
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

        # Copy data
        migrations.RunPython(copy_field_data),

        # Remove old fields
        migrations.RemoveField(
            model_name='contracttype',
            name='contract_type',
        ),
        migrations.RemoveField(
            model_name='function',
            name='function',
        ),
        migrations.RemoveField(
            model_name='language',
            name='language',
        ),
        migrations.RemoveField(
            model_name='location',
            name='location',
        ),
        migrations.RemoveField(
            model_name='question',
            name='question',
        ),
        migrations.RemoveField(
            model_name='skill',
            name='skill',
        ),

        # Rename new fields
        migrations.RenameField(
            model_name='contracttype',
            old_name='name_new',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='function',
            old_name='name_new',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='language',
            old_name='name_new',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='name_new',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='name_new',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='skill',
            old_name='name_new',
            new_name='name',
        ),
    ]
