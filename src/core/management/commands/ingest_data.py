from django.core.management.base import BaseCommand
from celery import current_app # Import celery's current_app

class Command(BaseCommand):
    help = 'Ingests customer and loan data from Excel files'

    def handle(self, *args, **options):
        customer_file_path = 'customer_data.xlsx'
        loan_file_path = 'loan_data.xlsx'
        
        current_app.send_task(
            'core.tasks.ingest_data_task', 
            args=[customer_file_path, loan_file_path]
        )
        
        self.stdout.write(self.style.SUCCESS('Data ingestion task has been queued.'))