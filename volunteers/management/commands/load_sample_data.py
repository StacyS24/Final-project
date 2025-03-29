from django.core.management.base import BaseCommand
from volunteers.sample_data import sample_data  # Assuming your sample_data function is in sample_data.py

class Command(BaseCommand):
    help = 'Load sample data into the database'

    def handle(self, *args, **kwargs):
        sample_data()
        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data'))