from django.core.management.base import BaseCommand
from suggestions.services import SuggestionService


class Command(BaseCommand):
    help = 'Generate AI suggestions for all employees and vacancies'

    def handle(self, *args, **options):
        self.stdout.write('Starting suggestion generation...')
        
        try:
            SuggestionService.generate_suggestions()
            self.stdout.write(self.style.SUCCESS('Successfully generated suggestions'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating suggestions: {str(e)}')
            )