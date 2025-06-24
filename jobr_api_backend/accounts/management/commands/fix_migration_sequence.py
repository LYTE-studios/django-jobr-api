from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix the django_migrations table sequence'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get the current maximum ID
            cursor.execute("SELECT MAX(id) FROM django_migrations")
            max_id = cursor.fetchone()[0]
            
            if max_id is None:
                self.stdout.write('No migrations found in the table')
                return
            
            # Reset the sequence to the maximum ID
            cursor.execute("SELECT setval('django_migrations_id_seq', %s)", [max_id])
            
            self.stdout.write(f'Successfully reset sequence to {max_id}') 