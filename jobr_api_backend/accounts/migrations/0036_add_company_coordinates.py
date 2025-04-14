from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_company_facebook_url_company_instagram_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]