from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_allow_null_vat_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='street_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='house_number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]