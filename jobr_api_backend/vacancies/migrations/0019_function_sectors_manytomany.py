from django.db import migrations, models


def store_sector_relationships(apps, schema_editor):
    Function = apps.get_model('vacancies', 'Function')
    # Store existing relationships
    relationships = []
    for function in Function.objects.all():
        if hasattr(function, 'sector_id') and function.sector_id is not None:
            relationships.append((function.id, function.sector_id))
    return relationships


def restore_sector_relationships(apps, schema_editor, relationships):
    Function = apps.get_model('vacancies', 'Function')
    Sector = apps.get_model('vacancies', 'Sector')
    
    # Restore the relationships using the new M2M field
    for function_id, sector_id in relationships:
        try:
            function = Function.objects.get(id=function_id)
            sector = Sector.objects.get(id=sector_id)
            function.sectors.add(sector)
        except (Function.DoesNotExist, Sector.DoesNotExist):
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('vacancies', '0018_alter_vacancy_expected_mastery_and_more'),
    ]

    operations = [
        # Store existing relationships
        migrations.RunPython(
            lambda apps, schema_editor: store_sector_relationships(apps, schema_editor),
            migrations.RunPython.noop
        ),
        
        # Remove the old ForeignKey field
        migrations.RemoveField(
            model_name='function',
            name='sector',
        ),
        
        # Add the new ManyToMany field
        migrations.AddField(
            model_name='function',
            name='sectors',
            field=models.ManyToManyField(blank=True, related_name='functions', to='vacancies.sector'),
        ),
        
        # Custom operation to restore the relationships
        migrations.RunPython(
            lambda apps, schema_editor: restore_sector_relationships(
                apps, 
                schema_editor, 
                store_sector_relationships(apps, schema_editor)
            ),
            migrations.RunPython.noop
        ),
    ]