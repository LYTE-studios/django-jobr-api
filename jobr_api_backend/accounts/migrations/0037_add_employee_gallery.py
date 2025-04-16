from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import FileExtensionValidator
from common.utils import validate_image_size

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_add_company_coordinates'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gallery', models.ImageField(help_text='Employee gallery image (max 5MB, jpg, jpeg, png, gif)', upload_to='employee_galleries/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']), validate_image_size])),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_gallery', to='accounts.employee')),
            ],
            options={
                'verbose_name': 'Employee Gallery',
                'verbose_name_plural': 'Employee Galleries',
                'ordering': ['id'],
            },
        ),
    ]