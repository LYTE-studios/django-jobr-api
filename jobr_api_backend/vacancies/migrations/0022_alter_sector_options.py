# Generated by Django 5.1.3 on 2025-04-09 10:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0021_alter_functionskill_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sector',
            options={'ordering': ['weight']},
        ),
    ]
