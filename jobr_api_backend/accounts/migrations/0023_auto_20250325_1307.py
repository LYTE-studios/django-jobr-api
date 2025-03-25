from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if the table doesn't exist, we'll create it
    try:
        schema_editor.execute("""
            CREATE TABLE IF NOT EXISTS accounts_review (
                id bigserial PRIMARY KEY,
                rating integer NOT NULL,
                comment text NOT NULL,
                created_at timestamp with time zone NOT NULL,
                updated_at timestamp with time zone NOT NULL,
                reviewed_id integer NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
                reviewer_id integer NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
                UNIQUE(reviewer_id, reviewed_id)
            );
            CREATE INDEX IF NOT EXISTS accounts_review_reviewed_id ON accounts_review(reviewed_id);
            CREATE INDEX IF NOT EXISTS accounts_review_reviewer_id ON accounts_review(reviewer_id);
        """)
    except Exception as e:
        print(f"Error creating review table: {e}")

def reverse_func(apps, schema_editor):
    try:
        schema_editor.execute("DROP TABLE IF EXISTS accounts_review;")
    except Exception as e:
        print(f"Error dropping review table: {e}")

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0022_remove_customuser_admin_profile_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
